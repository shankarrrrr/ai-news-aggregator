"""
Abstract base class for ranking strategies.

This module implements the Strategy pattern, allowing different ranking
algorithms to be used interchangeably for different exam types.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ArticleMetadata(BaseModel):
    """
    Metadata for ranking calculation.
    
    Attributes:
        category: Article category (e.g., Polity, Economy)
        source_type: Type of source (youtube, pib, government_schemes)
        published_at: Publication timestamp
        content_length: Length of content in characters
        keywords: List of extracted keywords
    """
    category: str
    source_type: str
    published_at: datetime
    content_length: int = Field(gt=0)
    keywords: List[str] = Field(default_factory=list)


class RankingResult(BaseModel):
    """
    Result of ranking calculation.
    
    Attributes:
        score: Relevance score from 0.0 to 10.0
        reasoning: Explanation of the score
        factors: Individual factor scores for transparency
    """
    score: float = Field(ge=0.0, le=10.0)
    reasoning: str
    factors: Dict[str, float] = Field(default_factory=dict)


class AbstractRankingStrategy(ABC):
    """
    Abstract base class for ranking strategies.
    
    Implements the Strategy pattern to allow different ranking algorithms
    for different exam types (UPSC, SSC, Banking, etc.). This design follows
    the Open/Closed Principle - new strategies can be added without modifying
    existing code.
    
    Attributes:
        _exam_type (str): Type of exam this strategy is for (private, encapsulated)
        _weights (Dict[str, float]): Scoring weights for factors (private, encapsulated)
    """
    
    def __init__(self, exam_type: str, weights: Dict[str, float]):
        """
        Initialize the ranking strategy.
        
        Args:
            exam_type: Type of exam (UPSC, SSC, Banking, etc.)
            weights: Dictionary of factor weights (must sum to 1.0)
            
        Raises:
            ValueError: If weights don't sum to 1.0
        """
        self._exam_type = exam_type
        self._weights = weights
        self._validate_weights()
    
    @property
    def exam_type(self) -> str:
        """
        Get the exam type for this strategy (encapsulation via property accessor).
        
        Returns:
            The exam type
        """
        return self._exam_type
    
    @property
    def weights(self) -> Dict[str, float]:
        """
        Get a copy of the weights (encapsulation via property accessor).
        
        Returns:
            Copy of the weights dictionary
        """
        return self._weights.copy()
    
    @abstractmethod
    def calculate_score(
        self, 
        content: str, 
        metadata: ArticleMetadata
    ) -> RankingResult:
        """
        Calculate relevance score for an article.
        
        This abstract method must be implemented by all concrete strategies,
        enforcing the Liskov Substitution Principle - all strategy subclasses
        must provide this functionality and be substitutable for the base class.
        
        Args:
            content: Article content text
            metadata: Article metadata for scoring
            
        Returns:
            RankingResult with score, reasoning, and factor breakdown
            
        Raises:
            ValueError: If inputs are invalid
        """
        pass
    
    def _validate_weights(self) -> None:
        """
        Validate that weights sum to 1.0.
        
        Ensures scoring consistency across all strategies.
        Private method (prefixed with _) for internal use only.
        
        Raises:
            ValueError: If weights don't sum to approximately 1.0
        """
        total = sum(self._weights.values())
        # Allow small floating point error (0.99 to 1.01)
        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"Weights must sum to 1.0, got {total}. "
                f"Weights: {self._weights}"
            )
    
    def _calculate_freshness_score(self, published_at: datetime) -> float:
        """
        Calculate freshness score based on publication date.
        
        Uses exponential decay: newer content scores higher.
        - 0 hours old: 1.0
        - 24 hours old: 0.5
        - 48 hours old: 0.25
        
        Args:
            published_at: Publication timestamp
            
        Returns:
            Score from 0.0 to 1.0 (newer = higher)
        """
        now = datetime.now(timezone.utc)
        
        # Ensure published_at is timezone-aware
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        
        age_hours = (now - published_at).total_seconds() / 3600
        
        # Exponential decay with half-life of 24 hours
        # Formula: 2^(-age_hours / 24)
        freshness = 2 ** (-age_hours / 24)
        
        # Clamp to [0.0, 1.0] range
        return max(0.0, min(1.0, freshness))
    
    def _calculate_category_relevance(
        self, 
        category: str, 
        priority_categories: List[str]
    ) -> float:
        """
        Calculate category relevance score.
        
        Priority categories receive higher scores, with the first priority
        receiving the highest score.
        
        Args:
            category: Article category
            priority_categories: List of high-priority categories for this exam
            
        Returns:
            Score from 0.0 to 1.0
        """
        if category in priority_categories:
            # Higher score for priority categories
            # First priority = 1.0, second = 0.9, third = 0.8, etc.
            index = priority_categories.index(category)
            return max(0.5, 1.0 - (index * 0.1))
        
        # Default score for non-priority categories
        return 0.5
    
    def _calculate_content_length_score(self, content_length: int) -> float:
        """
        Calculate score based on content length.
        
        Optimal length is 500-2000 characters. Too short or too long
        receives lower scores.
        
        Args:
            content_length: Length of content in characters
            
        Returns:
            Score from 0.0 to 1.0
        """
        if content_length < 100:
            # Too short - likely incomplete
            return 0.2
        elif content_length < 500:
            # Short but acceptable
            return 0.6 + (content_length - 100) / 400 * 0.2
        elif content_length <= 2000:
            # Optimal range
            return 1.0
        elif content_length <= 5000:
            # Long but acceptable
            return 1.0 - (content_length - 2000) / 3000 * 0.3
        else:
            # Too long - may be overwhelming
            return 0.5
    
    def _normalize_score(self, raw_score: float) -> float:
        """
        Normalize a raw score to the 0.0-10.0 range.
        
        Args:
            raw_score: Raw score (typically 0.0-1.0)
            
        Returns:
            Normalized score from 0.0 to 10.0
        """
        normalized = raw_score * 10.0
        return max(0.0, min(10.0, normalized))
    
    def _log_scoring(self, article_id: str, score: float) -> None:
        """
        Log scoring operation for monitoring.
        
        Args:
            article_id: Identifier for the article
            score: Calculated score
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(
            f"{self.__class__.__name__} scored article {article_id}: {score:.2f}"
        )
