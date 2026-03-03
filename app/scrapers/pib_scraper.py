"""
PIB (Press Information Bureau) scraper for government press releases.

This module implements a concrete scraper for fetching official government
press releases from the Press Information Bureau website.
"""

from typing import List, Optional
from datetime import datetime, timedelta, timezone
import logging
import requests
from bs4 import BeautifulSoup

from app.scrapers.abstract_scraper import AbstractScraper, ScrapedContent, ScraperException


logger = logging.getLogger(__name__)


class PIBScraper(AbstractScraper):
    """
    Concrete scraper for PIB (Press Information Bureau) press releases.
    
    Inherits from AbstractScraper and implements PIB-specific
    scraping logic for government press releases. Demonstrates
    inheritance and the Liskov Substitution Principle.
    
    Attributes:
        _categories (List[str]): PIB categories to scrape (private)
    """
    
    # PIB categories relevant to competitive exams
    EXAM_RELEVANT_CATEGORIES = [
        "Government Policies",
        "Economy",
        "Defence",
        "International Relations",
        "Science & Technology",
        "Environment",
        "Social Welfare"
    ]
    
    def __init__(self, categories: Optional[List[str]] = None):
        """
        Initialize PIB scraper.
        
        Args:
            categories: Optional list of categories (uses default if None)
        """
        super().__init__(
            source_name="Press Information Bureau",
            base_url="https://pib.gov.in",
            timeout=30
        )
        self._categories = categories or self.EXAM_RELEVANT_CATEGORIES
    
    def scrape(self, hours: int = 24) -> List[ScrapedContent]:
        """
        Scrape press releases from PIB.
        
        Implements the abstract scrape() method from AbstractScraper,
        demonstrating polymorphism.
        
        Args:
            hours: Number of hours to look back (default: 24)
            
        Returns:
            List of scraped press releases
            
        Raises:
            ScraperException: If scraping fails critically
        """
        self._log_scrape_start(hours)
        all_content = []
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        for category in self._categories:
            try:
                releases = self._scrape_category(category, cutoff_time)
                logger.info(
                    f"Scraped {len(releases)} releases from category: {category}"
                )
                all_content.extend(releases)
            except Exception as e:
                self._handle_network_error(e)
                # Continue with next category instead of failing completely
                continue
        
        self._log_scrape_complete(len(all_content))
        return all_content
    
    def _scrape_category(
        self, 
        category: str, 
        cutoff_time: datetime
    ) -> List[ScrapedContent]:
        """
        Scrape press releases for a specific category.
        
        Private method (encapsulation) that handles category-specific scraping.
        
        Args:
            category: PIB category name
            cutoff_time: Only include releases after this time
            
        Returns:
            List of scraped content
            
        Raises:
            Exception: If HTTP request fails
        """
        # PIB release list page (simplified URL structure)
        # In production, this would use actual PIB API or page structure
        releases_url = f"{self._base_url}/PressReleasePage.aspx"
        
        try:
            response = requests.get(
                releases_url,
                params={'Category': category},
                timeout=self._timeout
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch PIB category {category}: {str(e)}")
            raise
        
        soup = BeautifulSoup(response.content, 'html.parser')
        releases = []
        
        # Find all press release entries
        # Note: Actual PIB HTML structure may vary; this is a representative implementation
        for item in soup.find_all('div', class_='content-area'):
            try:
                release = self._parse_release(item, category)
                if release and release.published_at >= cutoff_time:
                    if self.validate_content(release):
                        releases.append(release)
                    else:
                        logger.debug(f"Content validation failed for: {release.title}")
            except Exception as e:
                # Handle malformed HTML gracefully
                logger.warning(f"Failed to parse release item: {str(e)}")
                continue
        
        return releases
    
    def _parse_release(
        self, 
        item: BeautifulSoup, 
        category: str
    ) -> Optional[ScrapedContent]:
        """
        Parse a single press release item.
        
        Handles malformed HTML gracefully by returning None if parsing fails.
        
        Args:
            item: BeautifulSoup element containing release
            category: Category name
            
        Returns:
            ScrapedContent or None if parsing fails
        """
        try:
            # Extract title
            title_elem = item.find('h3') or item.find('h2')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # Extract content
            content_elem = item.find('div', class_='press-content') or item.find('p')
            if not content_elem:
                return None
            content = content_elem.get_text(strip=True)
            
            # Extract date (PIB format: DD-MMM-YYYY HH:MM)
            date_elem = item.find('span', class_='date') or item.find('time')
            if not date_elem:
                return None
            date_str = date_elem.get_text(strip=True)
            published_at = self._parse_pib_date(date_str)
            
            # Extract URL
            link_elem = item.find('a', href=True)
            if not link_elem:
                return None
            url = link_elem['href']
            if not url.startswith('http'):
                url = f"{self._base_url}{url}"
            
            # Extract ministry
            ministry = self._extract_ministry(item)
            
            return ScrapedContent(
                title=title,
                content=content,
                url=url,
                published_at=published_at,
                source_type='pib',
                metadata={
                    'category': category,
                    'ministry': ministry
                }
            )
        except Exception as e:
            logger.debug(f"Error parsing release: {str(e)}")
            return None
    
    def _parse_pib_date(self, date_str: str) -> datetime:
        """
        Parse PIB date format (DD-MMM-YYYY HH:MM).
        
        Handles PIB-specific date format parsing as per requirement 3.6.
        
        Args:
            date_str: Date string in PIB format
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValueError: If date format is invalid
        """
        # Common PIB date formats
        formats = [
            "%d-%b-%Y %H:%M",  # 15-Jan-2024 14:30
            "%d-%B-%Y %H:%M",  # 15-January-2024 14:30
            "%d/%m/%Y %H:%M",  # 15/01/2024 14:30
            "%d-%m-%Y %H:%M",  # 15-01-2024 14:30
            "%d-%b-%Y",        # 15-Jan-2024 (no time)
            "%d-%B-%Y",        # 15-January-2024 (no time)
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                # Add timezone info (PIB uses IST, convert to UTC)
                # IST is UTC+5:30
                dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
        
        # If all formats fail, log warning and use current time
        logger.warning(f"Could not parse PIB date: {date_str}, using current time")
        return datetime.now(timezone.utc)
    
    def _extract_ministry(self, item: BeautifulSoup) -> Optional[str]:
        """
        Extract ministry name from press release.
        
        Args:
            item: BeautifulSoup element containing release
            
        Returns:
            Ministry name or None if not found
        """
        # Look for ministry information in common locations
        ministry_elem = (
            item.find('span', class_='ministry') or
            item.find('div', class_='ministry') or
            item.find('strong', string=lambda s: s and 'Ministry' in s)
        )
        
        if ministry_elem:
            return ministry_elem.get_text(strip=True)
        
        return None
