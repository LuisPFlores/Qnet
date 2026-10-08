"""Local analyzer for article summaries and topic extraction."""

import re
from typing import List, Dict, Any


class Analyzer:
    """Summarize and classify collected content without external AI services."""

    @staticmethod
    def _sentences(text: str) -> List[str]:
        cleaned = re.sub(r"\s+", " ", text or "").strip()
        if not cleaned:
            return []
        return [
            part.strip()
            for part in re.split(r"(?<=[.!?])\s+", cleaned)
            if part.strip()
        ]

    def summarize_article(
        self, title: str, abstract: str, domain: str = "quantum networking"
    ) -> str:
        """Generate a concise summary of an article."""
        if not abstract and not title:
            return ""

        sentences = self._sentences(abstract)
        if not sentences:
            return title.strip()
        summary = " ".join(sentences[:3])
        if len(summary) > 750:
            summary = summary[:747].rsplit(" ", 1)[0] + "..."
        return summary

    def extract_topics(self, title: str, abstract: str) -> List[str]:
        """Extract key topics/keywords from an article."""
        if not abstract and not title:
            return []

        text = f"{title} {abstract}".lower()
        vocabulary = [
            ("quantum key distribution", r"\bquantum key distribution\b"),
            ("satellite qkd", r"\b(?:satellite|satellite-based)\s+qkd\b"),
            ("quantum internet", r"\bquantum internet\b"),
            ("quantum network", r"\bquantum networks?\b"),
            ("quantum communication", r"\bquantum communications?\b"),
            ("entanglement distribution", r"\bentanglement distribution\b"),
            ("entanglement swapping", r"\bentanglement swapping\b"),
            ("quantum repeater", r"\bquantum repeaters?\b"),
            ("quantum memory", r"\bquantum memories?\b"),
            ("quantum teleportation", r"\bquantum teleportation\b"),
            ("quantum cryptography", r"\bquantum cryptography\b"),
            ("continuous-variable qkd", r"\bcontinuous.variable\s+(?:quantum key distribution|qkd)\b"),
            ("quantum routing", r"\bquantum routing\b"),
            ("quantum network protocols", r"\bquantum network protocols?\b"),
            ("distributed quantum computing", r"\bdistributed quantum computing\b"),
            ("qkd", r"\bqkd\b"),
        ]
        return [name for name, pattern in vocabulary if re.search(pattern, text)][:7]

    def generate_hot_topics_analysis(
        self, topics_with_counts: List[Dict[str, Any]], recent_titles: List[str]
    ) -> str:
        """Build a concise report from ranked topic data and recent titles."""
        if not topics_with_counts:
            return "No topic data is available yet. Collect and analyze articles to populate this report."

        lines = ["Top topics by ranking:"]
        for topic in topics_with_counts[:10]:
            lines.append(
                f"- {topic['name']}: {topic['count']} article mentions "
                f"(score {topic['score']:.2f})"
            )
        if recent_titles:
            lines.extend(["", "Recent article titles:"])
            lines.extend(f"- {title}" for title in recent_titles[:8])
        lines.extend(
            ["", "This report reflects collected article and topic data; it does not make predictions."]
        )
        return "\n".join(lines)

    def generate_latest_summary(
        self,
        new_papers: List[Dict],
        new_company_news: List[Dict],
        new_university_news: List[Dict],
        hot_topics: List[Dict],
    ) -> str:
        """Build a latest-content briefing from collected records."""
        sections = [
            ("Research Highlights", new_papers),
            ("Industry Updates", new_company_news),
            ("Academic Developments", new_university_news),
        ]
        lines = []
        for heading, articles in sections:
            lines.append(f"**{heading}**")
            if not articles:
                lines.append("- No new items.")
                continue
            for article in articles[:10]:
                source = article.get("source", "")
                title = article.get("title", "Untitled")
                abstract = re.sub(r"\s+", " ", article.get("abstract", "")).strip()
                detail = f": {abstract[:200]}" if abstract else ""
                lines.append(f"- [{source}] {title}{detail}")

        lines.append("**Trending Topics**")
        if hot_topics:
            lines.extend(
                f"- {topic['name']} (score: {topic.get('score', 0):.2f})"
                for topic in hot_topics[:10]
            )
        else:
            lines.append("- No topic data available.")
        return "\n".join(lines)

    def classify_content_type(self, title: str, content: str) -> str:
        """Classify content with simple local title/content cues."""
        text = f"{title} {content[:500]}".lower()
        if re.search(r"\b(conference|proceedings|workshop|symposium)\b", text):
            return "conference"
        if re.search(r"\b(product|launch|release|available now|platform)\b", text):
            return "product"
        if re.search(r"\b(blog|opinion|perspective)\b", text):
            return "blog"
        if re.search(r"\b(news|announces|announcement|press release)\b", text):
            return "news"
        return "paper"
