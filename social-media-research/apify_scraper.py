"""Apify API integration for Instagram and TikTok scraping."""

import logging
from typing import List, Dict, Any, Optional
from apify_client import ApifyClient

logger = logging.getLogger(__name__)


class ApifyScraper:
    """Handle scraping of Instagram and TikTok content via Apify API."""

    INSTAGRAM_ACTOR = "apify/instagram-api-scraper"
    TIKTOK_ACTOR = "clockworks/tiktok-scraper"

    def __init__(self, api_key: str):
        """Initialize Apify client."""
        self.client = ApifyClient(api_key)

    def scrape_instagram_account(
        self,
        username: str,
        max_items: int = 50,
        include_videos: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Scrape Instagram account posts.

        Args:
            username: Instagram username to scrape
            max_items: Maximum number of posts to retrieve
            include_videos: Whether to include video file URLs

        Returns:
            List of post data dictionaries
        """
        logger.info(f"Scraping Instagram account: {username}")

        run_input = {
            "usernames": [username],
            "resultsLimit": max_items,
            "resultsType": "posts"
        }

        run = self.client.actor(self.INSTAGRAM_ACTOR).call(run_input=run_input)

        items = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            processed_item = {
                "platform": "instagram",
                "id": item.get("id"),
                "username": item.get("ownerUsername"),
                "caption": item.get("caption", ""),
                "timestamp": item.get("timestamp"),
                "likes": item.get("likesCount"),
                "comments": item.get("commentsCount"),
                "url": item.get("url"),
                "type": item.get("type"),
            }

            if include_videos and item.get("videoUrl"):
                processed_item["video_url"] = item.get("videoUrl")

            items.append(processed_item)

        logger.info(f"Retrieved {len(items)} Instagram posts")
        return items

    def scrape_instagram_search(
        self,
        hashtag: str,
        max_items: int = 50,
        include_videos: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Scrape Instagram posts by hashtag.

        Args:
            hashtag: Hashtag to search (without #)
            max_items: Maximum number of posts to retrieve
            include_videos: Whether to include video file URLs

        Returns:
            List of post data dictionaries
        """
        logger.info(f"Scraping Instagram hashtag: #{hashtag}")

        run_input = {
            "hashtags": [hashtag],
            "resultsLimit": max_items,
            "resultsType": "posts"
        }

        run = self.client.actor(self.INSTAGRAM_ACTOR).call(run_input=run_input)

        items = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            processed_item = {
                "platform": "instagram",
                "id": item.get("id"),
                "username": item.get("ownerUsername"),
                "caption": item.get("caption", ""),
                "timestamp": item.get("timestamp"),
                "likes": item.get("likesCount"),
                "comments": item.get("commentsCount"),
                "url": item.get("url"),
                "type": item.get("type"),
            }

            if include_videos and item.get("videoUrl"):
                processed_item["video_url"] = item.get("videoUrl")

            items.append(processed_item)

        logger.info(f"Retrieved {len(items)} Instagram posts for #{hashtag}")
        return items

    def scrape_tiktok_account(
        self,
        username: str,
        max_items: int = 50,
        include_videos: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Scrape TikTok account videos.

        Args:
            username: TikTok username to scrape
            max_items: Maximum number of videos to retrieve
            include_videos: Whether to include video file URLs

        Returns:
            List of video data dictionaries
        """
        logger.info(f"Scraping TikTok account: @{username}")

        run_input = {
            "profiles": [username],
            "resultsPerPage": max_items,
            "shouldDownloadVideos": include_videos,
            "shouldDownloadCovers": False
        }

        run = self.client.actor(self.TIKTOK_ACTOR).call(run_input=run_input)

        items = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            processed_item = {
                "platform": "tiktok",
                "id": item.get("id"),
                "username": item.get("authorMeta", {}).get("name"),
                "description": item.get("text", ""),
                "timestamp": item.get("createTime"),
                "likes": item.get("diggCount"),
                "comments": item.get("commentCount"),
                "shares": item.get("shareCount"),
                "views": item.get("playCount"),
                "url": item.get("webVideoUrl"),
            }

            if include_videos and item.get("videoUrl"):
                processed_item["video_url"] = item.get("videoUrl")

            items.append(processed_item)

        logger.info(f"Retrieved {len(items)} TikTok videos")
        return items

    def scrape_tiktok_search(
        self,
        search_query: str,
        max_items: int = 50,
        include_videos: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Scrape TikTok videos by search query.

        Args:
            search_query: Search query or hashtag
            max_items: Maximum number of videos to retrieve
            include_videos: Whether to include video file URLs

        Returns:
            List of video data dictionaries
        """
        logger.info(f"Scraping TikTok search: {search_query}")

        run_input = {
            "searchQueries": [search_query],
            "resultsPerPage": max_items,
            "shouldDownloadVideos": include_videos,
            "shouldDownloadCovers": False
        }

        run = self.client.actor(self.TIKTOK_ACTOR).call(run_input=run_input)

        items = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            processed_item = {
                "platform": "tiktok",
                "id": item.get("id"),
                "username": item.get("authorMeta", {}).get("name"),
                "description": item.get("text", ""),
                "timestamp": item.get("createTime"),
                "likes": item.get("diggCount"),
                "comments": item.get("commentCount"),
                "shares": item.get("shareCount"),
                "views": item.get("playCount"),
                "url": item.get("webVideoUrl"),
            }

            if include_videos and item.get("videoUrl"):
                processed_item["video_url"] = item.get("videoUrl")

            items.append(processed_item)

        logger.info(f"Retrieved {len(items)} TikTok videos for search: {search_query}")
        return items
