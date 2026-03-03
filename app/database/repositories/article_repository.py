"""
Article repository with exam-specific query methods.

This module provides specialized repository for Article entities with
queries optimized for competitive exam content management.

Demonstrates:
- Repository Pattern specialization
- Query optimization with indexes
- Bulk operations for performance
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from app.database.models import Article
from app.database.repositories.base_repository import BaseRepository, RepositoryException


class ArticleRepository(BaseRepository[Article]):
    """
    Repository for Article entities with exam-specific queries.
    
    Inherits from BaseRepository[Article] and adds specialized query methods
    for finding articles by date range, category, source, and URL.
    
    Demonstrates:
    - Liskov Substitution Principle (can be used wherever BaseRepository is expected)
    - Single Responsibility Principle (only handles article data access)
    """
    
    def __init__(self):
        """Initialize the article repository."""
        super().__init__(Article)
    
    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: Optional[int] = None
    ) -> List[Article]:
        """
        Find articles published within a date range.
        
        Uses index on published_at for performance.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            limit: Maximum number of results (optional)
            
        Returns:
            List of articles within date range, ordered by published_at DESC
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            from datetime import datetime, timedelta
            
            end = datetime.now()
            start = end - timedelta(hours=24)
            recent_articles = repo.find_by_date_range(start, end, limit=10)
            ```
        """
        with self._get_session() as session:
            query = session.query(Article).filter(
                and_(
                    Article.published_at >= start_date,
                    Article.published_at <= end_date
                )
            ).order_by(Article.published_at.desc())
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
    
    def find_by_category(
        self,
        category_id: int,
        limit: Optional[int] = None
    ) -> List[Article]:
        """
        Find articles by category ID.
        
        Uses index on category_id for performance.
        
        Args:
            category_id: The category ID to filter by
            limit: Maximum number of results (optional)
            
        Returns:
            List of articles in the category, ordered by published_at DESC
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            polity_articles = repo.find_by_category(category_id=1, limit=20)
            ```
        """
        with self._get_session() as session:
            query = session.query(Article).filter(
                Article.category_id == category_id
            ).order_by(Article.published_at.desc())
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
    
    def find_by_source(
        self,
        source_id: int,
        limit: Optional[int] = None
    ) -> List[Article]:
        """
        Find articles by source ID.
        
        Uses index on source_id for performance.
        
        Args:
            source_id: The source ID to filter by
            limit: Maximum number of results (optional)
            
        Returns:
            List of articles from the source, ordered by published_at DESC
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            youtube_articles = repo.find_by_source(source_id=1, limit=50)
            ```
        """
        with self._get_session() as session:
            query = session.query(Article).filter(
                Article.source_id == source_id
            ).order_by(Article.published_at.desc())
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
    
    def find_by_url(self, url: str) -> Optional[Article]:
        """
        Find an article by its URL (for duplicate detection).
        
        Uses unique index on url for fast lookup.
        
        Args:
            url: The article URL
            
        Returns:
            The article if found, None otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            existing = repo.find_by_url("https://example.com/article")
            if existing:
                print("Article already exists")
            ```
        """
        with self._get_session() as session:
            return session.query(Article).filter(
                Article.url == url
            ).first()
    
    def bulk_create(self, articles: List[Article]) -> List[Article]:
        """
        Create multiple articles in a single transaction (bulk insert).
        
        Implements performance optimization for batch processing.
        Uses SQLAlchemy bulk operations for efficiency.
        
        Args:
            articles: List of article instances to create
            
        Returns:
            List of created articles with populated IDs
            
        Raises:
            RepositoryException: If bulk creation fails
            
        Example:
            ```python
            articles = [
                Article(title="A1", content="C1", url="http://1.com", ...),
                Article(title="A2", content="C2", url="http://2.com", ...),
            ]
            created = repo.bulk_create(articles)
            print(f"Created {len(created)} articles")
            ```
        """
        if not articles:
            return []
        
        with self._get_session() as session:
            try:
                session.bulk_save_objects(articles, return_defaults=True)
                session.flush()
                
                # Refresh all objects to get generated IDs
                for article in articles:
                    session.refresh(article)
                
                return articles
            except IntegrityError as e:
                raise RepositoryException(f"Bulk create failed (duplicate URL?): {str(e)}")
    
    def find_uncategorized(self, limit: Optional[int] = None) -> List[Article]:
        """
        Find articles that haven't been categorized yet.
        
        Useful for pipeline processing to identify articles needing categorization.
        
        Args:
            limit: Maximum number of results (optional)
            
        Returns:
            List of uncategorized articles, ordered by published_at DESC
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            pending = repo.find_uncategorized(limit=100)
            for article in pending:
                # Process with CategorizationAgent
                pass
            ```
        """
        with self._get_session() as session:
            query = session.query(Article).filter(
                Article.category_id.is_(None)
            ).order_by(Article.published_at.desc())
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
    
    def find_by_category_and_date_range(
        self,
        category_id: int,
        start_date: datetime,
        end_date: datetime,
        limit: Optional[int] = None
    ) -> List[Article]:
        """
        Find articles by both category and date range.
        
        Combines multiple filters for precise queries.
        
        Args:
            category_id: The category ID to filter by
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            limit: Maximum number of results (optional)
            
        Returns:
            List of matching articles, ordered by published_at DESC
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            from datetime import datetime, timedelta
            
            end = datetime.now()
            start = end - timedelta(days=7)
            recent_polity = repo.find_by_category_and_date_range(
                category_id=1, start_date=start, end_date=end, limit=10
            )
            ```
        """
        with self._get_session() as session:
            query = session.query(Article).filter(
                and_(
                    Article.category_id == category_id,
                    Article.published_at >= start_date,
                    Article.published_at <= end_date
                )
            ).order_by(Article.published_at.desc())
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
