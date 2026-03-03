"""
UPSC Ranking Strategy for civil services examination.

This module implements a ranking strategy optimized for UPSC (Union Public
Service Commission) civil services examination, focusing on analytical depth,
source credibility, and syllabus alignment.
"""

from typing import Dict, List
from app.services.ranking.abstract_ranking_strategy import (
    AbstractRankingStrategy,
    ArticleMetadata,
    RankingResult
)


class UPSCRankingStrategy(AbstractRankingStrategy):
    """
    Ranking strategy optimized for UPSC civil services examination.
    
    This strategy prioritizes:
    - Analytical depth and nuanced understanding
    - High-credibility sources (PIB, government sources)
    - Syllabus-aligned categories (Polity, IR, Economy)
    - Content suitable for both Prelims and Mains preparation
    
    Inherits from AbstractRankingStrategy, demonstrating the Strategy pattern
    and following the Open/Closed Principle.
    """
    
    # Priority categories for UPSC (in order of importance)
    PRIORITY_CATEGORIES = [
        "Polity",
        "International Relations",
        "Economy",
        "Environment & Ecology",
        "Science & Tech",
        "Defence & Security",
        "Government Schemes",
        "Social Issues"
    ]
    
    # Default weights for scoring factors (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        "category_relevance": 0.25,
        "content_depth": 0.25,
        "source_credibility": 0.20,
        "freshness": 0.15,
        "content_length": 0.15
    }
    
    # High-credibility sources for UPSC preparation
    CREDIBLE_SOURCES = {
        "pib": 1.0,              # Press Information Bureau - highest credibility
        "government_schemes": 0.95,  # Official government portals
        "youtube": 0.75          # YouTube channels - varies by channel
    }
    
    # Keywords indicating analytical depth
    ANALYTICAL_KEYWORDS = [
        "analysis", "implications", "impact", "significance", "perspective",
        "challenges", "opportunities", "reforms", "policy", "governance",
        "constitutional", "judicial", "legislative", "executive", "federal",
        "bilateral", "multilateral", "geopolitical", "strategic", "economic",
        "sustainable", "development", "welfare", "rights", "justice"
    ]
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize UPSC ranking strategy.
        
        Args:
            weights: Optional custom weights (uses DEFAULT_WEIGHTS if None)
        """
        super().__init__(
            exam_type="UPSC",
            weights=weights or self.DEFAULT_WEIGHTS
        )
    
    def calculate_score(
        self, 
        content: str, 
        metadata: ArticleMetadata
    ) -> RankingResult:
        """
        Calculate UPSC relevance score for an article.
        
        Implements the abstract method from AbstractRankingStrategy,
        demonstrating polymorphism and the Liskov Substitution Principle.
        
        Args:
            content: Article content text
            metadata: Article metadata for scoring
            
        Returns:
            RankingResult with score (0.0-10.0), reasoning, and factor breakdown
        """
        # Calculate individual factor scores
        factors = {}
        
        # 1. Category relevance (25%)
        factors["category_relevance"] = self._calculate_category_relevance(
            metadata.category,
            self.PRIORITY_CATEGORIES
        )
        
        # 2. Content depth (25%)
        factors["content_depth"] = self._calculate_content_depth(content)
        
        # 3. Source credibility (20%)
        factors["source_credibility"] = self._calculate_source_credibility(
            metadata.source_type
        )
        
        # 4. Freshness (15%)
        factors["freshness"] = self._calculate_freshness_score(
            metadata.published_at
        )
        
        # 5. Content length (15%)
        factors["content_length"] = self._calculate_content_length_score(
            metadata.content_length
        )
        
        # Calculate weighted score
        raw_score = sum(
            factors[factor] * self._weights[factor]
            for factor in factors
        )
        
        # Normalize to 0.0-10.0 scale
        final_score = self._normalize_score(raw_score)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(factors, metadata)
        
        return RankingResult(
            score=final_score,
            reasoning=reasoning,
            factors=factors
        )
    
    def _calculate_content_depth(self, content: str) -> float:
        """
        Calculate analytical depth score for UPSC preparation.
        
        UPSC requires deep analytical understanding, not just factual recall.
        This method scores content based on presence of analytical keywords
        and content structure.
        
        Args:
            content: Article content text
            
        Returns:
            Score from 0.0 to 1.0 (higher = more analytical depth)
        """
        if not content:
            return 0.0
        
        content_lower = content.lower()
        
        # Count analytical keywords
        keyword_count = sum(
            1 for keyword in self.ANALYTICAL_KEYWORDS
            if keyword in content_lower
        )
        
        # Normalize keyword count (5+ keywords = full score)
        keyword_score = min(1.0, keyword_count / 5.0)
        
        # Check for multi-perspective content (indicates depth)
        perspective_indicators = [
            "however", "on the other hand", "alternatively", "conversely",
            "in contrast", "meanwhile", "furthermore", "moreover"
        ]
        perspective_count = sum(
            1 for indicator in perspective_indicators
            if indicator in content_lower
        )
        perspective_score = min(1.0, perspective_count / 3.0)
        
        # Check for question-answer format (good for exam prep)
        has_questions = "?" in content
        question_score = 0.2 if has_questions else 0.0
        
        # Weighted combination
        depth_score = (
            keyword_score * 0.5 +
            perspective_score * 0.3 +
            question_score * 0.2
        )
        
        return min(1.0, depth_score)
    
    def _calculate_source_credibility(self, source_type: str) -> float:
        """
        Calculate source credibility score for UPSC preparation.
        
        UPSC values authentic, official sources. PIB and government sources
        receive highest credibility scores.
        
        Args:
            source_type: Type of source (youtube, pib, government_schemes)
            
        Returns:
            Score from 0.0 to 1.0 (higher = more credible)
        """
        return self.CREDIBLE_SOURCES.get(source_type, 0.5)
    
    def _generate_reasoning(
        self, 
        factors: Dict[str, float],
        metadata: ArticleMetadata
    ) -> str:
        """
        Generate human-readable reasoning for the score.
        
        Provides transparency and explainability for the ranking decision,
        which is important for users to understand why content was prioritized.
        
        Args:
            factors: Dictionary of factor scores
            metadata: Article metadata
            
        Returns:
            Reasoning text explaining the score
        """
        # Identify strongest and weakest factors
        sorted_factors = sorted(
            factors.items(),
            key=lambda x: x[1],
            reverse=True
        )
        strongest = sorted_factors[0]
        weakest = sorted_factors[-1]
        
        # Build reasoning
        reasoning_parts = []
        
        # Category relevance
        if metadata.category in self.PRIORITY_CATEGORIES[:3]:
            reasoning_parts.append(
                f"High-priority category '{metadata.category}' for UPSC"
            )
        else:
            reasoning_parts.append(
                f"Category '{metadata.category}' is moderately relevant"
            )
        
        # Content depth
        if factors["content_depth"] >= 0.7:
            reasoning_parts.append("Strong analytical depth")
        elif factors["content_depth"] >= 0.4:
            reasoning_parts.append("Moderate analytical content")
        else:
            reasoning_parts.append("Limited analytical depth")
        
        # Source credibility
        if factors["source_credibility"] >= 0.9:
            reasoning_parts.append("Highly credible official source")
        elif factors["source_credibility"] >= 0.7:
            reasoning_parts.append("Credible source")
        else:
            reasoning_parts.append("Moderate source credibility")
        
        # Freshness
        if factors["freshness"] >= 0.8:
            reasoning_parts.append("Very recent content")
        elif factors["freshness"] >= 0.5:
            reasoning_parts.append("Recent content")
        else:
            reasoning_parts.append("Older content")
        
        return ". ".join(reasoning_parts) + "."
