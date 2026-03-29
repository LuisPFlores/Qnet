"""OpenAI-powered analyzer for summarization and topic extraction."""

import json
import logging
from typing import List, Dict, Any, Optional

from openai import OpenAI

import config

logger = logging.getLogger(__name__)


class Analyzer:
    """Uses OpenAI to summarize articles, extract topics, and generate insights."""

    def __init__(self):
        self.client = None
        if config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        else:
            logger.warning(
                "OPENAI_API_KEY not set – analyzer will return placeholder results"
            )

    def _call_openai(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        """Make an OpenAI chat completion call."""
        if not self.client:
            return ""
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return ""

    def summarize_article(self, title: str, abstract: str) -> str:
        """Generate a concise summary of an article."""
        if not abstract and not title:
            return ""

        system_prompt = (
            "You are a scientific research assistant specializing in quantum networking. "
            "Provide a concise 2-3 sentence summary of the given article that captures "
            "the key contribution and relevance to quantum networking."
        )
        user_prompt = f"Title: {title}\n\nAbstract/Content: {abstract}"

        return self._call_openai(system_prompt, user_prompt, max_tokens=300)

    def extract_topics(self, title: str, abstract: str) -> List[str]:
        """Extract key topics/keywords from an article."""
        if not abstract and not title:
            return []

        system_prompt = (
            "You are a topic extraction system for quantum networking research. "
            "Extract 3-7 specific topics or keywords from the given article. "
            "Return ONLY a JSON array of strings, no other text. "
            "Topics should be specific and relevant to quantum networking. "
            "Examples: 'quantum key distribution', 'entanglement swapping', "
            "'quantum repeater', 'satellite QKD', 'quantum memory'."
        )
        user_prompt = f"Title: {title}\n\nAbstract/Content: {abstract}"

        result = self._call_openai(system_prompt, user_prompt, max_tokens=200)

        try:
            # Try to parse JSON from the response
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            topics = json.loads(result)
            if isinstance(topics, list):
                return [str(t).strip().lower() for t in topics if t]
        except (json.JSONDecodeError, IndexError):
            # Fallback: split by comma or newline
            topics = [t.strip().strip('"\'').lower() for t in result.split(",")]
            return [t for t in topics if len(t) > 2]

        return []

    def generate_hot_topics_analysis(
        self, topics_with_counts: List[Dict[str, Any]], recent_titles: List[str]
    ) -> str:
        """Generate an AI narrative analysis of current hot topics."""
        system_prompt = (
            "You are a quantum networking research analyst. Based on the topic frequency "
            "data and recent article titles, provide a concise analysis (3-5 paragraphs) of:\n"
            "1. The hottest research topics right now in quantum networking\n"
            "2. Emerging trends that are gaining momentum\n"
            "3. Key areas where industry and academia are converging\n"
            "4. Predictions for near-term research directions\n\n"
            "Be specific and insightful. Reference the actual topics and papers where relevant."
        )

        topics_text = "\n".join(
            [
                f"- {t['name']}: {t['count']} mentions (score: {t['score']:.2f})"
                for t in topics_with_counts[:20]
            ]
        )
        titles_text = "\n".join([f"- {t}" for t in recent_titles[:30]])

        user_prompt = (
            f"Top topics by frequency and relevance:\n{topics_text}\n\n"
            f"Recent article titles:\n{titles_text}"
        )

        return self._call_openai(system_prompt, user_prompt, max_tokens=1500)

    def generate_latest_summary(
        self,
        new_papers: List[Dict],
        new_company_news: List[Dict],
        new_university_news: List[Dict],
        hot_topics: List[Dict],
    ) -> str:
        """Generate a comprehensive summary of the latest content across all sources."""
        system_prompt = (
            "You are a quantum networking intelligence analyst. Generate a comprehensive "
            "briefing summarizing the latest developments across research papers, company "
            "announcements, and university news. Structure your response with clear sections:\n"
            "1. **Research Highlights**: Key new papers and their significance\n"
            "2. **Industry Updates**: Notable company news and product developments\n"
            "3. **Academic Developments**: University research group updates\n"
            "4. **Trending Topics**: What topics are gaining the most attention\n"
            "5. **Key Takeaways**: 3-5 bullet points summarizing the most important developments\n\n"
            "Be concise but informative. Focus on what matters for someone tracking "
            "quantum networking developments."
        )

        papers_text = "\n".join(
            [
                f"- [{p.get('source', '')}] {p['title']}: {p.get('abstract', '')[:200]}"
                for p in new_papers[:15]
            ]
        )
        company_text = "\n".join(
            [
                f"- [{c.get('source', '')}] {c['title']}: {c.get('abstract', '')[:200]}"
                for c in new_company_news[:10]
            ]
        )
        uni_text = "\n".join(
            [
                f"- [{u.get('source', '')}] {u['title']}: {u.get('abstract', '')[:200]}"
                for u in new_university_news[:10]
            ]
        )
        topics_text = "\n".join(
            [f"- {t['name']} (score: {t.get('score', 0):.2f})" for t in hot_topics[:10]]
        )

        user_prompt = (
            f"New Research Papers:\n{papers_text or 'None found'}\n\n"
            f"Company News:\n{company_text or 'None found'}\n\n"
            f"University Updates:\n{uni_text or 'None found'}\n\n"
            f"Current Hot Topics:\n{topics_text or 'None available'}"
        )

        return self._call_openai(system_prompt, user_prompt, max_tokens=2000)

    def classify_content_type(self, title: str, content: str) -> str:
        """Classify content as paper, news, product, blog, or conference."""
        if not self.client:
            return "paper"

        system_prompt = (
            "Classify the following content into exactly one category: "
            "paper, news, product, blog, or conference. "
            "Return ONLY the category word, nothing else."
        )
        user_prompt = f"Title: {title}\nContent: {content[:500]}"

        result = self._call_openai(system_prompt, user_prompt, max_tokens=10)
        result = result.strip().lower()

        valid_types = {"paper", "news", "product", "blog", "conference"}
        return result if result in valid_types else "paper"
