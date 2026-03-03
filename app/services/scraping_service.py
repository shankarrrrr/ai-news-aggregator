"""
Scraping Service for orchestrating content scraping.

This module implements the Service Layer Pattern for coordinating
scraper execution and storing results via repositories.

Demonstrates:
- Service Layer Pattern (business logic coordination)
- Dependency Injection (depends on abstractions)
- Error handling and logging
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
import logging
import json

from app.scrapers.scraper_factory import ScraperFactory, SourceType
from app.scrapers.abstract_scraper import AbstractScraper, ScrapedContent
from app.database.repositories.article_repository import ArticleRepository
from app.database.repositories.source_repository import SourceRepository
from app.database.models import Article, Source


logger = logging.getLogger(__name__)


class ScrapingService:
    """
    Service for orchestrating content scraping from multiple sources.
    
    Coordinates scraper execution, duplicate filtering, and database storage.
    Implements the Service Layer Pattern to separate business logic from
    data access and presentation layers.
    
    Demonstrates:
    - Dependency Inversion Principle (depends on abstractions: repositories)
    - Single Responsibility Principle (only handles scraping orchestration)
    - Error handling for production readiness
    
    Attributes:
        _scraper_factory (ScraperFactory): Factory for creating scrapers
        _article_repo (ArticleRepository): Repository for article persistence
        _source_repo (SourceRepository): Repository for source metadata
    """
    
    def __init__(
        self,
        scraper_factory: ScraperFactory,
        article_repository: ArticleRepository,
        source_repository: SourceRepository
    ):
        """
        Initialize the scraping service with dependencies.
        
        Uses dependency injection to receive repository instances,
        demonstrating the Dependency Inversion Principle.
        
        Args:
            scraper_factory: Factory for creating scraper instances
            article_repository: Repository for article data access
            source_repository: Repository for source data access
        """
        self._scraper_factory = scraper_factory
        self._article_repo = article_repository
        self._source_repo = source_repository
        logger.info("ScrapingService initialized")
    
    def scrape_all_sources(
        self,
        hours: int = 24,
        source_types: Optional[List[SourceType]] = None
    ) -> Dict[str, int]:
        """
        Scrape content from all active sources.
        
        Orchestrates the complete scraping workflow:
        1. Get active sources from database
        2. Create scrapers for each source type
        3. Scrape content from each source
        4. Filter duplicates
        5. Store new articles in database
        
        Args:
            hours: Number of hours to look back for content
            source_types: Optional list of specific source types to scrape
                         (if None, scrapes all active sources)
        
        Returns:
            Dictionary with statistics:
            - 'total_scraped': Total items scraped from all sources
            - 'duplicates_filtered': Number of duplicates filtered out
            - 'articles_stored': Number of new articles stored
            - 'sources_processed': Number of sources successfully processed
            - 'sources_failed': Number of sources that failed
            
        Example:
            >>> service = ScrapingService(factory, article_repo, source_repo)
            >>> stats = service.scrape_all_sources(hours=24)
            >>> print(f"Stored {stats['articles_stored']} new articles")
        """
        logger.info(f"Starting scraping for last {hours} hours")
        
        # Get active sources from database and extract data while in session
        if source_types:
            active_sources_data = []
            for source_type in source_types:
                sources = self._source_repo.find_active_by_type(source_type)
                for source in sources:
                    active_sources_data.append({
                        'id': source.id,
                        'name': source.name,
                        'source_type': source.source_type.value if hasattr(source.source_type, 'value') else str(source.source_type),
                        'url': source.url
                    })
        else:
            sources = self._source_repo.find_active_sources()
            active_sources_data = []
            for source in sources:
                active_sources_data.append({
                    'id': source.id,
                    'name': source.name,
                    'source_type': source.source_type.value if hasattr(source.source_type, 'value') else str(source.source_type),
                    'url': source.url
                })
        
        logger.info(f"Found {len(active_sources_data)} active sources")
        
        # Statistics tracking
        total_scraped = 0
        sources_processed = 0
        sources_failed = 0
        all_scraped_content: List[tuple[ScrapedContent, dict]] = []
        
        # Scrape each source
        for source_data in active_sources_data:
            try:
                content_list = self._scrape_source_data(source_data, hours)
                
                # Pair each content with its source data
                for content in content_list:
                    all_scraped_content.append((content, source_data))
                
                total_scraped += len(content_list)
                sources_processed += 1
                
                logger.info(
                    f"Scraped {len(content_list)} items from {source_data['name']}"
                )
            except Exception as e:
                sources_failed += 1
                logger.error(
                    f"Failed to scrape {source_data['name']}: {str(e)}",
                    exc_info=True
                )
                # Continue with other sources even if one fails
                continue
        
        # Filter duplicates and create article entities
        articles_to_create = self._filter_duplicates(all_scraped_content)
        
        duplicates_filtered = total_scraped - len(articles_to_create)
        
        # Bulk insert articles
        if articles_to_create:
            try:
                created_articles = self._article_repo.bulk_create(articles_to_create)
                articles_stored = len(created_articles)
                logger.info(f"Stored {articles_stored} new articles in database")
            except Exception as e:
                logger.error(f"Failed to store articles: {str(e)}", exc_info=True)
                articles_stored = 0
        else:
            articles_stored = 0
            logger.info("No new articles to store")
        
        # Return statistics
        stats = {
            'total_scraped': total_scraped,
            'duplicates_filtered': duplicates_filtered,
            'articles_stored': articles_stored,
            'sources_processed': sources_processed,
            'sources_failed': sources_failed
        }
        
        logger.info(f"Scraping complete: {stats}")
        return stats
    
    def _scrape_source_data(
        self,
        source_data: dict,
        hours: int
    ) -> List[ScrapedContent]:
        """
        Scrape content from a single source using source data dict.
        
        Creates appropriate scraper using factory and executes scraping.
        
        Args:
            source_data: Dictionary with source information (id, name, source_type, url)
            hours: Number of hours to look back
            
        Returns:
            List of scraped content items
            
        Raises:
            ValueError: If source type is not supported
            Exception: If scraping fails
        """
        # Map database SourceType to factory SourceType
        source_type_map = {
            'youtube': SourceType.YOUTUBE,
            'pib': SourceType.PIB,
            'government_schemes': SourceType.GOVERNMENT_SCHEMES
        }
        
        source_type_str = source_data['source_type']
        
        if source_type_str not in source_type_map:
            raise ValueError(f"Unsupported source type: {source_type_str}")
        
        factory_source_type = source_type_map[source_type_str]
        
        # Create scraper using factory
        scraper = self._scraper_factory.create_scraper(factory_source_type)
        
        # Execute scraping
        logger.debug(f"Scraping {source_data['name']} with {scraper.__class__.__name__}")
        content_list = scraper.scrape(hours=hours)
        
        return content_list

    def _scrape_source(
        self,
        source: Source,
        hours: int
    ) -> List[ScrapedContent]:
        """
        Scrape content from a single source.
        
        Creates appropriate scraper using factory and executes scraping.
        
        Args:
            source: The source entity to scrape
            hours: Number of hours to look back
            
        Returns:
            List of scraped content items
            
        Raises:
            ValueError: If source type is not supported
            Exception: If scraping fails
        """
        # Map database SourceType to factory SourceType
        source_type_map = {
            'youtube': SourceType.YOUTUBE,
            'pib': SourceType.PIB,
            'government_schemes': SourceType.GOVERNMENT_SCHEMES
        }
        
        source_type_str = source.source_type.value if hasattr(source.source_type, 'value') else source.source_type
        
        if source_type_str not in source_type_map:
            raise ValueError(f"Unsupported source type: {source_type_str}")
        
        factory_source_type = source_type_map[source_type_str]
        
        # Create scraper using factory
        scraper = self._scraper_factory.create_scraper(factory_source_type)
        
        # Execute scraping
        logger.debug(f"Scraping {source.name} with {scraper.__class__.__name__}")
        content_list = scraper.scrape(hours=hours)
        
        return content_list
    
    def _filter_duplicates(
        self,
        scraped_content: List[tuple[ScrapedContent, dict]]
    ) -> List[Article]:
        """
        Filter out duplicate articles using URL comparison.
        
        Checks each scraped content URL against existing articles in database.
        Only creates Article entities for new content.
        
        Args:
            scraped_content: List of (ScrapedContent, source_data) tuples
            
        Returns:
            List of Article entities ready for insertion (no duplicates)
        """
        articles_to_create = []
        
        for content, source_data in scraped_content:
            # Check if article with this URL already exists
            existing = self._article_repo.find_by_url(content.url)
            
            if existing is not None:
                logger.debug(f"Duplicate found: {content.url}")
                continue
            
            # Create new article entity
            article = self._create_article_entity_from_data(content, source_data)
            articles_to_create.append(article)
        
        logger.info(
            f"Filtered {len(scraped_content) - len(articles_to_create)} duplicates"
        )
        
        return articles_to_create
    
    def _create_article_entity_from_data(
        self,
        content: ScrapedContent,
        source_data: dict
    ) -> Article:
        """
        Create an Article ORM entity from scraped content and source data.
        
        Converts ScrapedContent Pydantic model to SQLAlchemy Article model.
        
        Args:
            content: Scraped content data
            source_data: Dictionary with source information (id, name, source_type, url)
            
        Returns:
            Article entity ready for database insertion
        """
        # Serialize metadata to JSON string
        metadata_json = json.dumps(content.metadata) if content.metadata else None
        
        article = Article(
            title=content.title,
            content=content.content,
            url=content.url,
            published_at=content.published_at,
            source_id=source_data['id'],
            category_id=None,  # Will be set by CategorizationService
            secondary_categories=None,  # Will be set by CategorizationService
            metadata=metadata_json
        )
        
        return article

    def _create_article_entity(
        self,
        content: ScrapedContent,
        source: Source
    ) -> Article:
        """
        Create an Article ORM entity from scraped content.
        
        Converts ScrapedContent Pydantic model to SQLAlchemy Article model.
        
        Args:
            content: Scraped content data
            source: Source entity this content came from
            
        Returns:
            Article entity ready for database insertion
        """
        # Serialize metadata to JSON string
        metadata_json = json.dumps(content.metadata) if content.metadata else None
        
        article = Article(
            title=content.title,
            content=content.content,
            url=content.url,
            published_at=content.published_at,
            source_id=source.id,
            category_id=None,  # Will be set by CategorizationService
            secondary_categories=None,  # Will be set by CategorizationService
            metadata=metadata_json
        )
        
        return article
    
    def scrape_single_source(
        self,
        source_id: int,
        hours: int = 24
    ) -> Dict[str, int]:
        """
        Scrape content from a single source by ID.
        
        Useful for testing or re-scraping a specific source.
        
        Args:
            source_id: The source ID to scrape
            hours: Number of hours to look back
            
        Returns:
            Dictionary with statistics (same format as scrape_all_sources)
            
        Raises:
            ValueError: If source not found or inactive
        """
        source = self._source_repo.find_by_id(source_id)
        
        if source is None:
            raise ValueError(f"Source with ID {source_id} not found")
        
        if not source.is_active:
            raise ValueError(f"Source {source.name} is not active")
        
        logger.info(f"Scraping single source: {source.name}")
        
        try:
            content_list = self._scrape_source(source, hours)
            
            # Pair content with source
            scraped_content = [(content, source) for content in content_list]
            
            # Filter duplicates and create articles
            articles_to_create = self._filter_duplicates(scraped_content)
            
            # Store articles
            if articles_to_create:
                created_articles = self._article_repo.bulk_create(articles_to_create)
                articles_stored = len(created_articles)
            else:
                articles_stored = 0
            
            stats = {
                'total_scraped': len(content_list),
                'duplicates_filtered': len(content_list) - len(articles_to_create),
                'articles_stored': articles_stored,
                'sources_processed': 1,
                'sources_failed': 0
            }
            
            logger.info(f"Single source scraping complete: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to scrape source {source.name}: {str(e)}", exc_info=True)
            return {
                'total_scraped': 0,
                'duplicates_filtered': 0,
                'articles_stored': 0,
                'sources_processed': 0,
                'sources_failed': 1
            }
