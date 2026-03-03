"""
SSC Ranking Strategy for Staff Selection Commission examinations.

This module implements a ranking strategy optimized for SSC (Staff Selection
Commission) examinations, focusing on factual density, clarity, and
objective-type question suitability.
"""

from typing import Dict, List
import re
from app.services.ranking.abstract_ranking_strategy import (
    AbstractRankingStrategy,
    ArticleMetadata,
    RankingResult
)


class SSCRankingStrategy(AbstractRankingStrategy):
    """
    Ranking strategy optimized for SSC examinations.
    
    This strategy prioritizes:
    - Factual density (dates, numbers, names, places)
    - Clear, concise content suitable for objective questions
    - Current affairs relevance
    - Categories aligned with SSC syllabus
    
    SSC exams are primarily objective (MCQ-based), so content with clear
    facts and figures is more valuable than analytical essays.
    
    Inherits from AbstractRankingStrategy, demonstrating the Strategy pattern.
    """
    
    # Priority categories for SSC (in order of importance)
    PRIORITY_CATEGORIES = [
        "Economy",
        "Polity",
        "Science & Tech",
        "Government Schemes",
        "Social Issues",
        "Environment & Ecology",
        "International Relations",
        "Defence & Security"
    ]
    
    # Default weights for scoring factors (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        "category_relevance": 0.25,
        "factual_density": 0.30,      # Higher weight for facts
        "source_credibility": 0.15,
        "freshness": 0.20,             # Higher weight for current affairs
        "content_length": 0.10
    }
    
    # High-credibility sources for SSC preparation
    CREDIBLE_SOURCES = {
        "pib": 1.0,                    # Official government source
        "government_schemes": 0.95,    # Official scheme information
        "youtube": 0.70                # Educational channels
    }
    
    # Patterns for identifying factual content
    FACTUAL_PATTERNS = {
        "dates": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        "numbers": r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:crore|lakh|million|billion|thousand|percent|%|km|kg|meter|litre)?\b',
        "proper_nouns": r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
        "years": r'\b(?:19|20)\d{2}\b'
    }
    
    # Keywords indicating factual content
    FACTUAL_KEYWORDS = [
        "launched", "announced", "appointed", "inaugurated", "signed",
        "established", "founded", "located", "capital", "headquarters",
        "minister", "president", "chairman", "director", "secretary",
        "scheme", "program", "initiative", "project", "mission",
        "budget", "allocation", "investment", "funding", "revenue",
        "agreement", "treaty", "memorandum", "protocol", "convention"
    ]
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize SSC ranking strategy.
        
        Args:
            weights: Optional custom weights (uses DEFAULT_WEIGHTS if None)
        """
        super().__init__(
            exam_type="SSC",
            weights=weights or self.DEFAULT_WEIGHTS
        )
    
    def calculate_score(
        self, 
        content: str, 
        metadata: ArticleMetadata
    ) -> RankingResult:
        """
        Calculate SSC relevance score for an article.
        
        Implements the abstract method from AbstractRankingStrategy.
        
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
        
        # 2. Factual density (30%) - most important for SSC
        factors["factual_density"] = self._calculate_factual_density(content)
        
        # 3. Source credibility (15%)
        factors["source_credibility"] = self._calculate_source_credibility(
            metadata.source_type
        )
        
        # 4. Freshness (20%) - current affairs are crucial
        factors["freshness"] = self._calculate_freshness_score(
            metadata.published_at
        )
        
        # 5. Content length (10%)
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
    
    def _calculate_factual_density(self, content: str) -> float:
        """
        Calculate factual density score for SSC preparation.
        
        SSC exams are objective and fact-based. Content with more dates,
        numbers, names, and specific facts scores higher.
        
        Args:
            content: Article content text
            
        Returns:
            Score from 0.0 to 1.0 (higher = more factual content)
        """
        if not content:
            return 0.0
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        # Count factual patterns
        pattern_counts = {}
        for pattern_name, pattern in self.FACTUAL_PATTERNS.items():
            matches = re.findall(pattern, content)
            pattern_counts[pattern_name] = len(matches)
        
        # Count factual keywords
        keyword_count = sum(
            1 for keyword in self.FACTUAL_KEYWORDS
            if keyword in content_lower
        )
        
        # Calculate density scores
        # Dates: 1+ per 100 words is good
        date_density = min(1.0, pattern_counts["dates"] / (word_count / 100))
        
        # Numbers: 3+ per 100 words is good
        number_density = min(1.0, pattern_counts["numbers"] / (word_count / 100) / 3)
        
        # Proper nouns: 5+ per 100 words is good
        noun_density = min(1.0, pattern_counts["proper_nouns"] / (word_count / 100) / 5)
        
        # Keywords: 3+ per 100 words is good
        keyword_density = min(1.0, keyword_count / (word_count / 100) / 3)
        
        # Weighted combination
        factual_score = (
            date_density * 0.25 +
            number_density * 0.25 +
            noun_density * 0.25 +
            keyword_density * 0.25
        )
        
        return min(1.0, factual_score)
    
    def _calculate_source_credibility(self, source_type: str) -> float:
        """
        Calculate source credibility score for SSC preparation.
        
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
        
        Args:
            factors: Dictionary of factor scores
            metadata: Article metadata
            
        Returns:
            Reasoning text explaining the score
        """
        reasoning_parts = []
        
        # Category relevance
        if metadata.category in self.PRIORITY_CATEGORIES[:3]:
            reasoning_parts.append(
                f"High-priority category '{metadata.category}' for SSC"
            )
        else:
            reasoning_parts.append(
                f"Category '{metadata.category}' is relevant for SSC"
            )
        
        # Factual density
        if factors["factual_density"] >= 0.7:
            reasoning_parts.append("High factual density with specific data")
        elif factors["factual_density"] >= 0.4:
            reasoning_parts.append("Moderate factual content")
        else:
            reasoning_parts.append("Limited factual information")
        
        # Source credibility
        if factors["source_credibility"] >= 0.9:
            reasoning_parts.append("Official government source")
        elif factors["source_credibility"] >= 0.7:
            reasoning_parts.append("Credible source")
        else:
            reasoning_parts.append("Standard source credibility")
        
        # Freshness
        if factors["freshness"] >= 0.8:
            reasoning_parts.append("Very recent for current affairs")
        elif factors["freshness"] >= 0.5:
            reasoning_parts.append("Recent content")
        else:
            reasoning_parts.append("Older content, less relevant for current affairs")
        
        # Content length
        if factors["content_length"] >= 0.8:
            reasoning_parts.append("Appropriate length for SSC preparation")
        
        return ". ".join(reasoning_parts) + "."
