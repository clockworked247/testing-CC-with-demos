"""Apify API integration for Instagram and TikTok scraping."""

import logging
import time
from typing import List, Dict, Any, Optional, Callable
from apify_client import ApifyClient
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ApifyScraper:
    """Handle scraping of Instagram and TikTok content via Apify API."""

    INSTAGRAM_ACTOR = "apify/instagram-api-scraper"
    TIKTOK_ACTOR = "clockworks/tiktok-scraper"

    def __init__(self, api_key: str, max_retries: int = 3):
        """
        Initialize Apify client.

        Args:
            api_key: Apify API key
            max_retries: Maximum number of retry attempts for API calls
        """
        self.client = ApifyClient(api_key)
        self.max_retries = max_retries

    def _call_actor_with_retry(
        self,
        actor_id: str,
        run_input: Dict[str, Any],
        operation_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Call Apify actor with retry logic.

        Args:
            actor_id: Apify actor ID
            run_input: Input parameters for the actor
            operation_name: Description of operation for logging

        Returns:
            Actor run result or None if all retries failed
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"{operation_name} (attempt {attempt + 1}/{self.max_retries})")
                run = self.client.actor(actor_id).call(run_input=run_input)
                return run
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"API call failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API call failed after {self.max_retries} attempts: {e}")
                    raise

        return None

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

        run = self._call_actor_with_retry(
            self.INSTAGRAM_ACTOR,
            run_input,
            f"Scraping @{username}"
        )

        if not run:
            logger.error("Failed to scrape Instagram account")
            return []

        items = []
        dataset_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

        with tqdm(total=len(dataset_items), desc="Processing Instagram posts", unit="post") as pbar:
            for item in dataset_items:
                try:
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
                except Exception as e:
                    logger.warning(f"Error processing item: {e}")

                pbar.update(1)

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

        run = self._call_actor_with_retry(
            self.INSTAGRAM_ACTOR,
            run_input,
            f"Searching #{hashtag}"
        )

        if not run:
            logger.error("Failed to scrape Instagram hashtag")
            return []

        items = []
        dataset_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

        with tqdm(total=len(dataset_items), desc="Processing Instagram posts", unit="post") as pbar:
            for item in dataset_items:
                try:
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
                except Exception as e:
                    logger.warning(f"Error processing item: {e}")

                pbar.update(1)

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

        run = self._call_actor_with_retry(
            self.TIKTOK_ACTOR,
            run_input,
            f"Scraping @{username}"
        )

        if not run:
            logger.error("Failed to scrape TikTok account")
            return []

        items = []
        dataset_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

        with tqdm(total=len(dataset_items), desc="Processing TikTok videos", unit="video") as pbar:
            for item in dataset_items:
                try:
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
                except Exception as e:
                    logger.warning(f"Error processing item: {e}")

                pbar.update(1)

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

        run = self._call_actor_with_retry(
            self.TIKTOK_ACTOR,
            run_input,
            f"Searching '{search_query}'"
        )

        if not run:
            logger.error("Failed to scrape TikTok search")
            return []

        items = []
        dataset_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

        with tqdm(total=len(dataset_items), desc="Processing TikTok videos", unit="video") as pbar:
            for item in dataset_items:
                try:
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
                except Exception as e:
                    logger.warning(f"Error processing item: {e}")

                pbar.update(1)

        logger.info(f"Retrieved {len(items)} TikTok videos for search: {search_query}")
        return items
