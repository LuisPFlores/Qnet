"""Company website collector for quantum networking technology providers."""

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


class CompanyCollector(BaseCollector):
    """Scrapes news/blog pages from quantum networking companies."""

    SOURCE_TYPE = "company"

    def collect(self) -> List[Dict[str, Any]]:
        all_results = []

        for company in config.COMPANY_SOURCES:
            source = self.get_or_create_source(company["name"], company["url"])
            try:
                items = self._scrape_company(company)
                all_results.extend(items)
                self.mark_source_fetched(source)
            except Exception as e:
                logger.error(f"Error scraping {company['name']}: {e}")

        return all_results

    def _scrape_company(self, company: dict) -> List[Dict[str, Any]]:
        """Scrape a single company's news/blog page."""
        url = company["url"]
        results = []

        try:
            resp = requests.get(url, headers=HEADERS, timeout=config.REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return results

        soup = BeautifulSoup(resp.text, "lxml")

        # Generic selectors that work for many blog/news pages
        article_selectors = [
            "article",
            ".post",
            ".blog-post",
            ".news-item",
            ".entry",
            ".card",
            '[class*="post"]',
            '[class*="news"]',
            '[class*="article"]',
            '[class*="blog"]',
        ]

        articles_found = []
        for selector in article_selectors:
            articles_found = soup.select(selector)
            if articles_found:
                break

        if not articles_found:
            # Fallback: look for any links with substantial text
            articles_found = soup.select("a[href]")

        count = 0
        for article_el in articles_found:
            if count >= config.MAX_RESULTS_PER_SOURCE:
                break

            # Extract title
            title_el = article_el.select_one("h1, h2, h3, h4, .title, .entry-title")
            if title_el:
                title = title_el.get_text(strip=True)
            elif article_el.name == "a":
                title = article_el.get_text(strip=True)
            else:
                title = ""

            if not title or len(title) < 10:
                continue

            # Extract link
            link_el = article_el.select_one("a[href]") or (
                article_el if article_el.name == "a" else None
            )
            link = ""
            if link_el and link_el.get("href"):
                link = urljoin(url, link_el["href"])

            # Extract description/summary
            desc_el = article_el.select_one(
                "p, .excerpt, .summary, .description, [class*='excerpt']"
            )
            description = desc_el.get_text(strip=True) if desc_el else ""

            # Extract date if available
            date_el = article_el.select_one(
                "time, .date, .published, [class*='date'], [datetime]"
            )
            pub_date = None
            if date_el:
                date_str = date_el.get("datetime", "") or date_el.get_text(strip=True)
                pub_date = self._parse_date(date_str)

            ext_id = f"company:{company['name']}:{hashlib.md5(title.encode()).hexdigest()}"

            results.append(
                {
                    "title": title,
                    "authors": company["name"],
                    "abstract": description,
                    "url": link,
                    "published_date": pub_date,
                    "content_type": "news",
                    "external_id": ext_id,
                    "source_name": company["name"],
                    "raw_content": description,
                }
            )
            count += 1

        return results

    @staticmethod
    def _parse_date(date_str: str):
        """Try multiple date formats to parse a date string."""
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
            "%m/%d/%Y",
            "%d/%m/%Y",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        return None
