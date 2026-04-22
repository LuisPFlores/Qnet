"""Core agent orchestrator – coordinates collectors, analyzer, and topic engine."""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from database.models import Article, Source
from agent.analyzer import Analyzer
from agent.topic_engine import TopicEngine
from collectors.arxiv_collector import ArxivCollector
from collectors.scholar_collector import ScholarCollector
from collectors.ieee_collector import IEEECollector
from collectors.company_collector import CompanyCollector
from collectors.university_collector import UniversityCollector
from collectors.github_collector import GitHubCollector

logger = logging.getLogger(__name__)


class QNetAgent:
    """Main orchestrator for the Quantum Network Intelligence Agent."""

    def __init__(self, session: Session):
        self.session = session
        self.analyzer = Analyzer()
        self.topic_engine = TopicEngine(session)
        self.collectors = [
            ArxivCollector(session),
            ScholarCollector(session),
            IEEECollector(session),
            CompanyCollector(session),
            UniversityCollector(session),
            GitHubCollector(session),
        ]

    def collect_all(self) -> Dict[str, Any]:
        """
        Run all collectors, deduplicate, store in DB, analyze, and update topics.
        This is the "give me the last content" handler.
        """
        logger.info("Starting full collection across all sources...")
        all_items = []
        source_counts = {}

        for collector in self.collectors:
            items = collector.collect_safe()
            source_counts[collector.SOURCE_TYPE] = len(items)
            all_items.extend(items)

        # Cross-source dedup: keep the first occurrence per normalized title
        # (collector order defines priority: arXiv > Scholar > IEEE > Company > Uni > GitHub)
        seen_titles: dict[str, str] = {}  # normalized_title -> source_name
        unique_items: list[Dict[str, Any]] = []
        for item in all_items:
            norm = Article.normalize_title(item.get("title", ""))
            if not norm:
                continue
            if norm in seen_titles:
                logger.info(
                    "Cross-source duplicate skipped: '%s' from %s "
                    "(already collected from %s)",
                    item.get("title", "")[:80],
                    item.get("source_name", "?"),
                    seen_titles[norm],
                )
                continue
            seen_titles[norm] = item.get("source_name", "")
            unique_items.append(item)

        logger.info(
            "Cross-source dedup: %d items → %d unique",
            len(all_items),
            len(unique_items),
        )

        # Deduplicate and store
        new_articles = self._store_articles(unique_items)
        logger.info(
            f"Collected {len(all_items)} total items, {len(new_articles)} new articles stored"
        )

        # Analyze new articles with OpenAI
        self._analyze_articles(new_articles)

        # Update hot topics
        hot_topics = self.topic_engine.get_hot_topics()

        # Categorize new articles by type for the summary
        new_papers = [
            self._article_to_dict(a)
            for a in new_articles
            if a.content_type in ("paper", "conference")
        ]
        new_company_news = [
            self._article_to_dict(a)
            for a in new_articles
            if a.content_type in ("news", "product")
        ]
        new_university_news = [
            self._article_to_dict(a)
            for a in new_articles
            if a.source and a.source.source_type == "university"
        ]
        new_simulators = [
            self._article_to_dict(a)
            for a in new_articles
            if a.content_type == "software"
        ]

        # Generate comprehensive summary
        summary = self.analyzer.generate_latest_summary(
            new_papers, new_company_news, new_university_news, hot_topics
        )

        # Generate hot topics analysis
        recent_titles = [a.title for a in new_articles[:30]]
        analysis = self.analyzer.generate_hot_topics_analysis(hot_topics, recent_titles)

        # Save snapshot
        self.topic_engine.save_snapshot(hot_topics, analysis)
        self.session.commit()

        return {
            "total_collected": len(all_items),
            "new_articles": len(new_articles),
            "source_counts": source_counts,
            "papers": new_papers,
            "company_news": new_company_news,
            "university_news": new_university_news,
            "simulators": new_simulators,
            "hot_topics": hot_topics,
            "summary": summary,
            "analysis": analysis,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _store_articles(self, items: List[Dict[str, Any]]) -> List[Article]:
        """Store collected items in the database, skipping duplicates."""
        new_articles = []

        for item in items:
            ext_id = item.get("external_id", "")
            if not ext_id:
                continue

            # Check for same-source duplicate (external_id)
            existing = (
                self.session.query(Article).filter_by(external_id=ext_id).first()
            )
            if existing:
                continue

            # Check for cross-source duplicate (normalized title already in DB)
            norm_title = Article.normalize_title(item.get("title", ""))
            if norm_title:
                title_dup = (
                    self.session.query(Article)
                    .filter_by(normalized_title=norm_title)
                    .first()
                )
                if title_dup:
                    logger.info(
                        "DB cross-source duplicate skipped: '%s' from %s "
                        "(matches existing article id=%d from %s)",
                        item.get("title", "")[:80],
                        item.get("source_name", "?"),
                        title_dup.id,
                        title_dup.source.name if title_dup.source else "unknown",
                    )
                    continue

            # Find or create source
            source_name = item.get("source_name", "")
            source = self.session.query(Source).filter_by(name=source_name).first()

            article = Article(
                source_id=source.id if source else None,
                title=item.get("title", ""),
                authors=item.get("authors", ""),
                abstract=item.get("abstract", ""),
                url=item.get("url", ""),
                published_date=item.get("published_date"),
                content_type=item.get("content_type", "paper"),
                external_id=ext_id,
                normalized_title=norm_title,
                raw_content=item.get("raw_content", ""),
                fetched_at=datetime.now(timezone.utc),
            )
            self.session.add(article)
            self.session.flush()
            new_articles.append(article)

        return new_articles

    def _analyze_articles(self, articles: List[Article]):
        """Run AI analysis on articles: summarize and extract topics."""
        for article in articles:
            # Generate summary
            if article.abstract or article.raw_content:
                content = article.abstract or article.raw_content
                article.summary = self.analyzer.summarize_article(
                    article.title, content
                )

                # Extract and link topics
                topics = self.analyzer.extract_topics(article.title, content)
                for topic_name in topics:
                    self.topic_engine.update_topic(topic_name, article)

        self.session.flush()

    def get_all_articles(
        self,
        source_type: Optional[str] = None,
        content_type: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get articles with optional filtering."""
        query = self.session.query(Article)

        if source_type:
            query = query.join(Source).filter(Source.source_type == source_type)
        if content_type:
            query = query.filter(Article.content_type == content_type)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Article.title.ilike(search_term))
                | (Article.abstract.ilike(search_term))
                | (Article.authors.ilike(search_term))
            )

        query = query.order_by(Article.fetched_at.desc())
        articles = query.offset(offset).limit(limit).all()

        return [self._article_to_dict(a) for a in articles]

    def get_article_count(self) -> Dict[str, int]:
        """Get counts of articles by source type."""
        counts = {}
        sources = self.session.query(Source).all()
        for source in sources:
            stype = source.source_type
            if stype not in counts:
                counts[stype] = 0
            counts[stype] += len(source.articles)
        counts["total"] = sum(counts.values())
        return counts

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the dashboard."""
        article_counts = self.get_article_count()
        hot_topics = self.topic_engine.get_hot_topics(limit=10)
        latest_snapshot = self.topic_engine.get_latest_snapshot()
        trends = self.topic_engine.get_topic_trends()

        recent_articles = (
            self.session.query(Article)
            .order_by(Article.fetched_at.desc())
            .limit(10)
            .all()
        )

        return {
            "article_counts": article_counts,
            "hot_topics": hot_topics,
            "latest_snapshot": latest_snapshot,
            "trends": trends[:10],
            "recent_articles": [self._article_to_dict(a) for a in recent_articles],
        }

    @staticmethod
    def _article_to_dict(article: Article) -> Dict[str, Any]:
        """Convert an Article ORM object to a dictionary."""
        return {
            "id": article.id,
            "title": article.title,
            "authors": article.authors,
            "abstract": article.abstract,
            "summary": article.summary,
            "url": article.url,
            "published_date": (
                article.published_date.isoformat() if article.published_date else ""
            ),
            "fetched_at": (
                article.fetched_at.isoformat() if article.fetched_at else ""
            ),
            "content_type": article.content_type,
            "source": article.source.name if article.source else "",
            "source_type": article.source.source_type if article.source else "",
            "topics": [t.name for t in article.topics],
        }
