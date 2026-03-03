"""
Configuration for Competitive Exam Intelligence System.

This module contains all configuration constants for the exam intelligence
system including exam categories, source URLs, and ranking weights.
"""

import os
from typing import Dict, List


# ============================================================================
# EXAM CATEGORIES
# ============================================================================

EXAM_CATEGORIES: List[str] = [
    "Polity",
    "Economy",
    "International Relations",
    "Science & Tech",
    "Environment & Ecology",
    "Defence & Security",
    "Government Schemes",
    "Social Issues"
]


# ============================================================================
# YOUTUBE EXAM PREPARATION CHANNELS
# ============================================================================

YOUTUBE_CHANNELS: List[str] = [
    "UCYRBFLkuZ8ZAfwz7ayGGvZQ",  # StudyIQ IAS
    "UCnvC2wLZOiKdFkM8Ml4EzQg",  # Drishti IAS
    "UCZ8QY-RF48rE3LJRgdD0kVQ",  # Vision IAS
    "UCawZsQWqfGSbCI5yjkdVkTA",  # OnlyIAS
    "UCOEVlIHEsILuTV_Ix8dDW5A",  # Insights IAS
    "UC3cBGxYNVQURTNdvIjn05pA",  # PIB India Official
    "UCawZsQWqfGSbCI5yjkdVkTC",  # Sansad TV
    "UCawZsQWqfGSbCI5yjkdVkTD",  # Vajiram & Ravi
    "UCawZsQWqfGSbCI5yjkdVkTE",  # Adda247
    "UCawZsQWqfGSbCI5yjkdVkTF",  # BYJU'S Exam Prep
    "UCawZsQWqfGSbCI5yjkdVkTG",  # Unacademy UPSC
]


# ============================================================================
# PIB (PRESS INFORMATION BUREAU) CONFIGURATION
# ============================================================================

PIB_BASE_URL: str = "https://pib.gov.in"
PIB_CATEGORIES: List[str] = [
    "Government Policies",
    "Economy",
    "Defence",
    "International Relations",
    "Science & Technology",
    "Environment",
    "Social Welfare"
]


# ============================================================================
# GOVERNMENT SCHEMES PORTALS
# ============================================================================

GOVERNMENT_SCHEME_PORTALS: List[Dict[str, str]] = [
    {
        "name": "MyScheme",
        "url": "https://www.myscheme.gov.in",
        "description": "National portal for government schemes"
    },
    {
        "name": "India.gov.in",
        "url": "https://www.india.gov.in/topics/social-welfare",
        "description": "National portal - social welfare schemes"
    },
    {
        "name": "Digital India",
        "url": "https://www.digitalindia.gov.in",
        "description": "Digital India initiatives"
    }
]


# ============================================================================
# RANKING STRATEGY WEIGHTS
# ============================================================================

# UPSC Ranking Weights (Civil Services Examination)
UPSC_RANKING_WEIGHTS: Dict[str, float] = {
    "category_relevance": 0.30,  # Category match with UPSC syllabus
    "content_depth": 0.25,       # Analytical depth of content
    "freshness": 0.20,           # Recency of content
    "source_credibility": 0.15,  # Reliability of source
    "content_length": 0.10       # Optimal content length
}

# SSC Ranking Weights (Staff Selection Commission)
SSC_RANKING_WEIGHTS: Dict[str, float] = {
    "category_relevance": 0.35,  # Category match with SSC syllabus
    "factual_density": 0.25,     # Density of factual information
    "freshness": 0.20,           # Recency of content
    "source_credibility": 0.10,  # Reliability of source
    "content_length": 0.10       # Optimal content length
}

# Banking Exam Ranking Weights (IBPS, SBI, RBI)
BANKING_RANKING_WEIGHTS: Dict[str, float] = {
    "category_relevance": 0.30,  # Category match with banking syllabus
    "banking_keywords": 0.25,    # Banking-specific terminology
    "freshness": 0.25,           # Recency of content (important for banking)
    "source_credibility": 0.10,  # Reliability of source
    "content_length": 0.10       # Optimal content length
}


# ============================================================================
# GEMINI API CONFIGURATION
# ============================================================================

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = "gemini-1.5-flash"
GEMINI_TEMPERATURE: float = 0.7
GEMINI_MAX_TOKENS: int = 2048


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_URL: str = os.getenv("DATABASE_URL", "")


# ============================================================================
# SCRAPING CONFIGURATION
# ============================================================================

DEFAULT_SCRAPE_HOURS: int = 24  # Default lookback period
DEFAULT_TOP_N: int = 10         # Default number of top articles to select
SCRAPER_TIMEOUT: int = 30       # Request timeout in seconds


# ============================================================================
# ENABLE/DISABLE SOURCES
# ============================================================================

ENABLE_YOUTUBE_SCRAPER: bool = True
ENABLE_PIB_SCRAPER: bool = True
ENABLE_GOVERNMENT_SCHEMES_SCRAPER: bool = True

# Legacy AI news scrapers (disabled for exam system)
ENABLE_OPENAI_SCRAPER: bool = False
ENABLE_ANTHROPIC_SCRAPER: bool = False


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_configuration() -> None:
    """
    Validate configuration on startup.
    
    Ensures all required environment variables are set and configuration
    values are valid. Fails fast with clear error messages.
    
    Raises:
        ValueError: If configuration is invalid
        EnvironmentError: If required environment variables are missing
    """
    errors = []
    
    # Validate required environment variables
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY environment variable is not set")
    
    if not DATABASE_URL:
        errors.append("DATABASE_URL environment variable is not set")
    
    # Validate YouTube channel IDs format
    for channel_id in YOUTUBE_CHANNELS:
        if not channel_id or len(channel_id) != 24:
            errors.append(f"Invalid YouTube channel ID format: {channel_id}")
    
    # Validate ranking weights sum to 1.0
    for exam_type, weights in [
        ("UPSC", UPSC_RANKING_WEIGHTS),
        ("SSC", SSC_RANKING_WEIGHTS),
        ("Banking", BANKING_RANKING_WEIGHTS)
    ]:
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):
            errors.append(
                f"{exam_type} ranking weights must sum to 1.0, got {total}"
            )
    
    # Validate exam categories
    if len(EXAM_CATEGORIES) != 8:
        errors.append(
            f"Expected 8 exam categories, got {len(EXAM_CATEGORIES)}"
        )
    
    # Raise all errors at once
    if errors:
        error_message = "Configuration validation failed:\n" + "\n".join(
            f"  - {error}" for error in errors
        )
        raise EnvironmentError(error_message)


# ============================================================================
# CONFIGURATION SUMMARY
# ============================================================================

def get_configuration_summary() -> Dict[str, any]:
    """
    Get a summary of current configuration.
    
    Returns:
        Dictionary containing configuration summary
    """
    return {
        "exam_categories": len(EXAM_CATEGORIES),
        "youtube_channels": len(YOUTUBE_CHANNELS),
        "pib_categories": len(PIB_CATEGORIES),
        "government_portals": len(GOVERNMENT_SCHEME_PORTALS),
        "gemini_model": GEMINI_MODEL,
        "database_configured": bool(DATABASE_URL),
        "enabled_scrapers": {
            "youtube": ENABLE_YOUTUBE_SCRAPER,
            "pib": ENABLE_PIB_SCRAPER,
            "government_schemes": ENABLE_GOVERNMENT_SCHEMES_SCRAPER
        }
    }

