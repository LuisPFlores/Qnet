"""Topic engine for hot topic detection and trend scoring."""

import json
import logging
from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Article, Topic, HotTopicSnapshot, article_topics

logger = logging.getLogger(__name__)

# Weights for topic scoring
RECENCY_WEIGHT = 0.4  # How recent the topic mentions are
FREQUENCY_WEIGHT = 0.35  # How often the topic appears
CROSS_SOURCE_WEIGHT = 0.25  # How many different sources mention it


class TopicEngine:
    """Detects hot topics and scores trends from collected articles."""

    def __init__(self, session: Session):
        self.session = session

    def get_hot_topics(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Calculate and return the current hot topics ranked by score.

        Scoring formula:
        score = (RECENCY_WEIGHT * recency_score) +
                (FREQUENCY_WEIGHT * frequency_score) +
                (CROSS_SOURCE_WEIGHT * cross_source_score)
        """
        topics = self.session.query(Topic).all()
        if not topics:
            return []

        topic_scores = []
        now = datetime.now(timezone.utc)

        # Get global stats for normalization
        max_count = max(len(t.articles) for t in topics) if topics else 1
        max_count = max(max_count, 1)

        for topic in topics:
            if not topic.articles:
                continue

            # ── Frequency score (normalized) ───────────────────────────
            count = len(topic.articles)
            frequency_score = count / max_count

            # ── Recency score (based on most recent article) ───────────
            most_recent = max(
                (a.published_date or a.fetched_at for a in topic.articles),
                default=now,
            )
            if most_recent.tzinfo is None:
                most_recent = most_recent.replace(tzinfo=timezone.utc)
            days_ago = (now - most_recent).days
            recency_score = max(0, 1.0 - (days_ago / 365))  # Decay over 1 year

            # ── Cross-source score ─────────────────────────────────────
            source_types = set()
            for article in topic.articles:
                if article.source:
                    source_types.add(article.source.source_type)
            # Normalize: 5 source types possible
            cross_source_score = len(source_types) / 5.0

            # ── Combined score ─────────────────────────────────────────
            score = (
                RECENCY_WEIGHT * recency_score
                + FREQUENCY_WEIGHT * frequency_score
                + CROSS_SOURCE_WEIGHT * cross_source_score
            )

            topic_scores.append(
                {
                    "id": topic.id,
                    "name": topic.name,
                    "description": topic.description,
                    "count": count,
                    "score": round(score, 4),
                    "recency_score": round(recency_score, 4),
                    "frequency_score": round(frequency_score, 4),
                    "cross_source_score": round(cross_source_score, 4),
                    "source_types": list(source_types),
                    "last_seen": topic.last_seen.isoformat() if topic.last_seen else "",
                }
            )

        # Sort by score descending
        topic_scores.sort(key=lambda x: x["score"], reverse=True)
        return topic_scores[:limit]

    def update_topic(self, topic_name: str, article_obj: "Article"):
        """Add or update a topic and link it to an article."""
        topic_name = topic_name.strip().lower()
        if len(topic_name) < 3:
            return

        topic = self.session.query(Topic).filter_by(name=topic_name).first()
        if not topic:
            topic = Topic(
                name=topic_name,
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
            )
            self.session.add(topic)
            self.session.flush()
        else:
            topic.last_seen = datetime.now(timezone.utc)

        # Link article to topic if not already linked
        if article_obj not in topic.articles:
            topic.articles.append(article_obj)

        # Update relevance score based on current count
        topic.relevance_score = float(len(topic.articles))

    def save_snapshot(self, hot_topics: List[Dict], analysis_text: str = ""):
        """Save a hot topics snapshot to the database."""
        snapshot = HotTopicSnapshot(
            generated_at=datetime.now(timezone.utc),
            topics_json=json.dumps(hot_topics),
            analysis_text=analysis_text,
        )
        self.session.add(snapshot)
        self.session.flush()
        return snapshot

    def get_latest_snapshot(self) -> Dict[str, Any]:
        """Get the most recent hot topics snapshot."""
        snapshot = (
            self.session.query(HotTopicSnapshot)
            .order_by(HotTopicSnapshot.generated_at.desc())
            .first()
        )
        if not snapshot:
            return {"topics": [], "analysis": "", "generated_at": None}

        return {
            "topics": json.loads(snapshot.topics_json),
            "analysis": snapshot.analysis_text,
            "generated_at": snapshot.generated_at,
        }

    def get_topic_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get topics that are trending (increasing in mentions) over a time period."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        midpoint = datetime.now(timezone.utc) - timedelta(days=days // 2)

        topics = self.session.query(Topic).all()
        trends = []

        for topic in topics:
            if not topic.articles:
                continue

            # Count mentions in first half vs second half of the period
            early_count = sum(
                1
                for a in topic.articles
                if a.fetched_at
                and a.fetched_at >= cutoff
                and a.fetched_at < midpoint
            )
            recent_count = sum(
                1
                for a in topic.articles
                if a.fetched_at and a.fetched_at >= midpoint
            )

            if early_count == 0 and recent_count > 0:
                trend = "new"
                trend_score = recent_count
            elif early_count > 0:
                trend_score = (recent_count - early_count) / early_count
                if trend_score > 0.2:
                    trend = "rising"
                elif trend_score < -0.2:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                continue

            trends.append(
                {
                    "name": topic.name,
                    "trend": trend,
                    "trend_score": round(trend_score, 2),
                    "early_count": early_count,
                    "recent_count": recent_count,
                    "total": len(topic.articles),
                }
            )

        trends.sort(key=lambda x: x["trend_score"], reverse=True)
        return trends
