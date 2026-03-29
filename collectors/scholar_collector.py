"""Google Scholar collector for quantum networking papers."""

import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

import config
from agent.collector import BaseCollector

logger = logging.getLogger(__name__)


class ScholarCollector(BaseCollector):
    """Collects quantum networking papers from Google Scholar using scholarly."""

    SOURCE_TYPE = "scholar"

    def collect(self) -> List[Dict[str, Any]]:
        source = self.get_or_create_source(
            "Google Scholar", "https://scholar.google.com/"
        )

        results = []
        try:
            from scholarly import scholarly

            for keyword in config.QUANTUM_NETWORK_KEYWORDS[:3]:
                search_query = scholarly.search_pubs(keyword)
                count = 0
                for paper in search_query:
                    if count >= config.MAX_RESULTS_PER_SOURCE // 3:
                        break

                    bib = paper.get("bib", {})
                    title = bib.get("title", "")
                    if not title:
                        continue

                    authors = bib.get("author", "")
                    if isinstance(authors, list):
                        authors = ", ".join(authors)

                    abstract = bib.get("abstract", "")
                    url = paper.get("pub_url", "") or paper.get("eprint_url", "")
                    year = bib.get("pub_year", "")

                    pub_date = None
                    if year:
                        try:
                            pub_date = datetime(int(year), 1, 1, tzinfo=timezone.utc)
                        except (ValueError, TypeError):
                            pass

                    ext_id = f"scholar:{hashlib.md5(title.encode()).hexdigest()}"

                    results.append(
                        {
                            "title": title,
                            "authors": authors,
                            "abstract": abstract,
                            "url": url,
                            "published_date": pub_date,
                            "content_type": "paper",
                            "external_id": ext_id,
                            "source_name": "Google Scholar",
                            "raw_content": abstract,
                        }
                    )
                    count += 1

        except ImportError:
            logger.warning("scholarly library not installed, skipping Google Scholar")
        except Exception as e:
            logger.error(f"Google Scholar collection error: {e}")

        self.mark_source_fetched(source)
        return results
