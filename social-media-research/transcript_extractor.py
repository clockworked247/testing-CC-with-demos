"""Video transcript extraction using OpenAI Whisper API."""

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


class TranscriptExtractor:
    """Extract transcripts from video URLs using Whisper API."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize transcript extractor.

        Args:
            openai_api_key: OpenAI API key (optional, will use env var if not provided)
        """
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key found. Transcript extraction will be disabled.")

        self.whisper_url = "https://api.openai.com/v1/audio/transcriptions"

    def extract_transcript(
        self,
        video_url: str,
        max_retries: int = 3,
        timeout: int = 300
    ) -> Optional[str]:
        """
        Extract transcript from a video URL.

        Args:
            video_url: URL of the video to transcribe
            max_retries: Maximum number of retry attempts
            timeout: Timeout for video download in seconds

        Returns:
            Transcript text or None if extraction failed
        """
        if not self.api_key:
            logger.debug("Skipping transcript extraction (no API key)")
            return None

        temp_file = None
        try:
            # Download video to temporary file
            logger.debug(f"Downloading video: {video_url}")
            temp_file = self._download_video(video_url, timeout)

            if not temp_file:
                return None

            # Transcribe with retries
            for attempt in range(max_retries):
                try:
                    transcript = self._transcribe_file(temp_file)
                    logger.debug(f"Successfully transcribed video (attempt {attempt + 1})")
                    return transcript
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Transcription attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Transcription failed after {max_retries} attempts: {e}")
                        return None

        except Exception as e:
            logger.error(f"Error extracting transcript from {video_url}: {e}")
            return None

        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {temp_file}: {e}")

    def _download_video(self, video_url: str, timeout: int = 300) -> Optional[str]:
        """
        Download video to temporary file.

        Args:
            video_url: URL of the video
            timeout: Download timeout in seconds

        Returns:
            Path to temporary file or None if download failed
        """
        try:
            response = requests.get(
                video_url,
                stream=True,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            response.raise_for_status()

            # Create temporary file with appropriate extension
            suffix = '.mp4'  # Default to mp4
            if 'content-type' in response.headers:
                content_type = response.headers['content-type'].lower()
                if 'webm' in content_type:
                    suffix = '.webm'
                elif 'mov' in content_type:
                    suffix = '.mov'

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                # Download in chunks to handle large files
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)

                return temp_file.name

        except requests.exceptions.Timeout:
            logger.error(f"Timeout downloading video from {video_url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading video from {video_url}: {e}")
            return None

    def _transcribe_file(self, file_path: str) -> str:
        """
        Transcribe audio file using Whisper API.

        Args:
            file_path: Path to audio/video file

        Returns:
            Transcript text

        Raises:
            Exception if transcription fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        with open(file_path, 'rb') as audio_file:
            files = {
                'file': (os.path.basename(file_path), audio_file, 'application/octet-stream'),
                'model': (None, 'whisper-1'),
                'response_format': (None, 'text')
            }

            response = requests.post(
                self.whisper_url,
                headers=headers,
                files=files,
                timeout=300
            )

            response.raise_for_status()
            return response.text.strip()

    def extract_batch(
        self,
        items: list[Dict[str, Any]],
        progress_callback: Optional[callable] = None
    ) -> list[Dict[str, Any]]:
        """
        Extract transcripts for a batch of items.

        Args:
            items: List of content items with potential video URLs
            progress_callback: Optional callback function for progress updates

        Returns:
            Items with transcripts added where available
        """
        if not self.api_key:
            logger.info("Skipping transcript extraction (no OpenAI API key)")
            return items

        total = len(items)
        for idx, item in enumerate(items):
            video_url = item.get('video_url')

            if video_url:
                logger.info(f"Extracting transcript {idx + 1}/{total}")
                transcript = self.extract_transcript(video_url)

                if transcript:
                    item['transcript'] = transcript
                    logger.info(f"✓ Transcript extracted ({len(transcript)} characters)")
                else:
                    item['transcript'] = None
                    logger.warning(f"✗ Transcript extraction failed")
            else:
                item['transcript'] = None

            if progress_callback:
                progress_callback(idx + 1, total)

        return items
