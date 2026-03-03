"""
Custom exception classes for the Competitive Exam Intelligence System.

This module defines exception hierarchies for different types of errors,
enabling proper error handling and recovery strategies.
"""

from typing import Optional


class SystemException(Exception):
    """Base exception for all system errors."""
    
    def __init__(self, message: str, cause: Optional[Exception] = None):
        """
        Initialize system exception.
        
        Args:
            message: Error message
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.cause = cause


class TransientError(SystemException):
    """
    Exception for temporary errors that may succeed on retry.
    
    Examples: Network timeouts, API rate limits, temporary service unavailability
    """
    
    def __init__(self, message: str, retry_after: Optional[int] = None, cause: Optional[Exception] = None):
        """
        Initialize transient error.
        
        Args:
            message: Error message
            retry_after: Suggested retry delay in seconds
            cause: Original exception that caused this error
        """
        super().__init__(message, cause)
        self.retry_after = retry_after


class PermanentError(SystemException):
    """
    Exception for permanent errors that will not succeed on retry.
    
    Examples: Invalid API keys, malformed data, configuration errors
    """
    pass


class NetworkError(TransientError):
    """Network-related errors that may be temporary."""
    pass


class APIError(SystemException):
    """Base class for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, cause: Optional[Exception] = None):
        """
        Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code if applicable
            cause: Original exception that caused this error
        """
        super().__init__(message, cause)
        self.status_code = status_code


class APIRateLimitError(TransientError):
    """API rate limit exceeded - should retry with backoff."""
    pass


class APIQuotaExceededError(PermanentError):
    """API quota exceeded - will not succeed until quota resets."""
    pass


class ConfigurationError(PermanentError):
    """Configuration-related errors."""
    pass


class DatabaseError(SystemException):
    """Database-related errors."""
    pass


class ValidationError(PermanentError):
    """Data validation errors."""
    pass