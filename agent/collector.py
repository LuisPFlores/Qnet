"""Base collector abstract class for all source collectors."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from database.models import Source

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Abstract base class for all content collectors."""

    SOURCE_TYPE: str = ""  # Override in subclass

    def __init__(self, session: Session):
        self.session = session

    def get_or_create_source(self, name: str, url: str = "") -> Source:
        """Get existing source or create a new one."""
        source = (
            self.session.query(Source)
            .filter_by(name=name, source_type=self.SOURCE_TYPE)
            .first()
        )
        if not source:
            source = Source(name=name, source_type=self.SOURCE_TYPE, url=url)
            self.session.add(source)
            self.session.flush()
        return source

    def mark_source_fetched(self, source: Source):
        """Update the last_fetched timestamp on a source."""
        source.last_fetched = datetime.now(timezone.utc)
        self.session.flush()

    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        """
        Fetch new content from the source.

        Returns a list of dicts with keys:
            - title: str
            - authors: str
            - abstract: str
            - url: str
            - published_date: datetime | None
            - content_type: str (paper, news, product, blog, conference)
            - external_id: str (unique identifier for deduplication)
            - source_name: str
            - raw_content: str (optional, full text if available)
        """
        ...

    def collect_safe(self) -> List[Dict[str, Any]]:
        """Wrapper that catches exceptions and logs them."""
        try:
            results = self.collect()
            logger.info(
                f"[{self.SOURCE_TYPE}] Collected {len(results)} items"
            )
            return results
        except Exception as e:
            logger.error(f"[{self.SOURCE_TYPE}] Collection failed: {e}")
            return []
