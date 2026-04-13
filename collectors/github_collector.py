"""GitHub collector for quantum network simulator repositories.

Fetches live metadata (stars, last commit, open issues, latest release)
from the GitHub REST API for each simulator that has a github_url configured.
Also creates Article entries so simulator updates appear in collection results.
"""

import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

import requests

import config
from agent.collector import BaseCollector
from database.models import Simulator

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


def _parse_github_owner_repo(url: str) -> Optional[Tuple[str, str]]:
    """Extract (owner, repo) from a GitHub URL."""
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if match:
        return match.group(1), match.group(2)
    return None


class GitHubCollector(BaseCollector):
    """Collects live GitHub metadata for quantum network simulators."""

    SOURCE_TYPE = "github"

    def collect(self) -> List[Dict[str, Any]]:
        source = self.get_or_create_source(
            "GitHub Simulators", "https://github.com/"
        )

        results = []
        simulators = self.session.query(Simulator).all()

        for sim in simulators:
            if not sim.github_url:
                continue

            parsed = _parse_github_owner_repo(sim.github_url)
            if not parsed:
                logger.warning(f"Cannot parse GitHub URL for {sim.name}: {sim.github_url}")
                continue

            owner, repo = parsed
            repo_data = self._fetch_repo_info(owner, repo)
            if not repo_data:
                continue

            # Update the Simulator record with live data
            sim.github_stars = repo_data.get("stargazers_count", 0)
            sim.github_open_issues = repo_data.get("open_issues_count", 0)
            sim.github_last_commit = repo_data.get("pushed_at", "")
            sim.last_updated = datetime.now(timezone.utc)

            # Fetch latest release tag
            release_tag = self._fetch_latest_release(owner, repo)
            if release_tag:
                sim.github_latest_release = release_tag

            self.session.flush()
            logger.info(
                f"[github] Updated {sim.name}: "
                f"{sim.github_stars} stars, "
                f"last push {sim.github_last_commit}, "
                f"release {sim.github_latest_release}"
            )

            # Create an Article entry for this simulator update
            description = repo_data.get("description", "") or ""
            pushed_at = repo_data.get("pushed_at", "")
            pub_date = None
            if pushed_at:
                try:
                    pub_date = datetime.fromisoformat(
                        pushed_at.replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            ext_id = f"github:{owner}/{repo}"
            results.append(
                {
                    "title": f"{sim.name} - Quantum Network Simulator ({sim.github_stars} stars)",
                    "authors": f"{owner}",
                    "abstract": (
                        f"{description}. "
                        f"Language: {sim.language}. "
                        f"License: {sim.license}. "
                        f"Status: {sim.status}. "
                        f"Stars: {sim.github_stars}. "
                        f"Latest release: {sim.github_latest_release or 'N/A'}."
                    ),
                    "url": sim.github_url,
                    "published_date": pub_date,
                    "content_type": "software",
                    "external_id": ext_id,
                    "source_name": "GitHub Simulators",
                    "raw_content": description,
                }
            )

        self.mark_source_fetched(source)
        return results

    def _fetch_repo_info(self, owner: str, repo: str) -> Optional[Dict]:
        """Fetch repository metadata from GitHub API."""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "QNetAgent/1.0",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 403:
                logger.warning(f"GitHub API rate limited for {owner}/{repo}")
            elif resp.status_code == 404:
                logger.warning(f"GitHub repo not found: {owner}/{repo}")
            else:
                logger.warning(
                    f"GitHub API returned {resp.status_code} for {owner}/{repo}"
                )
        except Exception as e:
            logger.error(f"GitHub API error for {owner}/{repo}: {e}")
        return None

    def _fetch_latest_release(self, owner: str, repo: str) -> Optional[str]:
        """Fetch the latest release tag name from GitHub API."""
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/releases/latest"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "QNetAgent/1.0",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("tag_name", "")
        except Exception:
            pass
        return None
