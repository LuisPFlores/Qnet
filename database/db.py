"""Database connection and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

import config
from database.models import Base, Source, University, Company


def get_engine():
    """Create and return the SQLAlchemy engine."""
    os.makedirs(config.DATA_DIR, exist_ok=True)
    engine = create_engine(f"sqlite:///{config.DB_PATH}", echo=False)
    return engine


def init_db(engine=None):
    """Create all tables and seed initial data if needed."""
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(engine)
    _seed_initial_data(engine)
    return engine


def get_session(engine=None) -> Session:
    """Return a new database session."""
    if engine is None:
        engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def _seed_initial_data(engine):
    """Seed default sources, universities, and companies from config."""
    session = get_session(engine)
    try:
        # ── Seed default sources ───────────────────────────────────────
        _seed_sources(session)
        # ── Seed universities from config ──────────────────────────────
        _seed_universities(session)
        # ── Seed companies from config ─────────────────────────────────
        _seed_companies(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _seed_sources(session):
    """Seed built-in source entries."""
    builtin_sources = [
        {"name": "arXiv", "source_type": "arxiv", "url": "https://arxiv.org/"},
        {
            "name": "Google Scholar",
            "source_type": "scholar",
            "url": "https://scholar.google.com/",
        },
        {
            "name": "IEEE Xplore",
            "source_type": "ieee",
            "url": "https://ieeexplore.ieee.org/",
        },
    ]
    for src_data in builtin_sources:
        exists = session.query(Source).filter_by(name=src_data["name"]).first()
        if not exists:
            session.add(Source(**src_data))

    # Add company sources
    for company in config.COMPANY_SOURCES:
        exists = session.query(Source).filter_by(name=company["name"]).first()
        if not exists:
            session.add(
                Source(
                    name=company["name"],
                    source_type="company",
                    url=company["url"],
                )
            )

    # Add university sources
    for uni in config.UNIVERSITY_SOURCES:
        exists = session.query(Source).filter_by(name=uni["name"]).first()
        if not exists:
            session.add(
                Source(
                    name=uni["name"],
                    source_type="university",
                    url=uni["url"],
                )
            )


def _seed_universities(session):
    """Seed university entries from config."""
    for uni_data in config.UNIVERSITY_SOURCES:
        exists = session.query(University).filter_by(name=uni_data["name"]).first()
        if not exists:
            session.add(
                University(
                    name=uni_data["name"],
                    country=uni_data.get("country", ""),
                    department=uni_data.get("department", ""),
                    url=uni_data.get("url", ""),
                    key_researchers=uni_data.get("key_researchers", ""),
                    focus_areas=uni_data.get("focus_areas", ""),
                )
            )


def _seed_companies(session):
    """Seed company entries from config."""
    for comp_data in config.COMPANY_SOURCES:
        exists = session.query(Company).filter_by(name=comp_data["name"]).first()
        if not exists:
            session.add(
                Company(
                    name=comp_data["name"],
                    url=comp_data.get("url", ""),
                    description=comp_data.get("description", ""),
                )
            )
