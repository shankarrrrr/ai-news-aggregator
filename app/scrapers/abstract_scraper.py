"""
Abstract base class for content scrapers.

This module implements the Template Method pattern, defining the interface
and common behavior for all content scrapers in the system.
"""

from abc import ABC, abstractmethod
from typing import List, Callable, Any
from datetime import datetime
import time
import random
import logging
from pydantic import BaseModel, Field, HttpUrl
from ..exceptions import TransientError, PermanentError, NetworkError


class ScrapedContent(BaseModel):
    """
    Data model for scraped content.
    
    Attributes:
        title: Content title
        content: Main content text
        url: Source URL
        published_at: Publication timestamp
        source_type: Type of source (youtube, pib, government_schemes)
        metadata: Additional metadata as key-value pairs
    """
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    url: str
    published_at: datetime
    source_type: str
    metadata: dict = Field(default_factory=dict)


class ScraperException(Exception):
    """Exception raised by scrapers during content fetching."""
    pass


class AbstractScraper(ABC):
    """
    Abstract base class for all content scrapers.
    
    Implements the Template Method pattern where the scraping algorithm
    structure is defined, but specific steps are implemented by subclasses.
    This design follows the Open/Closed Principle - open for extension
    (new scrapers), closed for modification (base class remains stable).
    
    Attributes:
        _source_name (str): Name of the content source (private, encapsulated)
        _base_url (str): Base URL for the source (private, encapsulated)
        _timeout (int): Request timeout in seconds (private, encapsulated)
    """
    
    def __init__(self, source_name: str, base_url: str, timeout: int = 30):
        """
        Initialize the scraper with common configuration.
        
        Args:
            source_name: Human-readable name of the source
            base_url: Base URL for API or website
            timeout: Request timeout in seconds (default: 30)
        """
        self._source_name = source_name
        self._base_url = base_url
        self._timeout = timeout
    
    @property
    def source_name(self) -> str:
        """
        Get the source name (encapsulation via property accessor).
        
        Returns:
            The source name
        """
        return self._source_name
    
    @property
    def base_url(self) -> str:
        """
        Get the base URL (encapsulation via property accessor).
        
        Returns:
            The base URL
        """
        return self._base_url
    
    @property
    def timeout(self) -> int:
        """
        Get the timeout value (encapsulation via property accessor).
        
        Returns:
            The timeout in seconds
        """
        return self._timeout
    
    @abstractmethod
    def scrape(self, hours: int = 24) -> List[ScrapedContent]:
        """
        Scrape content from the source.
        
        This abstract method must be implemented by all concrete scrapers,
        enforcing the Liskov Substitution Principle - all subclasses must
        provide this functionality and be substitutable for the base class.
        
        Args:
            hours: Number of hours to look back for content (default: 24)
            
        Returns:
            List of scraped content items
            
        Raises:
            ScraperException: If scraping fails
        """
        pass
    
    def validate_content(self, content: ScrapedContent) -> bool:
        """
        Validate scraped content meets minimum requirements.
        
        Common validation logic shared across all scrapers to avoid
        code duplication (DRY principle).
        
        Args:
            content: Content to validate
            
        Returns:
            True if valid, False otherwise
        """
        return (
            len(content.title) > 0 and
            len(content.content) > 50 and
            content.url.startswith('http')
        )
    
    def scrape_with_retry(
        self, 
        hours: int = 24, 
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ) -> List[ScrapedContent]:
        """
        Scrape content with exponential backoff retry logic.
        
        This method wraps the abstract scrape() method with retry logic
        for handling transient errors like network timeouts and API rate limits.
        
        Args:
            hours: Number of hours to look back for content
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            
        Returns:
            List of scraped content items
            
        Raises:
            PermanentError: If error is not retryable
            TransientError: If all retries are exhausted
        """
        logger = logging.getLogger(__name__)
        
        for attempt in range(max_retries + 1):
            try:
                self._log_scrape_start(hours)
                result = self.scrape(hours)
                self._log_scrape_complete(len(result))
                return result
                
            except PermanentError:
                # Don't retry permanent errors
                logger.error(f"Permanent error in {self._source_name}, not retrying")
                raise
                
            except TransientError as e:
                if attempt == max_retries:
                    logger.error(
                        f"All {max_retries} retry attempts failed for {self._source_name}"
                    )
                    raise
                
                # Calculate delay with exponential backoff and jitter
                delay = min(
                    base_delay * (2 ** attempt) + random.uniform(0, 1),
                    max_delay
                )
                
                # Use retry_after from exception if provided
                if hasattr(e, 'retry_after') and e.retry_after:
                    delay = max(delay, e.retry_after)
                
                logger.warning(
                    f"Transient error in {self._source_name} "
                    f"(attempt {attempt + 1}/{max_retries + 1}): {str(e)}. "
                    f"Retrying in {delay:.1f} seconds"
                )
                
                time.sleep(delay)
                
            except Exception as e:
                # Convert unknown exceptions to transient errors for retry
                logger.warning(
                    f"Unknown error in {self._source_name}, treating as transient: {str(e)}"
                )
                
                if attempt == max_retries:
                    raise TransientError(
                        f"Scraping failed after {max_retries} retries: {str(e)}",
                        cause=e
                    )
                
                delay = min(
                    base_delay * (2 ** attempt) + random.uniform(0, 1),
                    max_delay
                )
                
                logger.warning(
                    f"Retrying {self._source_name} in {delay:.1f} seconds "
                    f"(attempt {attempt + 1}/{max_retries + 1})"
                )
                
                time.sleep(delay)
        
        # This should never be reached, but just in case
        raise TransientError(f"Unexpected error: retry loop completed without result")
    
    def _execute_with_timeout(
        self, 
        func: Callable[[], Any], 
        timeout_seconds: int = None
    ) -> Any:
        """
        Execute a function with timeout handling.
        
        Args:
            func: Function to execute
            timeout_seconds: Timeout in seconds (uses self._timeout if None)
            
        Returns:
            Function result
            
        Raises:
            TransientError: If timeout occurs
        """
        import signal
        
        timeout = timeout_seconds or self._timeout
        
        def timeout_handler(signum, frame):
            raise TransientError(f"Operation timed out after {timeout} seconds")
        
        # Set up timeout signal
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = func()
            signal.alarm(0)  # Cancel timeout
            return result
        except TransientError:
            raise
        except Exception as e:
            signal.alarm(0)  # Cancel timeout
            raise NetworkError(f"Network operation failed: {str(e)}", cause=e)
        finally:
            signal.signal(signal.SIGALRM, old_handler)
    
    def _handle_network_error(self, error: Exception) -> None:
        """
        Common error handling for network failures.
        
        Provides consistent error logging across all scrapers and
        converts exceptions to appropriate error types.
        Private method (prefixed with _) for internal use only.
        
        Args:
            error: The exception that occurred
            
        Raises:
            TransientError: For retryable network errors
            PermanentError: For non-retryable errors
        """
        logger = logging.getLogger(__name__)
        
        # Log the error with context
        logger.error(
            f"Network error in {self._source_name}: {str(error)}",
            exc_info=True,
            extra={
                'source_name': self._source_name,
                'base_url': self._base_url,
                'error_type': type(error).__name__
            }
        )
        
        # Convert to appropriate exception type
        if isinstance(error, (ConnectionError, TimeoutError)):
            raise TransientError(f"Network connection failed: {str(error)}", cause=error)
        elif isinstance(error, PermissionError):
            raise PermanentError(f"Permission denied: {str(error)}", cause=error)
        else:
            # Default to transient for unknown network errors
            raise TransientError(f"Network error: {str(error)}", cause=error)
    
    def _log_scrape_start(self, hours: int) -> None:
        """
        Log the start of a scraping operation.
        
        Args:
            hours: Number of hours being scraped
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Starting scrape for {self._source_name} "
            f"(lookback: {hours} hours)"
        )
    
    def _log_scrape_complete(self, count: int) -> None:
        """
        Log the completion of a scraping operation.
        
        Args:
            count: Number of items scraped
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Completed scrape for {self._source_name}: "
            f"{count} items retrieved"
        )
