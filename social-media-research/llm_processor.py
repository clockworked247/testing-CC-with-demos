"""OpenRouter API integration for LLM-based content analysis."""

import logging
import time
import requests
from typing import List, Dict, Any
from tqdm import tqdm

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Process content using OpenRouter API."""

    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet", max_retries: int = 3):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key
            model: LLM model to use
            max_retries: Maximum number of retry attempts for API calls
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.max_retries = max_retries

    def analyze_content_batch(
        self,
        items: List[Dict[str, Any]],
        research_question: str
    ) -> str:
        """
        Analyze a batch of social media content.

        Args:
            items: List of content items to analyze
            research_question: The research question or topic to focus on

        Returns:
            Analysis summary as a string
        """
        logger.info(f"Analyzing {len(items)} items with LLM")

        content_summary = self._prepare_content_summary(items)

        prompt = f"""You are analyzing social media content to answer a research question.

Research Question: {research_question}

Content to analyze ({len(items)} items):

{content_summary}

Please provide a comprehensive analysis that:
1. Identifies key themes and patterns across the content
2. Highlights relevant insights related to the research question
3. Notes any trends in engagement (likes, comments, shares, views)
4. Summarizes the main narratives or messaging
5. Provides actionable insights and recommendations

Format your response as a structured analysis with clear sections."""

        response = self._call_openrouter(prompt)
        return response

    def generate_deep_research_report(
        self,
        all_items: List[Dict[str, Any]],
        research_question: str,
        batch_size: int = 20
    ) -> str:
        """
        Generate a comprehensive research report by processing content in batches.

        Args:
            all_items: All content items to analyze
            research_question: The research question to investigate
            batch_size: Number of items to process per batch

        Returns:
            Comprehensive research report
        """
        logger.info(f"Generating deep research report for {len(all_items)} items")

        batch_analyses = []
        num_batches = (len(all_items) + batch_size - 1) // batch_size

        with tqdm(total=num_batches, desc="Analyzing batches", unit="batch") as pbar:
            for i in range(0, len(all_items), batch_size):
                batch = all_items[i:i + batch_size]
                batch_num = i // batch_size + 1
                pbar.set_description(f"Analyzing batch {batch_num}/{num_batches}")

                try:
                    analysis = self.analyze_content_batch(batch, research_question)
                    batch_analyses.append(analysis)
                except Exception as e:
                    logger.error(f"Failed to analyze batch {batch_num}: {e}")
                    # Continue with other batches even if one fails
                    batch_analyses.append(f"[Batch {batch_num} analysis failed: {e}]")

                pbar.update(1)

        logger.info("Synthesizing final report...")
        synthesis_prompt = f"""You are synthesizing multiple analyses of social media content into a comprehensive research report.

Research Question: {research_question}

Total Content Analyzed: {len(all_items)} items across {len(batch_analyses)} batches

Individual Batch Analyses:

{self._format_batch_analyses(batch_analyses)}

Please create a comprehensive research report that:
1. Provides an executive summary of key findings
2. Synthesizes insights across all batches
3. Identifies overarching themes and patterns
4. Highlights the most significant discoveries
5. Provides data-driven recommendations
6. Includes limitations and considerations

Format the report professionally with clear sections and subsections."""

        final_report = self._call_openrouter(synthesis_prompt)
        return final_report

    def _prepare_content_summary(self, items: List[Dict[str, Any]]) -> str:
        """Prepare a summary of content items for analysis."""
        summaries = []

        for idx, item in enumerate(items, 1):
            platform = item.get("platform", "unknown")
            username = item.get("username", "unknown")

            if platform == "instagram":
                text = item.get("caption", "")
                engagement = f"Likes: {item.get('likes', 0)}, Comments: {item.get('comments', 0)}"
            else:
                text = item.get("description", "")
                engagement = f"Likes: {item.get('likes', 0)}, Comments: {item.get('comments', 0)}, Shares: {item.get('shares', 0)}, Views: {item.get('views', 0)}"

            # Include transcript if available
            transcript = item.get("transcript")
            transcript_section = ""
            if transcript:
                transcript_section = f"\nTranscript: {transcript[:1000]}{'...' if len(transcript) > 1000 else ''}"

            summary = f"""
Item {idx} [{platform.upper()}]:
Author: @{username}
Content: {text[:500]}{'...' if len(text) > 500 else ''}{transcript_section}
Engagement: {engagement}
URL: {item.get('url', 'N/A')}
---
"""
            summaries.append(summary)

        return "\n".join(summaries)

    def _format_batch_analyses(self, analyses: List[str]) -> str:
        """Format batch analyses for synthesis."""
        formatted = []
        for idx, analysis in enumerate(analyses, 1):
            formatted.append(f"\n=== BATCH {idx} ANALYSIS ===\n{analysis}\n")
        return "\n".join(formatted)

    def _call_openrouter(self, prompt: str, max_tokens: int = 4096) -> str:
        """
        Call OpenRouter API with retry logic.

        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens in response

        Returns:
            LLM response text

        Raises:
            Exception if all retries fail
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=120
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"OpenRouter API timeout. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error("OpenRouter API timeout after all retries")
                    raise

            except requests.exceptions.HTTPError as e:
                # Handle rate limits
                if e.response.status_code == 429:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** (attempt + 2)  # Longer wait for rate limits
                        logger.warning(f"Rate limited. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error("Rate limited after all retries")
                        raise
                else:
                    logger.error(f"HTTP error: {e}")
                    raise

            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"API call failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Error calling OpenRouter API after {self.max_retries} attempts: {e}")
                    raise

        raise Exception("Failed to call OpenRouter API after all retries")
