"""SQLAlchemy ORM models for the QNet Agent database."""

import re
import unicodedata
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Table,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ── Many-to-many: articles <-> topics ──────────────────────────────────
article_topics = Table(
    "article_topics",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id"), primary_key=True),
)


def _utcnow():
    return datetime.now(timezone.utc)


# ── Sources ────────────────────────────────────────────────────────────
class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    source_type = Column(
        String(50), nullable=False
    )  # arxiv, scholar, ieee, company, university
    url = Column(Text, default="")
    last_fetched = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)

    articles = relationship("Article", back_populates="source")

    def __repr__(self):
        return f"<Source {self.name} ({self.source_type})>"


# ── Articles ───────────────────────────────────────────────────────────
class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    title = Column(String(500), nullable=False)
    authors = Column(Text, default="")
    abstract = Column(Text, default="")
    summary = Column(Text, default="")  # AI-generated summary
    url = Column(Text, default="")
    published_date = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=_utcnow)
    content_type = Column(
        String(50), default="paper"
    )  # paper, news, product, blog, conference
    raw_content = Column(Text, default="")  # full scraped text if available
    external_id = Column(
        String(255), nullable=True, unique=True
    )  # dedup key (arxiv id, doi, url hash)
    normalized_title = Column(
        String(500), nullable=True, index=True
    )  # cross-source dedup key

    source = relationship("Source", back_populates="articles")
    topics = relationship("Topic", secondary=article_topics, back_populates="articles")

    @staticmethod
    def normalize_title(title: str) -> str:
        """Return a canonical form of a title for cross-source deduplication."""
        text = unicodedata.normalize("NFKD", title)
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)   # drop punctuation
        text = re.sub(r"\s+", " ", text)       # collapse whitespace
        return text

    def __repr__(self):
        return f"<Article {self.title[:60]}>"


# ── Topics ─────────────────────────────────────────────────────────────
class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, default="")
    relevance_score = Column(Float, default=0.0)
    first_seen = Column(DateTime, default=_utcnow)
    last_seen = Column(DateTime, default=_utcnow)

    articles = relationship(
        "Article", secondary=article_topics, back_populates="topics"
    )

    def __repr__(self):
        return f"<Topic {self.name} (score={self.relevance_score:.2f})>"


# ── Universities ───────────────────────────────────────────────────────
class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100), default="")
    department = Column(String(255), default="")
    research_group = Column(String(255), default="")
    url = Column(Text, default="")
    key_researchers = Column(Text, default="")
    focus_areas = Column(Text, default="")
    last_updated = Column(DateTime, default=_utcnow)

    def __repr__(self):
        return f"<University {self.name}>"


# ── Companies ──────────────────────────────────────────────────────────
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, default="")
    products = Column(Text, default="")
    description = Column(Text, default="")
    last_updated = Column(DateTime, default=_utcnow)

    def __repr__(self):
        return f"<Company {self.name}>"


# ── Hot Topics Snapshots ───────────────────────────────────────────────
class HotTopicSnapshot(Base):
    __tablename__ = "hot_topic_snapshots"

    id = Column(Integer, primary_key=True)
    generated_at = Column(DateTime, default=_utcnow)
    topics_json = Column(Text, default="[]")  # JSON list of ranked topics
    analysis_text = Column(Text, default="")  # AI-generated narrative summary

    def __repr__(self):
        return f"<HotTopicSnapshot {self.generated_at}>"


# ── Simulators ─────────────────────────────────────────────────────────
class Simulator(Base):
    __tablename__ = "simulators"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, default="")
    github_url = Column(Text, default="")
    docs_url = Column(Text, default="")
    language = Column(String(255), default="")  # e.g. "Python", "C++/OMNeT++"
    dependencies = Column(Text, default="")
    install_command = Column(Text, default="")  # e.g. "pip install qunetsim"
    license = Column(String(100), default="")
    example_code = Column(Text, default="")  # working code snippet
    scenarios = Column(Text, default="")  # comma-separated use cases
    status = Column(String(50), default="active")  # active, stalled, dead
    github_stars = Column(Integer, default=0)
    github_last_commit = Column(String(50), default="")  # ISO date string
    github_open_issues = Column(Integer, default=0)
    github_latest_release = Column(String(100), default="")
    paper_reference = Column(Text, default="")  # academic citation
    last_updated = Column(DateTime, default=_utcnow)

    def __repr__(self):
        return f"<Simulator {self.name}>"
