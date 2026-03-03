"""
Category repository for exam content categories.

This module provides repository for Category entities with queries
for finding categories by name and ordered lists.

Demonstrates:
- Repository Pattern specialization
- Reference data management
"""

from typing import List, Optional
from app.database.models import Category
from app.database.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """
    Repository for Category entities.
    
    Inherits from BaseRepository[Category] and adds specialized query methods
    for finding categories by name and retrieving ordered lists.
    
    Categories are reference data (Polity, Economy, International Relations, etc.)
    that are seeded during database initialization.
    
    Demonstrates:
    - Liskov Substitution Principle (can be used wherever BaseRepository is expected)
    - Single Responsibility Principle (only handles category data access)
    """
    
    def __init__(self):
        """Initialize the category repository."""
        super().__init__(Category)
    
    def find_by_name(self, name: str) -> Optional[Category]:
        """
        Find a category by its name.
        
        Uses unique index on name for fast lookup.
        
        Args:
            name: The category name (e.g., "Polity", "Economy")
            
        Returns:
            The category if found, None otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            polity = repo.find_by_name("Polity")
            if polity:
                print(f"Category ID: {polity.id}")
            ```
        """
        with self._get_session() as session:
            return session.query(Category).filter(
                Category.name == name
            ).first()
    
    def find_all_ordered(self) -> List[Category]:
        """
        Find all categories ordered by name alphabetically.
        
        Useful for displaying category lists in UI or reports.
        
        Returns:
            List of all categories, ordered by name ASC
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            categories = repo.find_all_ordered()
            for cat in categories:
                print(f"{cat.id}: {cat.name}")
            ```
        """
        with self._get_session() as session:
            return session.query(Category).order_by(Category.name.asc()).all()
    
    def get_category_id_by_name(self, name: str) -> Optional[int]:
        """
        Get category ID by name (convenience method).
        
        Returns just the ID without loading the full entity.
        Useful for foreign key assignments.
        
        Args:
            name: The category name
            
        Returns:
            The category ID if found, None otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            category_id = repo.get_category_id_by_name("Economy")
            article.category_id = category_id
            ```
        """
        category = self.find_by_name(name)
        return category.id if category else None
    
    def exists_by_name(self, name: str) -> bool:
        """
        Check if a category exists by name.
        
        Useful for validation before creating articles.
        
        Args:
            name: The category name to check
            
        Returns:
            True if category exists, False otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            if repo.exists_by_name("Polity"):
                print("Valid category")
            ```
        """
        with self._get_session() as session:
            return session.query(Category).filter(
                Category.name == name
            ).first() is not None
