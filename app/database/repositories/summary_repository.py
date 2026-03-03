"""
Summary repository for AI-generated article summaries.

This module provides repository for Summary entities with queries
for finding summaries by article.

Demonstrates:
- Repository Pattern specialization
- One-to-one relationship handling
"""

from typing import Optional
from app.database.models import Summary
from app.database.repositories.base_repository import BaseRepository


class SummaryRepository(BaseRepository[Summary]):
    """
    Repository for Summary entities.
    
    Inherits from BaseRepository[Summary] and adds specialized query methods
    for finding summaries by article ID.
    
    Demonstrates:
    - Liskov Substitution Principle (can be used wherever BaseRepository is expected)
    - Single Responsibility Principle (only handles summary data access)
    """
    
    def __init__(self):
        """Initialize the summary repository."""
        super().__init__(Summary)
    
    def find_by_article_id(self, article_id: int) -> Optional[Summary]:
        """
        Find a summary by its associated article ID.
        
        Since Summary has a one-to-one relationship with Article,
        this returns at most one summary.
        
        Args:
            article_id: The article ID to find summary for
            
        Returns:
            The summary if found, None otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            summary = repo.find_by_article_id(42)
            if summary:
                print(summary.summary_text)
                print(summary.exam_relevance)
            ```
        """
        with self._get_session() as session:
            return session.query(Summary).filter(
                Summary.article_id == article_id
            ).first()
    
    def exists_for_article(self, article_id: int) -> bool:
        """
        Check if a summary exists for an article.
        
        Useful for pipeline processing to identify articles needing summarization.
        
        Args:
            article_id: The article ID to check
            
        Returns:
            True if summary exists, False otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            if not repo.exists_for_article(42):
                # Generate summary for this article
                pass
            ```
        """
        with self._get_session() as session:
            return session.query(Summary).filter(
                Summary.article_id == article_id
            ).first() is not None
