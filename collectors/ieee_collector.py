"""IEEE Xplore collector for quantum networking papers and conference proceedings."""

import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

import requests

import config
from agent.collector import BaseCollector

logger = logging.getLogger(__name__)

IEEE_API_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"


class IEEECollector(BaseCollector):
    """Collects quantum networking papers from IEEE Xplore API."""

    SOURCE_TYPE = "ieee"

    def collect(self) -> List[Dict[str, Any]]:
        source = self.get_or_create_source(
            "IEEE Xplore", "https://ieeexplore.ieee.org/"
        )

        results = []

        if not config.IEEE_API_KEY:
            logger.info(
                "IEEE API key not configured -- using fallback web search approach"
            )
            results = self._collect_fallback()
        else:
            results = self._collect_api()

        self.mark_source_fetched(source)
        return results

    def _collect_api(self) -> List[Dict[str, Any]]:
        """Collect using the official IEEE Xplore API."""
        results = []
        for keyword in ["quantum network", "quantum key distribution", "quantum internet"]:
            try:
                params = {
                    "apikey": config.IEEE_API_KEY,
                    "querytext": keyword,
                    "max_records": min(config.MAX_RESULTS_PER_SOURCE // 3, 200),
                    "sort_field": "article_title",
                    "sort_order": "asc",
                }
                logger.info(f"IEEE API request for '{keyword}': {IEEE_API_URL}")
                resp = requests.get(
                    IEEE_API_URL, params=params, timeout=config.REQUEST_TIMEOUT
                )

                # Log the HTTP status for debugging
                logger.info(f"IEEE API response status: {resp.status_code}")

                if resp.status_code == 403:
                    logger.error("IEEE API returned 403 Forbidden -- check your API key")
                    continue
                if resp.status_code == 429:
                    logger.error("IEEE API returned 429 Too Many Requests -- rate limited")
                    continue

                resp.raise_for_status()
                data = resp.json()

                total_found = data.get("total_records", 0)
                logger.info(f"IEEE API found {total_found} results for '{keyword}'")

                for article in data.get("articles", []):
                    title = article.get("title", "")
                    if not title:
                        continue

                    # Authors can be a list of dicts with 'full_name',
                    # or nested under an 'authors' key
                    authors_raw = article.get("authors", {})
                    if isinstance(authors_raw, dict):
                        authors_list = authors_raw.get("authors", [])
                    elif isinstance(authors_raw, list):
                        authors_list = authors_raw
                    else:
                        authors_list = []
                    authors = ", ".join(
                        [a.get("full_name", "") for a in authors_list if isinstance(a, dict)]
                    )

                    abstract = article.get("abstract", "")
                    url = article.get("html_url", "") or article.get("pdf_url", "")
                    if not url:
                        # Build URL from article_number if available
                        art_num = article.get("article_number", "")
                        if art_num:
                            url = f"https://ieeexplore.ieee.org/document/{art_num}"
                    doi = article.get("doi", "")

                    # publication_date format varies; try multiple patterns
                    pub_date = None
                    pub_date_str = article.get("publication_date", "")
                    pub_year = article.get("publication_year", "")
                    if pub_date_str:
                        for fmt in [
                            "%d %b. %Y",    # "15 Jan. 2024"
                            "%d %B %Y",     # "15 January 2024"
                            "%b. %Y",       # "Jan. 2024"
                            "%B %Y",        # "January 2024"
                            "%Y",           # "2024"
                        ]:
                            try:
                                pub_date = datetime.strptime(
                                    pub_date_str.strip(), fmt
                                ).replace(tzinfo=timezone.utc)
                                break
                            except ValueError:
                                continue
                    if not pub_date and pub_year:
                        try:
                            pub_date = datetime.strptime(
                                str(pub_year).strip(), "%Y"
                            ).replace(tzinfo=timezone.utc)
                        except ValueError:
                            pass

                    ext_id = f"ieee:{doi}" if doi else f"ieee:{hashlib.md5(title.encode()).hexdigest()}"

                    content_type = "paper"
                    ct = article.get("content_type", "").lower()
                    if "conference" in ct or "conferences" in ct:
                        content_type = "conference"

                    results.append(
                        {
                            "title": title,
                            "authors": authors,
                            "abstract": abstract,
                            "url": url,
                            "published_date": pub_date,
                            "content_type": content_type,
                            "external_id": ext_id,
                            "source_name": "IEEE Xplore",
                            "raw_content": abstract,
                        }
                    )

                logger.info(f"IEEE API parsed {len(results)} articles so far")

            except requests.exceptions.Timeout:
                logger.error(f"IEEE API timeout for keyword '{keyword}'")
            except requests.exceptions.ConnectionError as e:
                logger.error(f"IEEE API connection error for '{keyword}': {e}")
            except Exception as e:
                logger.error(f"IEEE API error for keyword '{keyword}': {e}", exc_info=True)

        logger.info(f"IEEE API collection complete: {len(results)} total articles")
        return results

    def _collect_fallback(self) -> List[Dict[str, Any]]:
        """Fallback: scrape IEEE Xplore search results when no API key is available."""
        from bs4 import BeautifulSoup

        results = []
        search_url = "https://ieeexplore.ieee.org/search/searchresult.jsp"

        for keyword in ["quantum network", "quantum key distribution"]:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                params = {"queryText": keyword, "sortType": "newest"}
                resp = requests.get(
                    search_url,
                    params=params,
                    headers=headers,
                    timeout=config.REQUEST_TIMEOUT,
                )

                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml")
                    # IEEE renders content via JS, so basic scraping yields limited results.
                    # We extract what we can from the initial HTML payload.
                    for item in soup.select(".result-item, .List-results-items"):
                        title_el = item.select_one("h2 a, .title a")
                        if not title_el:
                            continue
                        title = title_el.get_text(strip=True)
                        link = title_el.get("href", "")
                        if link and not link.startswith("http"):
                            link = f"https://ieeexplore.ieee.org{link}"

                        ext_id = f"ieee:{hashlib.md5(title.encode()).hexdigest()}"

                        results.append(
                            {
                                "title": title,
                                "authors": "",
                                "abstract": "",
                                "url": link,
                                "published_date": None,
                                "content_type": "paper",
                                "external_id": ext_id,
                                "source_name": "IEEE Xplore",
                                "raw_content": "",
                            }
                        )
            except Exception as e:
                logger.error(f"IEEE fallback scrape error: {e}")

        return results
