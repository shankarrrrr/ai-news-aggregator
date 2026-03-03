"""
Ranking repository with top-N query optimization.

This module provides repository for Ranking entities with queries
optimized for finding top-ranked articles.

Demonstrates:
- Repository Pattern specialization
- Query optimization with indexes
- Performance-critical top-N queries
"""

from typing import List, Optional
from sqlalchemy import and_
from app.database.models import Ranking, Article
from app.database.repositories.base_repository import BaseRepository


class RankingRepository(BaseRepository[Ranking]):
    """
    Repository for Ranking entities with top-N query optimization.
    
    Inherits from BaseRepository[Ranking] and adds specialized query methods
    for finding rankings by article, score range, and top-N rankings.
    
    Demonstrates:
    - Liskov Substitution Principle (can be used wherever BaseRepository is expected)
    - Single Responsibility Principle (only handles ranking data access)
    - Performance optimization with proper indexing
    """
    
    def __init__(self):
        """Initialize the ranking repository."""
        super().__init__(Ranking)
    
    def find_by_article_id(self, article_id: int) -> Optional[Ranking]:
        """
        Find a ranking by its associated article ID.
        
        Since Ranking has a one-to-one relationship with Article,
        this returns at most one ranking.
        
        Args:
            article_id: The article ID to find ranking for
            
        Returns:
            The ranking if found, None otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            ranking = repo.find_by_article_id(42)
            if ranking:
                print(f"Score: {ranking.score}")
                print(f"Reasoning: {ranking.reasoning}")
            ```
        """
        with self._get_session() as session:
            return session.query(Ranking).filter(
                Ranking.article_id == article_id
            ).first()
    
    def find_top_n(
        self,
        n: int,
        exam_type: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> List[Ranking]:
        """
        Find top N ranked articles by score.
        
        Uses index on score column for performance.
        Optionally filters by exam type and minimum score.
        
        Args:
            n: Number of top rankings to return
            exam_type: Filter by exam type (UPSC, SSC, Banking) (optional)
            min_score: Minimum score threshold (optional)
            
        Returns:
            List of top N rankings, ordered by score DESC
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            # Get top 10 articles for UPSC
            top_upsc = repo.find_top_n(n=10, exam_type="UPSC", min_score=7.0)
            
            # Get top 20 articles overall
            top_all = repo.find_top_n(n=20)
            ```
        """
        with self._get_session() as session:
            query = session.query(Ranking)
            
            # Apply filters
            filters = []
            if exam_type is not None:
                filters.append(Ranking.exam_type == exam_type)
            if min_score is not None:
                filters.append(Ranking.score >= min_score)
            
            if filters:
                query = query.filter(and_(*filters))
            
            # Order by score DESC and limit to N
            query = query.order_by(Ranking.score.desc()).limit(n)
            
            return query.all()
    
    def find_by_score_range(
        self,
        min_score: float,
        max_score: float,
        exam_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Ranking]:
        """
        Find rankings within a score range.
        
        Useful for identifying borderline articles or specific score tiers.
        
        Args:
            min_score: Minimum score (inclusive)
            max_score: Maximum score (inclusive)
            exam_type: Filter by exam type (optional)
            limit: Maximum number of results (optional)
            
        Returns:
            List of rankings within score range, ordered by score DESC
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            # Find borderline articles (scores 4.0-6.0)
            borderline = repo.find_by_score_range(
                min_score=4.0, max_score=6.0, exam_type="UPSC"
            )
            ```
        """
        with self._get_session() as session:
            query = session.query(Ranking).filter(
                and_(
                    Ranking.score >= min_score,
                    Ranking.score <= max_score
                )
            )
            
            if exam_type is not None:
                query = query.filter(Ranking.exam_type == exam_type)
            
            query = query.order_by(Ranking.score.desc())
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
    
    def exists_for_article(self, article_id: int) -> bool:
        """
        Check if a ranking exists for an article.
        
        Useful for pipeline processing to identify articles needing ranking.
        
        Args:
            article_id: The article ID to check
            
        Returns:
            True if ranking exists, False otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            if not repo.exists_for_article(42):
                # Generate ranking for this article
                pass
            ```
        """
        with self._get_session() as session:
            return session.query(Ranking).filter(
                Ranking.article_id == article_id
            ).first() is not None
    
    def find_top_n_with_articles(
        self,
        n: int,
        exam_type: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> List[tuple[Ranking, Article]]:
        """
        Find top N ranked articles with their associated article data.
        
        Performs a join to fetch both ranking and article in a single query.
        Optimized for digest generation where both ranking and article data are needed.
        
        Args:
            n: Number of top rankings to return
            exam_type: Filter by exam type (optional)
            min_score: Minimum score threshold (optional)
            
        Returns:
            List of (Ranking, Article) tuples, ordered by score DESC
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            top_with_articles = repo.find_top_n_with_articles(n=10, exam_type="UPSC")
            for ranking, article in top_with_articles:
                print(f"{article.title}: {ranking.score}")
            ```
        """
        with self._get_session() as session:
            query = session.query(Ranking, Article).join(
                Article, Ranking.article_id == Article.id
            )
            
            # Apply filters
            filters = []
            if exam_type is not None:
                filters.append(Ranking.exam_type == exam_type)
            if min_score is not None:
                filters.append(Ranking.score >= min_score)
            
            if filters:
                query = query.filter(and_(*filters))
            
            # Order by score DESC and limit to N
            query = query.order_by(Ranking.score.desc()).limit(n)
            
            return query.all()
