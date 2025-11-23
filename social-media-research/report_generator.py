"""Report generation and data export functionality."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate research reports and export data."""

    def __init__(self, output_dir: str = "output"):
        """Initialize report generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def save_raw_data(self, items: List[Dict[str, Any]], filename: str) -> Path:
        """
        Save raw scraped data to JSON.

        Args:
            items: List of content items
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved raw data to {output_path}")
        return output_path

    def save_research_report(
        self,
        report: str,
        research_question: str,
        metadata: Dict[str, Any]
    ) -> Path:
        """
        Save research report to markdown file.

        Args:
            report: The generated report content
            research_question: The research question
            metadata: Additional metadata about the research

        Returns:
            Path to saved report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_report_{timestamp}.md"
        output_path = self.output_dir / filename

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Social Media Research Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Research Question:** {research_question}\n\n")

            f.write("## Metadata\n\n")
            for key, value in metadata.items():
                f.write(f"- **{key}:** {value}\n")

            f.write(f"\n---\n\n")
            f.write(report)

        logger.info(f"Saved research report to {output_path}")
        return output_path

    def save_summary_statistics(
        self,
        items: List[Dict[str, Any]],
        filename: str = None
    ) -> Path:
        """
        Generate and save summary statistics.

        Args:
            items: List of content items
            filename: Optional output filename

        Returns:
            Path to saved statistics
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"statistics_{timestamp}.json"

        stats = self._calculate_statistics(items)
        output_path = self.output_dir / filename

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

        logger.info(f"Saved statistics to {output_path}")
        return output_path

    def _calculate_statistics(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics from content items."""
        if not items:
            return {}

        platforms = {}
        total_engagement = {
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "views": 0
        }

        for item in items:
            platform = item.get("platform", "unknown")
            platforms[platform] = platforms.get(platform, 0) + 1

            total_engagement["likes"] += item.get("likes", 0)
            total_engagement["comments"] += item.get("comments", 0)
            total_engagement["shares"] += item.get("shares", 0)
            total_engagement["views"] += item.get("views", 0)

        avg_engagement = {
            key: value / len(items) if len(items) > 0 else 0
            for key, value in total_engagement.items()
        }

        return {
            "total_items": len(items),
            "platforms": platforms,
            "total_engagement": total_engagement,
            "average_engagement": avg_engagement,
            "date_range": self._get_date_range(items)
        }

    def _get_date_range(self, items: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get date range of content."""
        timestamps = [
            item.get("timestamp")
            for item in items
            if item.get("timestamp")
        ]

        if not timestamps:
            return {"earliest": None, "latest": None}

        return {
            "earliest": min(timestamps),
            "latest": max(timestamps)
        }
