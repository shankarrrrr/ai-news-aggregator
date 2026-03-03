"""
Digest Generation Service for compiling top-ranked articles.

This module implements the DigestGenerationService that coordinates between
the RankingRepository and DigestAgent to generate formatted digests.

Demonstrates:
- Service Layer Pattern (business logic coordination)
- Dependency Injection (repositories and agents injected)
- Single Responsibility Principle (only handles digest generation)
- Open/Closed Principle (extensible without modification)
"""

import json
from typing import List, Optional
from datetime import datetime
from app.agent.digest_agent import DigestAgent, DigestArticle, DigestResult
from app.database.repositories.ranking_repository import RankingRepository
from app.database.models import Ranking, Article, Summary


class DigestGenerationService:
    """
    Service for generating formatted digests from top-ranked articles.
    
    Coordinates between RankingRepository and DigestAgent to:
    1. Fetch top N ranked articles with their data
    2. Convert database entities to DigestArticle format
    3. Generate formatted digest using DigestAgent
    4. Return formatted text output
    
    Demonstrates:
    - Service Layer Pattern (orchestrates business logic)
    - Dependency Inversion Principle (depends on abstractions)
    - Single Responsibility Principle (only handles digest generation)
    
    Attributes:
        _digest_agent (DigestAgent): AI agent for digest compilation (private)
        _ranking_repository (RankingRepository): Repository for rankings (private)
    """
    
    def __init__(
        self,
        digest_agent: DigestAgent,
        ranking_repository: RankingRepository
    ):
        """
        Initialize the digest generation service.
        
        Uses dependency injection to receive required components.
        This follows the Dependency Inversion Principle - the service
        depends on abstractions (interfaces) not concrete implementations.
        
        Args:
            digest_agent: Agent for generating formatted digests
            ranking_repository: Repository for accessing ranking data
        """
        self._digest_agent = digest_agent
        self._ranking_repository = ranking_repository
    
    def generate_digest(
        self,
        top_n: int = 10,
        exam_type: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> str:
        """
        Generate a formatted digest from top-ranked articles.
        
        This is the main service method that orchestrates the digest generation
        process. It demonstrates the Service Layer Pattern by coordinating
        between multiple components to achieve a business goal.
        
        Args:
            top_n: Number of top articles to include in digest
            exam_type: Filter by exam type (UPSC, SSC, Banking) (optional)
            min_score: Minimum score threshold (optional)
            
        Returns:
            Formatted digest text ready for display or email
            
        Raises:
            DigestGenerationException: If digest generation fails
            
        Example:
            ```python
            service = DigestGenerationService(digest_agent, ranking_repo)
            
            # Generate top 10 UPSC articles
            digest = service.generate_digest(
                top_n=10, 
                exam_type="UPSC", 
                min_score=7.0
            )
            print(digest)
            ```
        """
        try:
            # Step 1: Fetch top N articles with rankings and article data
            top_rankings_with_articles = self._ranking_repository.find_top_n_with_articles(
                n=top_n,
                exam_type=exam_type,
                min_score=min_score
            )
            
            if not top_rankings_with_articles:
                return self._generate_empty_digest(exam_type)
            
            # Step 2: Convert to DigestArticle format
            digest_articles = []
            for ranking, article in top_rankings_with_articles:
                digest_article = self._convert_to_digest_article(ranking, article)
                if digest_article:
                    digest_articles.append(digest_article)
            
            if not digest_articles:
                return self._generate_empty_digest(exam_type)
            
            # Step 3: Prepare input data for DigestAgent
            input_data = {
                "articles": digest_articles,
                "exam_type": exam_type or "General",
                "generation_params": {
                    "top_n": top_n,
                    "min_score": min_score,
                    "total_articles_processed": len(digest_articles)
                }
            }
            
            # Step 4: Generate digest using DigestAgent
            digest_result = self._digest_agent.execute(input_data)
            
            # Step 5: Format as text and return
            formatted_digest = self._digest_agent.format_as_text(digest_result)
            
            return formatted_digest
            
        except Exception as e:
            raise DigestGenerationException(
                f"Failed to generate digest: {str(e)}"
            ) from e
    
    def _convert_to_digest_article(
        self,
        ranking: Ranking,
        article: Article
    ) -> Optional[DigestArticle]:
        """
        Convert database entities to DigestArticle format.
        
        Extracts relevant data from Ranking and Article entities and
        creates a DigestArticle object suitable for digest compilation.
        
        Args:
            ranking: Ranking entity with score and reasoning
            article: Article entity with content and metadata
            
        Returns:
            DigestArticle object or None if conversion fails
        """
        try:
            # Extract key facts from summary if available
            key_facts = []
            if article.summary and article.summary.key_facts:
                try:
                    key_facts = json.loads(article.summary.key_facts)
                    if not isinstance(key_facts, list):
                        key_facts = []
                except (json.JSONDecodeError, TypeError):
                    key_facts = []
            
            # Get summary text
            summary_text = ""
            if article.summary and article.summary.summary_text:
                summary_text = article.summary.summary_text
            else:
                # Fallback to truncated content if no summary
                summary_text = article.content[:300] + "..." if len(article.content) > 300 else article.content
            
            # Get category name
            category_name = "Uncategorized"
            if article.category:
                category_name = article.category.name
            
            return DigestArticle(
                title=article.title,
                summary=summary_text,
                category=category_name,
                score=ranking.score,
                url=article.url,
                published_at=article.published_at,
                key_facts=key_facts
            )
            
        except Exception as e:
            # Log the error but don't fail the entire digest generation
            print(f"Warning: Failed to convert article {article.id} to DigestArticle: {str(e)}")
            return None
    
    def _generate_empty_digest(self, exam_type: Optional[str]) -> str:
        """
        Generate a digest for when no articles are found.
        
        Args:
            exam_type: The exam type that was searched for
            
        Returns:
            Formatted empty digest message
        """
        exam_text = f" for {exam_type}" if exam_type else ""
        
        return f"""
# Daily Competitive Exam Intelligence Digest{exam_text}

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

No articles found matching the specified criteria. This could be due to:
- No new content in the specified time period
- All articles scored below the minimum threshold
- No articles available for the specified exam type

Please try:
- Expanding the time window
- Lowering the minimum score threshold
- Running the scraping pipeline to fetch new content

---

*Generated by AI-Powered Competitive Exam News Intelligence System*
        """.strip()
    
    def get_digest_statistics(
        self,
        top_n: int = 10,
        exam_type: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> dict:
        """
        Get statistics about available articles for digest generation.
        
        Useful for monitoring and reporting purposes.
        
        Args:
            top_n: Number of top articles to analyze
            exam_type: Filter by exam type (optional)
            min_score: Minimum score threshold (optional)
            
        Returns:
            Dictionary with statistics about available articles
        """
        try:
            top_rankings = self._ranking_repository.find_top_n(
                n=top_n,
                exam_type=exam_type,
                min_score=min_score
            )
            
            if not top_rankings:
                return {
                    "total_articles": 0,
                    "exam_type": exam_type,
                    "min_score": min_score,
                    "max_score": None,
                    "avg_score": None,
                    "categories_represented": []
                }
            
            scores = [r.score for r in top_rankings]
            
            # Get categories (would need to join with articles)
            categories = set()
            for ranking in top_rankings:
                if ranking.article and ranking.article.category:
                    categories.add(ranking.article.category.name)
            
            return {
                "total_articles": len(top_rankings),
                "exam_type": exam_type,
                "min_score": min_score,
                "max_score": max(scores),
                "avg_score": sum(scores) / len(scores),
                "categories_represented": list(categories)
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get statistics: {str(e)}",
                "total_articles": 0
            }


class DigestGenerationException(Exception):
    """Exception raised during digest generation."""
    pass