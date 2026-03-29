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

    def collect(self) -> List[Dict[str, Any]]:
        source = self.get_or_create_source("arXiv", "https://arxiv.org/")

        client = arxiv.Client()
        search = arxiv.Search(
            query=config.ARXIV_QUERY,
            max_results=config.ARXIV_MAX_RESULTS,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        results = []
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

        self.mark_source_fetched(source)
        return results
