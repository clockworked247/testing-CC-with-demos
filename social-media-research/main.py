#!/usr/bin/env python3
"""
Social Media Research Tool

Automated research tool for Instagram and TikTok using Apify API and OpenRouter.
"""

import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

from config import Config
from apify_scraper import ApifyScraper
from llm_processor import LLMProcessor
from report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the social media research tool."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Automated social media research tool for Instagram and TikTok"
    )

    parser.add_argument(
        "--platform",
        choices=["instagram", "tiktok"],
        required=True,
        help="Social media platform to scrape"
    )

    parser.add_argument(
        "--mode",
        choices=["account", "search"],
        required=True,
        help="Scraping mode: account profile or search/hashtag"
    )

    parser.add_argument(
        "--target",
        required=True,
        help="Username (for account mode) or search query/hashtag (for search mode)"
    )

    parser.add_argument(
        "--research-question",
        required=True,
        help="Research question to investigate"
    )

    parser.add_argument(
        "--max-items",
        type=int,
        default=50,
        help="Maximum number of items to scrape (default: 50)"
    )

    parser.add_argument(
        "--include-videos",
        action="store_true",
        help="Include video file URLs in the output"
    )

    parser.add_argument(
        "--no-analysis",
        action="store_true",
        help="Skip LLM analysis and only save raw data"
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for reports and data (default: output)"
    )

    args = parser.parse_args()

    try:
        config = Config.from_env()
        config.output_dir = args.output_dir
        config.max_videos_per_search = args.max_items
        config.include_video_files = args.include_videos

        run_research(config, args)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def run_research(config: Config, args):
    """Execute the research workflow."""

    logger.info("=" * 60)
    logger.info("Social Media Research Tool")
    logger.info("=" * 60)
    logger.info(f"Platform: {args.platform}")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Target: {args.target}")
    logger.info(f"Research Question: {args.research_question}")
    logger.info(f"Max Items: {args.max_items}")
    logger.info("=" * 60)

    scraper = ApifyScraper(config.apify_api_key)
    report_gen = ReportGenerator(config.output_dir)

    logger.info("\n[1/4] Scraping content...")
    items = scrape_content(scraper, args)

    if not items:
        logger.warning("No items found. Exiting.")
        return

    logger.info(f"\n[2/4] Saving raw data...")
    timestamp = Path(report_gen.output_dir).name
    raw_data_file = report_gen.save_raw_data(
        items,
        f"raw_data_{args.platform}_{args.mode}_{args.target.replace('/', '_')}.json"
    )
    logger.info(f"Raw data saved to: {raw_data_file}")

    stats_file = report_gen.save_summary_statistics(items)
    logger.info(f"Statistics saved to: {stats_file}")

    if args.no_analysis:
        logger.info("\nSkipping LLM analysis (--no-analysis flag set)")
        logger.info("\nDone! Check the output directory for results.")
        return

    logger.info("\n[3/4] Analyzing content with LLM...")
    processor = LLMProcessor(config.openrouter_api_key, config.openrouter_model)

    try:
        report = processor.generate_deep_research_report(
            items,
            args.research_question
        )

        logger.info("\n[4/4] Generating final report...")
        metadata = {
            "Platform": args.platform,
            "Mode": args.mode,
            "Target": args.target,
            "Total Items Analyzed": len(items),
            "LLM Model": config.openrouter_model
        }

        report_file = report_gen.save_research_report(
            report,
            args.research_question,
            metadata
        )

        logger.info("=" * 60)
        logger.info("Research Complete!")
        logger.info("=" * 60)
        logger.info(f"Raw data: {raw_data_file}")
        logger.info(f"Statistics: {stats_file}")
        logger.info(f"Research report: {report_file}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error during LLM processing: {e}")
        logger.info("Raw data has been saved. You can retry analysis later.")
        raise


def scrape_content(scraper: ApifyScraper, args) -> list:
    """Scrape content based on platform and mode."""

    if args.platform == "instagram":
        if args.mode == "account":
            return scraper.scrape_instagram_account(
                args.target,
                args.max_items,
                args.include_videos
            )
        else:
            return scraper.scrape_instagram_search(
                args.target,
                args.max_items,
                args.include_videos
            )
    else:
        if args.mode == "account":
            return scraper.scrape_tiktok_account(
                args.target,
                args.max_items,
                args.include_videos
            )
        else:
            return scraper.scrape_tiktok_search(
                args.target,
                args.max_items,
                args.include_videos
            )


if __name__ == "__main__":
    main()
