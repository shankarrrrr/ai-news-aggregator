"""
Configuration validation for the Competitive Exam Intelligence System.

This module provides comprehensive validation of system configuration including
environment variables, API keys, database connections, and business logic constraints.

The validator follows the "fail fast" principle - detecting configuration issues
at startup rather than during runtime execution.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration constants
from app.config import (
    EXAM_CATEGORIES,
    YOUTUBE_CHANNELS,
    PIB_BASE_URL,
    GOVERNMENT_SCHEME_PORTALS
)


class ConfigurationError(Exception):
    """Exception raised when configuration validation fails."""
    pass


class ConfigValidator:
    """
    Comprehensive configuration validator for the system.
    
    Validates all aspects of system configuration including:
    - Required environment variables
    - API key formats and accessibility
    - Database connection parameters
    - Business logic constraints (weights, categories, etc.)
    - External service URLs and formats
    
    Follows the Single Responsibility Principle - only responsible for validation.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the configuration validator.
        
        Args:
            logger: Optional logger instance (creates default if None)
        """
        self._logger = logger or self._create_default_logger()
        self._errors: List[str] = []
        self._warnings: List[str] = []
    
    def validate_configuration(self) -> None:
        """
        Perform comprehensive configuration validation.
        
        Validates all system configuration and raises ConfigurationError
        if any critical issues are found. Logs warnings for non-critical issues.
        
        Raises:
            ConfigurationError: If critical configuration issues are found
        """
        self._logger.info("Starting configuration validation...")
        
        # Reset error and warning lists
        self._errors.clear()
        self._warnings.clear()
        
        # Validate all configuration aspects
        self._validate_environment_variables()
        self._validate_gemini_api_key()
        self._validate_database_url()
        self._validate_youtube_channels()
        self._validate_ranking_weights()
        self._validate_exam_categories()
        self._validate_external_urls()
        
        # Report results
        self._report_validation_results()
        
        # Fail fast if critical errors found
        if self._errors:
            error_summary = f"Configuration validation failed with {len(self._errors)} error(s)"
            self._logger.error(error_summary)
            raise ConfigurationError(error_summary)
        
        self._logger.info("Configuration validation completed successfully")
    
    def _validate_environment_variables(self) -> None:
        """Validate required environment variables are present."""
        required_vars = [
            'GEMINI_API_KEY',
            'DATABASE_URL'
        ]
        
        optional_vars = [
            'SMTP_SERVER',
            'SMTP_PORT',
            'SMTP_USERNAME',
            'SMTP_PASSWORD',
            'EMAIL_FROM',
            'EMAIL_TO'
        ]
        
        # Check required variables
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                self._errors.append(f"Required environment variable '{var}' is not set")
            elif not value.strip():
                self._errors.append(f"Required environment variable '{var}' is empty")
        
        # Check optional variables (warnings only)
        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        if missing_optional:
            self._warnings.append(
                f"Optional environment variables not set: {', '.join(missing_optional)}. "
                "Email functionality may not work."
            )
    
    def _validate_gemini_api_key(self) -> None:
        """Validate Gemini API key format and basic accessibility."""
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            return  # Already handled in environment variables validation
        
        # Validate API key format (Google API keys typically start with specific patterns)
        if not self._is_valid_gemini_api_key_format(api_key):
            self._errors.append(
                "GEMINI_API_KEY does not match expected format. "
                "Ensure you're using a valid Google AI Studio API key."
            )
        
        # Test basic API accessibility (optional - can be slow)
        # Uncomment if you want to test API connectivity during validation
        # try:
        #     self._test_gemini_api_connection(api_key)
        # except Exception as e:
        #     self._warnings.append(f"Could not verify Gemini API connectivity: {str(e)}")
    
    def _validate_database_url(self) -> None:
        """Validate database URL format and components."""
        db_url = os.getenv('DATABASE_URL')
        
        if not db_url:
            return  # Already handled in environment variables validation
        
        try:
            parsed = urlparse(db_url)
            
            # Validate scheme
            if parsed.scheme not in ['postgresql', 'postgres']:
                self._errors.append(
                    f"Database URL scheme '{parsed.scheme}' is not supported. "
                    "Use 'postgresql' or 'postgres'."
                )
            
            # Validate hostname
            if not parsed.hostname:
                self._errors.append("Database URL is missing hostname")
            
            # Validate port (if specified)
            if parsed.port and (parsed.port < 1 or parsed.port > 65535):
                self._errors.append(f"Database port {parsed.port} is invalid")
            
            # Validate database name
            if not parsed.path or parsed.path == '/':
                self._errors.append("Database URL is missing database name")
            
        except Exception as e:
            self._errors.append(f"Invalid database URL format: {str(e)}")
    
    def _validate_youtube_channels(self) -> None:
        """Validate YouTube channel IDs format."""
        if not YOUTUBE_CHANNELS:
            self._warnings.append("No YouTube channels configured")
            return
        
        # YouTube channel ID format: 24 characters, alphanumeric + underscore/hyphen
        channel_id_pattern = re.compile(r'^[a-zA-Z0-9_-]{24}$')
        
        invalid_channels = []
        for channel_id in YOUTUBE_CHANNELS:
            if not isinstance(channel_id, str):
                invalid_channels.append(f"{channel_id} (not a string)")
            elif not channel_id_pattern.match(channel_id):
                invalid_channels.append(f"{channel_id} (invalid format)")
        
        if invalid_channels:
            self._errors.append(
                f"Invalid YouTube channel IDs found: {', '.join(invalid_channels)}. "
                "Channel IDs should be 24-character alphanumeric strings."
            )
    
    def _validate_ranking_weights(self) -> None:
        """Validate ranking strategy weights sum to 1.0."""
        # Import ranking strategies to check their default weights
        try:
            from app.services.ranking.upsc_ranking_strategy import UPSCRankingStrategy
            from app.services.ranking.ssc_ranking_strategy import SSCRankingStrategy
            from app.services.ranking.banking_ranking_strategy import BankingRankingStrategy
            
            strategies = [
                ("UPSC", UPSCRankingStrategy),
                ("SSC", SSCRankingStrategy),
                ("Banking", BankingRankingStrategy)
            ]
            
            for strategy_name, strategy_class in strategies:
                try:
                    # Create instance with default weights to validate
                    strategy = strategy_class()
                    # If we get here, weights are valid (constructor validates)
                except ValueError as e:
                    self._errors.append(f"{strategy_name} ranking strategy weights invalid: {str(e)}")
                except Exception as e:
                    self._warnings.append(f"Could not validate {strategy_name} strategy weights: {str(e)}")
                    
        except ImportError as e:
            self._warnings.append(f"Could not import ranking strategies for validation: {str(e)}")
    
    def _validate_exam_categories(self) -> None:
        """Validate exam categories configuration."""
        if not EXAM_CATEGORIES:
            self._errors.append("No exam categories configured")
            return
        
        if not isinstance(EXAM_CATEGORIES, list):
            self._errors.append("EXAM_CATEGORIES must be a list")
            return
        
        # Check for minimum number of categories
        if len(EXAM_CATEGORIES) < 3:
            self._warnings.append(
                f"Only {len(EXAM_CATEGORIES)} exam categories configured. "
                "Consider adding more categories for better classification."
            )
        
        # Check for duplicate categories
        if len(EXAM_CATEGORIES) != len(set(EXAM_CATEGORIES)):
            duplicates = [cat for cat in EXAM_CATEGORIES if EXAM_CATEGORIES.count(cat) > 1]
            self._errors.append(f"Duplicate exam categories found: {set(duplicates)}")
        
        # Check category names are non-empty strings
        invalid_categories = [
            cat for cat in EXAM_CATEGORIES 
            if not isinstance(cat, str) or not cat.strip()
        ]
        if invalid_categories:
            self._errors.append(f"Invalid category names: {invalid_categories}")
    
    def _validate_external_urls(self) -> None:
        """Validate external service URLs."""
        urls_to_validate = []
        
        # Add PIB URL
        if PIB_BASE_URL:
            urls_to_validate.append(("PIB", PIB_BASE_URL))
        
        # Add government scheme portal URLs
        if GOVERNMENT_SCHEME_PORTALS:
            for portal in GOVERNMENT_SCHEME_PORTALS:
                portal_name = portal.get("name", "Unknown")
                portal_url = portal.get("url", "")
                if portal_url:
                    urls_to_validate.append((f"Gov Portal ({portal_name})", portal_url))
        
        # Validate URL formats
        for service_name, url in urls_to_validate:
            if not self._is_valid_url(url):
                self._errors.append(f"Invalid URL for {service_name}: {url}")
    
    def _is_valid_gemini_api_key_format(self, api_key: str) -> bool:
        """
        Check if API key matches expected Gemini API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if format appears valid, False otherwise
        """
        # Google API keys are typically 39 characters long and alphanumeric
        # This is a basic format check, not a guarantee of validity
        if len(api_key) < 20:  # Too short
            return False
        
        if len(api_key) > 100:  # Too long
            return False
        
        # Should contain only alphanumeric characters, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
            return False
        
        return True
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if URL format is valid.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL format is valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            return all([
                parsed.scheme in ['http', 'https'],
                parsed.netloc,
                '.' in parsed.netloc  # Basic domain validation
            ])
        except Exception:
            return False
    
    def _report_validation_results(self) -> None:
        """Report validation results to logger."""
        if self._errors:
            self._logger.error(f"Configuration validation found {len(self._errors)} error(s):")
            for i, error in enumerate(self._errors, 1):
                self._logger.error(f"  {i}. {error}")
        
        if self._warnings:
            self._logger.warning(f"Configuration validation found {len(self._warnings)} warning(s):")
            for i, warning in enumerate(self._warnings, 1):
                self._logger.warning(f"  {i}. {warning}")
        
        if not self._errors and not self._warnings:
            self._logger.info("All configuration checks passed")
    
    def _create_default_logger(self) -> logging.Logger:
        """
        Create a default logger for configuration validation.
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger("config_validator")
        logger.setLevel(logging.INFO)
        
        # Create console handler if no handlers exist
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger


def validate_configuration() -> None:
    """
    Convenience function to validate system configuration.
    
    This function creates a ConfigValidator instance and runs validation.
    Use this function at application startup to ensure configuration is valid.
    
    Raises:
        ConfigurationError: If critical configuration issues are found
    """
    validator = ConfigValidator()
    validator.validate_configuration()


def get_configuration_summary() -> Dict[str, Any]:
    """
    Get a summary of current configuration for debugging/monitoring.
    
    Returns:
        Dictionary containing configuration summary (sensitive data masked)
    """
    return {
        'gemini_api_key_configured': bool(os.getenv('GEMINI_API_KEY')),
        'database_url_configured': bool(os.getenv('DATABASE_URL')),
        'email_configured': bool(os.getenv('SMTP_SERVER')),
        'youtube_channels_count': len(YOUTUBE_CHANNELS) if YOUTUBE_CHANNELS else 0,
        'exam_categories_count': len(EXAM_CATEGORIES) if EXAM_CATEGORIES else 0,
        'pib_url_configured': bool(PIB_BASE_URL),
        'gov_portals_count': len(GOVERNMENT_SCHEME_PORTALS) if GOVERNMENT_SCHEME_PORTALS else 0
    }


if __name__ == "__main__":
    """Run configuration validation as a standalone script."""
    try:
        validate_configuration()
        print("✅ Configuration validation passed")
    except ConfigurationError as e:
        print(f"❌ Configuration validation failed: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error during validation: {e}")
        exit(1)