"""Configuration management for social media research app."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration."""

    apify_api_key: str
    openrouter_api_key: str
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    max_videos_per_search: int = 50
    include_video_files: bool = False
    output_dir: str = "output"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        apify_api_key = os.getenv("APIFY_API_KEY")
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

        if not apify_api_key:
            raise ValueError("APIFY_API_KEY environment variable is required")
        if not openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

        return cls(
            apify_api_key=apify_api_key,
            openrouter_api_key=openrouter_api_key,
            openrouter_model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
            max_videos_per_search=int(os.getenv("MAX_VIDEOS_PER_SEARCH", "50")),
            include_video_files=os.getenv("INCLUDE_VIDEO_FILES", "false").lower() == "true",
            output_dir=os.getenv("OUTPUT_DIR", "output")
        )
