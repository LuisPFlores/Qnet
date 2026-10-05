"""arXiv collector for quantum networking papers."""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

import arxiv

import config
from agent.collector import BaseCollector

logger = logging.getLogger(__name__)


class ArxivCollector(BaseCollector):
    """Collects quantum networking papers from arXiv."""

    SOURCE_TYPE = "arxiv"

    def __init__(self, session, query=None, max_results=None):
        super().__init__(session)
        self.query = query or config.ARXIV_QUERY
        self.max_results = max_results or config.ARXIV_MAX_RESULTS

    def collect(self) -> List[Dict[str, Any]]:
        source = self.get_or_create_source("arXiv", "https://arxiv.org/")

        # Use conservative settings to avoid arXiv 503 rate-limiting:
        # - page_size=10 keeps individual requests small
        # - delay_seconds=5 respects arXiv's rate-limit guidance
        # - num_retries=5 handles transient 503s
        client = arxiv.Client(
            page_size=10,
            delay_seconds=5.0,
            num_retries=5,
        )
        search = arxiv.Search(
            query=self.query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        results = []
        try:
            for paper in client.results(search):
                authors = ", ".join([a.name for a in paper.authors])
                pub_date = paper.published
                if pub_date and pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)

                results.append(
                    {
                        "title": paper.title,
                        "authors": authors,
                        "abstract": paper.summary,
                        "url": paper.entry_id,
                        "published_date": pub_date,
                        "content_type": "paper",
                        "external_id": f"arxiv:{paper.entry_id}",
                        "source_name": "arXiv",
                        "raw_content": paper.summary,
                    }
                )
        except (arxiv.HTTPError, arxiv.ArxivError) as e:
            logger.warning(
                "arXiv API error: %s. Returning %d papers collected so far.",
                e,
                len(results),
            )

        self.mark_source_fetched(source)
        return results
