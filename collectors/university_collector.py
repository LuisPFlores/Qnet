"""University research page collector for quantum networking groups."""

import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import config
from agent.collector import BaseCollector

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


class UniversityCollector(BaseCollector):
    """Scrapes research pages from university quantum networking groups."""

    SOURCE_TYPE = "university"

    def collect(self) -> List[Dict[str, Any]]:
        all_results = []

        for uni in config.UNIVERSITY_SOURCES:
            source = self.get_or_create_source(uni["name"], uni["url"])
            try:
                items = self._scrape_university(uni)
                all_results.extend(items)
                self.mark_source_fetched(source)
            except Exception as e:
                logger.error(f"Error scraping {uni['name']}: {e}")

        return all_results

    def _scrape_university(self, uni: dict) -> List[Dict[str, Any]]:
        """Scrape a single university research group page."""
        url = uni["url"]
        results = []

        try:
            resp = requests.get(url, headers=HEADERS, timeout=config.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return results

        soup = BeautifulSoup(resp.text, "lxml")

        # Look for publication / news / research items
        item_selectors = [
            "article",
            ".publication",
            ".paper",
            ".news-item",
            ".post",
            ".entry",
            ".research-item",
            ".list-item",
            '[class*="publication"]',
            '[class*="paper"]',
            '[class*="research"]',
            '[class*="news"]',
            "li",
        ]

        items_found = []
        for selector in item_selectors:
            items_found = soup.select(selector)
            if len(items_found) >= 3:
                break

        count = 0
        seen_titles = set()

        for item_el in items_found:
            if count >= config.MAX_RESULTS_PER_SOURCE:
                break

            # Extract title from headings or links
            title = ""
            title_el = item_el.select_one("h1, h2, h3, h4, a")
            if title_el:
                title = title_el.get_text(strip=True)

            if not title or len(title) < 15 or title in seen_titles:
                continue

            # Filter for quantum-related content
            full_text = item_el.get_text(strip=True).lower()
            is_relevant = any(
                kw.lower() in full_text for kw in config.QUANTUM_NETWORK_KEYWORDS
            )
            if not is_relevant and len(items_found) > 10:
                # Only filter if there are many items; small pages may all be relevant
                continue

            seen_titles.add(title)

            # Extract link
            link_el = item_el.select_one("a[href]")
            link = ""
            if link_el and link_el.get("href"):
                link = urljoin(url, link_el["href"])

            # Extract description
            desc_el = item_el.select_one("p, .abstract, .description, .summary")
            description = desc_el.get_text(strip=True) if desc_el else ""

            # Extract date
            date_el = item_el.select_one(
                "time, .date, .year, [class*='date'], [datetime]"
            )
            pub_date = None
            if date_el:
                date_str = date_el.get("datetime", "") or date_el.get_text(strip=True)
                pub_date = self._parse_date(date_str)

            ext_id = f"uni:{uni['name']}:{hashlib.md5(title.encode()).hexdigest()}"

            results.append(
                {
                    "title": title,
                    "authors": uni.get("key_researchers", ""),
                    "abstract": description,
                    "url": link,
                    "published_date": pub_date,
                    "content_type": "paper",
                    "external_id": ext_id,
                    "source_name": uni["name"],
                    "raw_content": description,
                }
            )
            count += 1

        return results

    @staticmethod
    def _parse_date(date_str: str):
        """Try multiple date formats."""
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
            "%Y",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        return None
