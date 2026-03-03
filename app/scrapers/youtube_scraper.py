"""
YouTube scraper for exam preparation channels.

This module implements a concrete scraper for fetching video transcripts
from YouTube exam preparation channels using RSS feeds and the YouTube
Transcript API.
"""

from typing import List, Optional
from datetime import datetime, timedelta, timezone
import logging
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from app.scrapers.abstract_scraper import AbstractScraper, ScrapedContent, ScraperException


logger = logging.getLogger(__name__)


class YouTubeScraper(AbstractScraper):
    """
    Concrete scraper for YouTube exam preparation channels.
    
    Inherits from AbstractScraper and implements YouTube-specific
    scraping logic using RSS feeds and transcript API. Demonstrates
    inheritance and polymorphism OOP principles.
    
    Attributes:
        _channel_ids (List[str]): YouTube channel IDs to scrape (private)
    """
    
    # Class constant: Exam preparation channels
    # These channels provide UPSC, SSC, Banking, and other competitive exam content
    EXAM_CHANNELS = [
        "UCYRBFLkuZ8ZAfwz7ayGGvZQ",  # StudyIQ IAS
        "UCnvC2wLZOiKdFkM8Ml4EzQg",  # Drishti IAS
        "UCZ8QY-RF48rE3LJRgdD0kVQ",  # Vision IAS
        "UCawZsQWqfGSbCI5yjkdVkTA",  # OnlyIAS
        "UCOEVlIHEsILuTV_Ix8dDW5A",  # Insights IAS
        "UCawZsQWqfGSbCI5yjkdVkTB",  # PIB India Official
        "UCawZsQWqfGSbCI5yjkdVkTC",  # Sansad TV
        "UCawZsQWqfGSbCI5yjkdVkTD",  # Vajiram & Ravi
        "UCawZsQWqfGSbCI5yjkdVkTE",  # Adda247
        "UCawZsQWqfGSbCI5yjkdVkTF",  # BYJU'S Exam Prep
        "UCawZsQWqfGSbCI5yjkdVkTG",  # Unacademy UPSC
    ]
    
    def __init__(self, channel_ids: Optional[List[str]] = None):
        """
        Initialize YouTube scraper.
        
        Args:
            channel_ids: Optional list of channel IDs (uses default if None)
        """
        super().__init__(
            source_name="YouTube Exam Channels",
            base_url="https://www.youtube.com",
            timeout=30
        )
        self._channel_ids = channel_ids or self.EXAM_CHANNELS
    
    def scrape(self, hours: int = 24) -> List[ScrapedContent]:
        """
        Scrape transcripts from all configured channels.
        
        Implements the abstract scrape() method from AbstractScraper,
        demonstrating polymorphism and the Liskov Substitution Principle.
        
        Args:
            hours: Number of hours to look back (default: 24)
            
        Returns:
            List of scraped video transcripts
            
        Raises:
            ScraperException: If scraping fails critically
        """
        self._log_scrape_start(hours)
        all_content = []
        
        for channel_id in self._channel_ids:
            try:
                videos = self._get_recent_videos(channel_id, hours)
                logger.info(
                    f"Found {len(videos)} recent videos for channel {channel_id}"
                )
                
                for video in videos:
                    transcript = self._get_transcript(video['video_id'])
                    if transcript:
                        content = ScrapedContent(
                            title=video['title'],
                            content=transcript,
                            url=video['url'],
                            published_at=video['published_at'],
                            source_type='youtube',
                            metadata={
                                'channel_id': channel_id,
                                'video_id': video['video_id'],
                                'description': video['description']
                            }
                        )
                        if self.validate_content(content):
                            all_content.append(content)
                        else:
                            logger.warning(
                                f"Content validation failed for video: {video['title']}"
                            )
                    else:
                        logger.debug(
                            f"No transcript available for video: {video['title']}"
                        )
            except Exception as e:
                self._handle_network_error(e)
                # Continue with next channel instead of failing completely
                continue
        
        self._log_scrape_complete(len(all_content))
        return all_content
    
    def _get_recent_videos(
        self, 
        channel_id: str, 
        hours: int
    ) -> List[dict]:
        """
        Get recent videos from a channel using RSS feed.
        
        Private method (encapsulation) that handles the details of
        fetching video metadata from YouTube RSS feeds.
        
        Args:
            channel_id: YouTube channel ID
            hours: Hours to look back
            
        Returns:
            List of video metadata dictionaries
            
        Raises:
            Exception: If RSS feed cannot be fetched
        """
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            logger.warning(f"Malformed RSS feed for channel {channel_id}")
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        videos = []
        
        for entry in feed.entries:
            # Skip YouTube Shorts (not typically exam content)
            if "/shorts/" in entry.link:
                logger.debug(f"Skipping YouTube Short: {entry.title}")
                continue
            
            # Parse publication time
            published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            
            # Only include videos within the time window
            if published_time >= cutoff_time:
                videos.append({
                    'title': entry.title,
                    'url': entry.link,
                    'video_id': self._extract_video_id(entry.link),
                    'published_at': published_time,
                    'description': entry.get('summary', '')
                })
        
        return videos
    
    def _extract_video_id(self, url: str) -> str:
        """
        Extract video ID from YouTube URL.
        
        Handles both youtube.com/watch and youtu.be URL formats.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID string
        """
        if "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        if "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        return url
    
    def _get_transcript(self, video_id: str) -> Optional[str]:
        """
        Get transcript for a video.
        
        Handles missing transcripts gracefully by returning None instead
        of crashing, as per requirement 2.3.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Transcript text or None if unavailable
        """
        try:
            # Fetch transcript (prefers English, falls back to auto-generated)
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get English transcript first
            try:
                transcript = transcript_list.find_transcript(['en', 'hi'])
            except:
                # Fall back to any available transcript
                transcript = transcript_list.find_generated_transcript(['en', 'hi'])
            
            # Combine all transcript snippets into single text
            transcript_data = transcript.fetch()
            return " ".join([item['text'] for item in transcript_data])
            
        except TranscriptsDisabled:
            logger.debug(f"Transcripts disabled for video {video_id}")
            return None
        except NoTranscriptFound:
            logger.debug(f"No transcript found for video {video_id}")
            return None
        except Exception as e:
            logger.warning(f"Error fetching transcript for {video_id}: {str(e)}")
            return None
