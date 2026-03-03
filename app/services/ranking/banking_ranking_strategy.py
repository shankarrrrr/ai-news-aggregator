"""
Banking Ranking Strategy for banking sector examinations.

This module implements a ranking strategy optimized for banking examinations
(IBPS, SBI, RBI, etc.), focusing on economy, banking sector news, government
schemes, and financial literacy content.
"""

from typing import Dict, List
import re
from app.services.ranking.abstract_ranking_strategy import (
    AbstractRankingStrategy,
    ArticleMetadata,
    RankingResult
)


class BankingRankingStrategy(AbstractRankingStrategy):
    """
    Ranking strategy optimized for banking examinations.
    
    This strategy prioritizes:
    - Economy and banking sector news
    - Government schemes (especially financial inclusion)
    - Banking-specific keywords and terminology
    - Financial literacy and awareness content
    
    Banking exams (IBPS, SBI, RBI) have a strong focus on current affairs
    related to banking, economy, and government financial schemes.
    
    Inherits from AbstractRankingStrategy, demonstrating the Strategy pattern.
    """
    
    # Priority categories for Banking exams (in order of importance)
    PRIORITY_CATEGORIES = [
        "Economy",
        "Government Schemes",
        "Polity",
        "International Relations",
        "Science & Tech",
        "Social Issues",
        "Environment & Ecology",
        "Defence & Security"
    ]
    
    # Default weights for scoring factors (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        "category_relevance": 0.20,
        "banking_keyword_score": 0.35,  # Highest weight for banking relevance
        "source_credibility": 0.15,
        "freshness": 0.20,
        "content_length": 0.10
    }
    
    # High-credibility sources for Banking preparation
    CREDIBLE_SOURCES = {
        "pib": 1.0,                    # Official government announcements
        "government_schemes": 1.0,     # Financial schemes are crucial
        "youtube": 0.70                # Banking education channels
    }
    
    # Banking-specific keywords (categorized for better scoring)
    BANKING_KEYWORDS = {
        # Core banking terms
        "core_banking": [
            "bank", "banking", "rbi", "reserve bank", "central bank",
            "commercial bank", "cooperative bank", "nbfc", "payment bank",
            "small finance bank", "regional rural bank", "rrb",
            "monetary policy", "repo rate", "reverse repo", "crr", "slr",
            "base rate", "mclr", "interest rate", "inflation", "deflation",
            "npa", "non-performing asset", "bad loan", "credit", "loan",
            "deposit", "savings", "current account", "fixed deposit",
            "recurring deposit", "atm", "debit card", "credit card",
            "digital banking", "mobile banking", "internet banking",
            "upi", "neft", "rtgs", "imps", "swift", "iban"
        ],
        
        # Financial inclusion and schemes
        "schemes": [
            "jan dhan", "pmjdy", "mudra", "stand up india", "startup india",
            "financial inclusion", "financial literacy", "pradhan mantri",
            "subsidy", "loan waiver", "credit guarantee", "microfinance",
            "self help group", "shg", "priority sector lending",
            "kisan credit card", "crop insurance", "pension scheme"
        ],
        
        # Regulatory and policy
        "regulatory": [
            "sebi", "irdai", "pfrda", "nabard", "sidbi", "exim bank",
            "banking regulation", "basel", "kyc", "aml", "anti money laundering",
            "compliance", "audit", "governance", "risk management",
            "capital adequacy", "liquidity", "solvency", "provisioning"
        ],
        
        # Economic indicators
        "economic": [
            "gdp", "gnp", "fiscal deficit", "current account deficit",
            "balance of payment", "foreign exchange", "forex", "currency",
            "rupee", "dollar", "exchange rate", "trade deficit",
            "export", "import", "fdi", "fii", "investment",
            "stock market", "sensex", "nifty", "bond", "debenture",
            "mutual fund", "insurance", "pension", "provident fund"
        ],
        
        # Digital and fintech
        "digital": [
            "fintech", "blockchain", "cryptocurrency", "bitcoin",
            "digital payment", "e-wallet", "paytm", "phonepe", "google pay",
            "bhim", "rupay", "aadhar", "biometric", "authentication",
            "cybersecurity", "data protection", "privacy", "encryption"
        ]
    }
    
    # Flatten all keywords for easy searching
    ALL_BANKING_KEYWORDS = [
        keyword
        for category in BANKING_KEYWORDS.values()
        for keyword in category
    ]
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize Banking ranking strategy.
        
        Args:
            weights: Optional custom weights (uses DEFAULT_WEIGHTS if None)
        """
        super().__init__(
            exam_type="Banking",
            weights=weights or self.DEFAULT_WEIGHTS
        )
    
    def calculate_score(
        self, 
        content: str, 
        metadata: ArticleMetadata
    ) -> RankingResult:
        """
        Calculate Banking exam relevance score for an article.
        
        Implements the abstract method from AbstractRankingStrategy.
        
        Args:
            content: Article content text
            metadata: Article metadata for scoring
            
        Returns:
            RankingResult with score (0.0-10.0), reasoning, and factor breakdown
        """
        # Calculate individual factor scores
        factors = {}
        
        # 1. Category relevance (20%)
        factors["category_relevance"] = self._calculate_category_relevance(
            metadata.category,
            self.PRIORITY_CATEGORIES
        )
        
        # 2. Banking keyword score (35%) - most important for banking exams
        factors["banking_keyword_score"] = self._calculate_banking_keyword_score(
            content
        )
        
        # 3. Source credibility (15%)
        factors["source_credibility"] = self._calculate_source_credibility(
            metadata.source_type
        )
        
        # 4. Freshness (20%) - banking sector changes rapidly
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
        reasoning = self._generate_reasoning(factors, metadata, content)
        
        return RankingResult(
            score=final_score,
            reasoning=reasoning,
            factors=factors
        )
    
    def _calculate_banking_keyword_score(self, content: str) -> float:
        """
        Calculate banking domain relevance score.
        
        Banking exams require strong knowledge of banking terminology,
        financial concepts, and sector-specific news. Content with more
        banking keywords scores higher.
        
        Args:
            content: Article content text
            
        Returns:
            Score from 0.0 to 1.0 (higher = more banking-relevant)
        """
        if not content:
            return 0.0
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        # Count keywords by category
        category_scores = {}
        
        for category_name, keywords in self.BANKING_KEYWORDS.items():
            keyword_count = sum(
                1 for keyword in keywords
                if keyword in content_lower
            )
            
            # Normalize by category size and content length
            # Target: 2+ keywords per 100 words per category
            category_density = keyword_count / (word_count / 100) / 2
            category_scores[category_name] = min(1.0, category_density)
        
        # Weighted combination of category scores
        weights = {
            "core_banking": 0.35,
            "schemes": 0.25,
            "regulatory": 0.15,
            "economic": 0.15,
            "digital": 0.10
        }
        
        total_score = sum(
            category_scores[cat] * weights[cat]
            for cat in category_scores
        )
        
        # Bonus for high keyword diversity (multiple categories covered)
        categories_covered = sum(
            1 for score in category_scores.values()
            if score > 0.3
        )
        diversity_bonus = min(0.2, categories_covered * 0.05)
        
        final_score = min(1.0, total_score + diversity_bonus)
        
        return final_score
    
    def _calculate_source_credibility(self, source_type: str) -> float:
        """
        Calculate source credibility score for Banking preparation.
        
        Government schemes and PIB announcements are especially important
        for banking exams.
        
        Args:
            source_type: Type of source (youtube, pib, government_schemes)
            
        Returns:
            Score from 0.0 to 1.0 (higher = more credible)
        """
        return self.CREDIBLE_SOURCES.get(source_type, 0.5)
    
    def _generate_reasoning(
        self, 
        factors: Dict[str, float],
        metadata: ArticleMetadata,
        content: str
    ) -> str:
        """
        Generate human-readable reasoning for the score.
        
        Args:
            factors: Dictionary of factor scores
            metadata: Article metadata
            content: Article content (for keyword analysis)
            
        Returns:
            Reasoning text explaining the score
        """
        reasoning_parts = []
        
        # Category relevance
        if metadata.category in self.PRIORITY_CATEGORIES[:2]:
            reasoning_parts.append(
                f"High-priority category '{metadata.category}' for Banking exams"
            )
        else:
            reasoning_parts.append(
                f"Category '{metadata.category}' is relevant for Banking exams"
            )
        
        # Banking keyword score
        if factors["banking_keyword_score"] >= 0.7:
            reasoning_parts.append("Strong banking sector relevance with domain-specific terminology")
        elif factors["banking_keyword_score"] >= 0.4:
            reasoning_parts.append("Moderate banking sector relevance")
        else:
            reasoning_parts.append("Limited banking-specific content")
        
        # Identify which banking categories are present
        content_lower = content.lower() if content else ""
        present_categories = []
        
        for category_name, keywords in self.BANKING_KEYWORDS.items():
            if any(keyword in content_lower for keyword in keywords[:5]):
                present_categories.append(category_name.replace("_", " "))
        
        if present_categories:
            reasoning_parts.append(
                f"Contains {', '.join(present_categories[:2])} content"
            )
        
        # Source credibility
        if factors["source_credibility"] >= 0.9:
            reasoning_parts.append("Official government source")
        elif factors["source_credibility"] >= 0.7:
            reasoning_parts.append("Credible source")
        
        # Freshness
        if factors["freshness"] >= 0.8:
            reasoning_parts.append("Very recent banking sector news")
        elif factors["freshness"] >= 0.5:
            reasoning_parts.append("Recent content")
        else:
            reasoning_parts.append("Older content")
        
        return ". ".join(reasoning_parts) + "."
