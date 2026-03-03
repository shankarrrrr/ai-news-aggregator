"""
Scrapers package for content aggregation.

This package contains all scraper implementations for fetching content
from various sources (YouTube, PIB, Government Schemes).
"""

from app.scrapers.abstract_scraper import (
    AbstractScraper,
    ScrapedContent,
    ScraperException
)
from app.scrapers.youtube_scraper import YouTubeScraper
from app.scrapers.pib_scraper import PIBScraper
from app.scrapers.government_schemes_scraper import GovernmentSchemesScraper
from app.scrapers.scraper_factory import (
    ScraperFactory,
    SourceType,
    create_scraper
)


__all__ = [
    # Abstract base
    'AbstractScraper',
    'ScrapedContent',
    'ScraperException',
    
    # Concrete scrapers
    'YouTubeScraper',
    'PIBScraper',
    'GovernmentSchemesScraper',
    
    # Factory
    'ScraperFactory',
    'SourceType',
    'create_scraper',
]
