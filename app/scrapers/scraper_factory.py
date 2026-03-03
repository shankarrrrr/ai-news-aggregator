"""
Scraper Factory for creating scraper instances.

This module implements the Factory Pattern for centralized scraper creation,
demonstrating the Open/Closed Principle (open for extension, closed for modification).
"""

from enum import Enum
from typing import Dict, Type, List, Optional
import logging

from app.scrapers.abstract_scraper import AbstractScraper
from app.scrapers.youtube_scraper import YouTubeScraper
from app.scrapers.pib_scraper import PIBScraper
from app.scrapers.government_schemes_scraper import GovernmentSchemesScraper


logger = logging.getLogger(__name__)


class SourceType(Enum):
    """
    Enumeration of available content source types.
    
    Provides type-safe source type identifiers for the factory.
    """
    YOUTUBE = "youtube"
    PIB = "pib"
    GOVERNMENT_SCHEMES = "government_schemes"


class ScraperFactory:
    """
    Factory class for creating scraper instances.
    
    Implements the Factory Pattern with a registry-based approach,
    allowing new scrapers to be registered without modifying the factory code.
    This demonstrates the Open/Closed Principle - the factory is open for
    extension (new scrapers can be registered) but closed for modification
    (no need to change factory code when adding new scrapers).
    
    Class Attributes:
        _registry (Dict[SourceType, Type[AbstractScraper]]): Registry mapping
            source types to scraper classes (class-level, shared across instances)
    """
    
    # Class-level registry (Singleton-like behavior for the registry)
    _registry: Dict[SourceType, Type[AbstractScraper]] = {}
    
    @classmethod
    def register_scraper(
        cls,
        source_type: SourceType,
        scraper_class: Type[AbstractScraper]
    ) -> None:
        """
        Register a scraper class for a source type.
        
        Allows dynamic registration of new scrapers without modifying
        the factory code, demonstrating extensibility.
        
        Args:
            source_type: The source type enum value
            scraper_class: The scraper class to register (must inherit from AbstractScraper)
            
        Raises:
            TypeError: If scraper_class does not inherit from AbstractScraper
        """
        if not issubclass(scraper_class, AbstractScraper):
            raise TypeError(
                f"{scraper_class.__name__} must inherit from AbstractScraper"
            )
        
        cls._registry[source_type] = scraper_class
        logger.info(
            f"Registered scraper: {scraper_class.__name__} for {source_type.value}"
        )
    
    @classmethod
    def create_scraper(
        cls,
        source_type: SourceType,
        **kwargs
    ) -> AbstractScraper:
        """
        Create a scraper instance for the specified source type.
        
        Factory method that returns the appropriate scraper instance.
        Demonstrates polymorphism - all scrapers implement the same interface
        (AbstractScraper) and can be used interchangeably.
        
        Args:
            source_type: The source type to create a scraper for
            **kwargs: Additional arguments to pass to the scraper constructor
            
        Returns:
            An instance of the appropriate scraper class
            
        Raises:
            ValueError: If source_type is not registered
            
        Example:
            >>> factory = ScraperFactory()
            >>> youtube_scraper = factory.create_scraper(SourceType.YOUTUBE)
            >>> pib_scraper = factory.create_scraper(SourceType.PIB)
        """
        if source_type not in cls._registry:
            available = ", ".join([st.value for st in cls._registry.keys()])
            raise ValueError(
                f"Unknown source type: {source_type.value}. "
                f"Available types: {available}"
            )
        
        scraper_class = cls._registry[source_type]
        logger.debug(f"Creating scraper: {scraper_class.__name__}")
        
        return scraper_class(**kwargs)
    
    @classmethod
    def get_available_sources(cls) -> List[SourceType]:
        """
        Get list of all registered source types.
        
        Useful for discovering what scrapers are available at runtime.
        
        Returns:
            List of registered SourceType enum values
            
        Example:
            >>> sources = ScraperFactory.get_available_sources()
            >>> print([s.value for s in sources])
            ['youtube', 'pib', 'government_schemes']
        """
        return list(cls._registry.keys())
    
    @classmethod
    def create_all_scrapers(cls, **kwargs) -> List[AbstractScraper]:
        """
        Create instances of all registered scrapers.
        
        Convenient method for creating all available scrapers at once,
        useful for pipeline execution that needs to scrape from all sources.
        
        Args:
            **kwargs: Additional arguments to pass to all scraper constructors
            
        Returns:
            List of scraper instances for all registered source types
            
        Example:
            >>> scrapers = ScraperFactory.create_all_scrapers()
            >>> for scraper in scrapers:
            ...     content = scraper.scrape(hours=24)
        """
        scrapers = []
        for source_type in cls._registry.keys():
            try:
                scraper = cls.create_scraper(source_type, **kwargs)
                scrapers.append(scraper)
            except Exception as e:
                logger.error(
                    f"Failed to create scraper for {source_type.value}: {str(e)}"
                )
                # Continue creating other scrapers even if one fails
                continue
        
        logger.info(f"Created {len(scrapers)} scrapers")
        return scrapers
    
    @classmethod
    def clear_registry(cls) -> None:
        """
        Clear all registered scrapers.
        
        Primarily useful for testing to reset the registry state.
        """
        cls._registry.clear()
        logger.debug("Cleared scraper registry")


# Register all available scrapers at module level
# This happens automatically when the module is imported
ScraperFactory.register_scraper(SourceType.YOUTUBE, YouTubeScraper)
ScraperFactory.register_scraper(SourceType.PIB, PIBScraper)
ScraperFactory.register_scraper(SourceType.GOVERNMENT_SCHEMES, GovernmentSchemesScraper)


# Convenience function for backward compatibility
def create_scraper(source_type: SourceType, **kwargs) -> AbstractScraper:
    """
    Convenience function to create a scraper.
    
    Delegates to ScraperFactory.create_scraper() for backward compatibility
    and simpler API usage.
    
    Args:
        source_type: The source type to create a scraper for
        **kwargs: Additional arguments to pass to the scraper constructor
        
    Returns:
        An instance of the appropriate scraper class
    """
    return ScraperFactory.create_scraper(source_type, **kwargs)
