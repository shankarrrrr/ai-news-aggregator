"""
Government Schemes scraper for welfare programs and policy information.

This module implements a concrete scraper for fetching information about
government schemes from official portals.
"""

from typing import List, Optional, Dict
from datetime import datetime, timezone
import logging
import requests
from bs4 import BeautifulSoup

from app.scrapers.abstract_scraper import AbstractScraper, ScrapedContent, ScraperException


logger = logging.getLogger(__name__)


class GovernmentSchemesScraper(AbstractScraper):
    """
    Concrete scraper for government schemes and welfare programs.
    
    Inherits from AbstractScraper and implements scheme-specific
    scraping logic for various government portals. Demonstrates
    inheritance and polymorphism OOP principles.
    
    Attributes:
        _portals (List[Dict[str, str]]): Government portals to scrape (private)
    """
    
    # Government scheme portals relevant to competitive exams
    SCHEME_PORTALS = [
        {
            'name': 'MyScheme',
            'url': 'https://www.myscheme.gov.in',
            'type': 'central'
        },
        {
            'name': 'India.gov.in Schemes',
            'url': 'https://www.india.gov.in/topics/schemes',
            'type': 'central'
        },
        {
            'name': 'Ministry of Rural Development',
            'url': 'https://rural.nic.in/schemes',
            'type': 'ministry'
        },
        {
            'name': 'Ministry of Social Justice',
            'url': 'https://socialjustice.gov.in/schemes',
            'type': 'ministry'
        }
    ]
    
    def __init__(self, portals: Optional[List[Dict[str, str]]] = None):
        """
        Initialize Government Schemes scraper.
        
        Args:
            portals: Optional list of portal configurations (uses default if None)
        """
        super().__init__(
            source_name="Government Schemes Portals",
            base_url="https://www.india.gov.in",
            timeout=30
        )
        self._portals = portals or self.SCHEME_PORTALS
    
    def scrape(self, hours: int = 24) -> List[ScrapedContent]:
        """
        Scrape scheme information from government portals.
        
        Implements the abstract scrape() method from AbstractScraper.
        Note: Schemes are updated less frequently than news, so we use
        current timestamp for all schemes as per requirement 4.5.
        
        Args:
            hours: Number of hours to look back (not strictly used for schemes)
            
        Returns:
            List of scraped scheme information
            
        Raises:
            ScraperException: If scraping fails critically
        """
        self._log_scrape_start(hours)
        all_content = []
        
        for portal in self._portals:
            try:
                schemes = self._scrape_portal(portal)
                logger.info(
                    f"Scraped {len(schemes)} schemes from portal: {portal['name']}"
                )
                all_content.extend(schemes)
            except Exception as e:
                self._handle_network_error(e)
                # Continue with next portal instead of failing completely
                continue
        
        self._log_scrape_complete(len(all_content))
        return all_content
    
    def _scrape_portal(self, portal: Dict[str, str]) -> List[ScrapedContent]:
        """
        Scrape schemes from a specific government portal.
        
        Private method (encapsulation) that handles portal-specific scraping.
        Handles varying HTML structures across portals as per requirement 4.5.
        
        Args:
            portal: Portal configuration dictionary
            
        Returns:
            List of scraped content
            
        Raises:
            Exception: If HTTP request fails
        """
        try:
            response = requests.get(
                portal['url'],
                timeout=self._timeout,
                headers={'User-Agent': 'Mozilla/5.0'}  # Some portals require user agent
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch portal {portal['name']}: {str(e)}")
            raise
        
        soup = BeautifulSoup(response.content, 'html.parser')
        schemes = []
        
        # Try multiple HTML patterns to handle varying structures
        scheme_containers = (
            soup.find_all('div', class_='scheme-item') or
            soup.find_all('div', class_='scheme-card') or
            soup.find_all('article', class_='scheme') or
            soup.find_all('div', class_='content-item')
        )
        
        for container in scheme_containers:
            try:
                scheme = self._parse_scheme(container, portal)
                if scheme and self.validate_content(scheme):
                    schemes.append(scheme)
                else:
                    logger.debug(f"Content validation failed for scheme")
            except Exception as e:
                # Handle malformed HTML gracefully
                logger.warning(f"Failed to parse scheme item: {str(e)}")
                continue
        
        return schemes
    
    def _parse_scheme(
        self, 
        container: BeautifulSoup, 
        portal: Dict[str, str]
    ) -> Optional[ScrapedContent]:
        """
        Parse a single scheme item.
        
        Handles varying HTML structures across different portals.
        
        Args:
            container: BeautifulSoup element containing scheme
            portal: Portal configuration
            
        Returns:
            ScrapedContent or None if parsing fails
        """
        try:
            # Extract scheme name (title)
            title_elem = (
                container.find('h3') or
                container.find('h2') or
                container.find('h4') or
                container.find('a', class_='scheme-title')
            )
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # Extract scheme details
            metadata = self._extract_scheme_metadata(container)
            
            # Format content from metadata
            content = self._format_scheme_content(title, metadata)
            
            # Extract URL
            link_elem = container.find('a', href=True)
            if not link_elem:
                # Use portal URL as fallback
                url = portal['url']
            else:
                url = link_elem['href']
                if not url.startswith('http'):
                    # Handle relative URLs
                    base = portal['url'].rstrip('/')
                    url = f"{base}/{url.lstrip('/')}"
            
            # Use current timestamp (schemes updated less frequently)
            published_at = datetime.now(timezone.utc)
            
            return ScrapedContent(
                title=title,
                content=content,
                url=url,
                published_at=published_at,
                source_type='government_schemes',
                metadata={
                    'portal': portal['name'],
                    'portal_type': portal['type'],
                    **metadata
                }
            )
        except Exception as e:
            logger.debug(f"Error parsing scheme: {str(e)}")
            return None
    
    def _extract_scheme_metadata(self, container: BeautifulSoup) -> Dict[str, str]:
        """
        Extract scheme metadata (ministry, objectives, beneficiaries, launch date).
        
        Handles varying HTML structures to extract as much metadata as possible.
        
        Args:
            container: BeautifulSoup element containing scheme
            
        Returns:
            Dictionary of metadata fields
        """
        metadata = {}
        
        # Extract ministry
        ministry_elem = (
            container.find('span', class_='ministry') or
            container.find('div', class_='ministry') or
            container.find(string=lambda s: s and 'Ministry' in str(s))
        )
        if ministry_elem:
            metadata['ministry'] = ministry_elem.get_text(strip=True) if hasattr(ministry_elem, 'get_text') else str(ministry_elem).strip()
        
        # Extract objectives
        objectives_elem = (
            container.find('div', class_='objectives') or
            container.find('p', class_='description') or
            container.find('div', class_='summary')
        )
        if objectives_elem:
            metadata['objectives'] = objectives_elem.get_text(strip=True)
        
        # Extract beneficiaries
        beneficiaries_elem = (
            container.find('span', class_='beneficiaries') or
            container.find('div', class_='target-group')
        )
        if beneficiaries_elem:
            metadata['beneficiaries'] = beneficiaries_elem.get_text(strip=True)
        
        # Extract launch date
        date_elem = (
            container.find('span', class_='launch-date') or
            container.find('time') or
            container.find('span', class_='date')
        )
        if date_elem:
            metadata['launch_date'] = date_elem.get_text(strip=True)
        
        return metadata
    
    def _format_scheme_content(
        self, 
        title: str, 
        metadata: Dict[str, str]
    ) -> str:
        """
        Format scheme content from title and metadata.
        
        Creates a structured text representation of the scheme information.
        
        Args:
            title: Scheme name
            metadata: Extracted metadata
            
        Returns:
            Formatted content string
        """
        content_parts = [f"Scheme: {title}"]
        
        if 'ministry' in metadata:
            content_parts.append(f"Ministry: {metadata['ministry']}")
        
        if 'objectives' in metadata:
            content_parts.append(f"Objectives: {metadata['objectives']}")
        
        if 'beneficiaries' in metadata:
            content_parts.append(f"Beneficiaries: {metadata['beneficiaries']}")
        
        if 'launch_date' in metadata:
            content_parts.append(f"Launch Date: {metadata['launch_date']}")
        
        return "\n\n".join(content_parts)
