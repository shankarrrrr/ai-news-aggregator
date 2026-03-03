"""
Base repository implementing the Repository Pattern with generic type support.

This module provides a generic base repository class that handles common CRUD
operations with proper session management and error handling.

Demonstrates:
- Repository Pattern (Design Pattern)
- Generic Programming (Type Safety)
- Dependency Inversion Principle (depend on abstractions)
- Single Responsibility Principle (data access only)
"""

from typing import TypeVar, Generic, List, Optional, Type
from contextlib import contextmanager
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.database.connection import get_engine


# Generic type variable for model classes
T = TypeVar('T')


class RepositoryException(Exception):
    """
    Custom exception for repository operations.
    
    Provides clear error context for database operation failures.
    """
    pass


class BaseRepository(Generic[T]):
    """
    Generic base repository for database operations.
    
    Implements the Repository Pattern to abstract data access logic.
    Uses Python generics to provide type-safe operations for any model type.
    
    Type Parameters:
        T: The SQLAlchemy model class this repository manages
    
    Attributes:
        _model_class (Type[T]): The model class for this repository (private)
        _session_factory (sessionmaker): SQLAlchemy session factory (private)
    
    Example:
        ```python
        class ArticleRepository(BaseRepository[Article]):
            def __init__(self):
                super().__init__(Article)
        
        repo = ArticleRepository()
        article = repo.find_by_id(1)
        ```
    """
    
    def __init__(self, model_class: Type[T]):
        """
        Initialize the repository with a model class.
        
        Args:
            model_class: The SQLAlchemy model class to manage
        """
        self._model_class = model_class
        self._session_factory = sessionmaker(bind=get_engine())
    
    @contextmanager
    def _get_session(self):
        """
        Context manager for database session handling.
        
        Implements proper session lifecycle:
        - Opens session
        - Commits on success
        - Rolls back on error
        - Always closes session
        
        Yields:
            Session: SQLAlchemy session
            
        Raises:
            RepositoryException: If database operation fails
            
        Example:
            ```python
            with self._get_session() as session:
                result = session.query(Article).all()
            ```
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise RepositoryException(f"Database operation failed: {str(e)}")
        except Exception as e:
            session.rollback()
            raise RepositoryException(f"Unexpected error: {str(e)}")
        finally:
            session.close()
    
    def create(self, entity: T) -> T:
        """
        Create a new entity in the database.
        
        Args:
            entity: The entity instance to create
            
        Returns:
            The created entity with populated ID
            
        Raises:
            RepositoryException: If creation fails
            
        Example:
            ```python
            article = Article(title="Test", content="Content", url="http://test.com")
            created = repo.create(article)
            print(created.id)  # Auto-generated ID
            ```
        """
        with self._get_session() as session:
            session.add(entity)
            session.flush()  # Populate ID before commit
            session.refresh(entity)  # Ensure all fields are loaded
            return entity
    
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """
        Find an entity by its primary key ID.
        
        Args:
            entity_id: The primary key value
            
        Returns:
            The entity if found, None otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            article = repo.find_by_id(42)
            if article:
                print(article.title)
            ```
        """
        with self._get_session() as session:
            return session.query(self._model_class).filter(
                self._model_class.id == entity_id
            ).first()
    
    def find_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        Find all entities with optional pagination.
        
        Args:
            limit: Maximum number of results (optional)
            offset: Number of results to skip (optional)
            
        Returns:
            List of entities
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            # Get first 10 articles
            articles = repo.find_all(limit=10, offset=0)
            
            # Get all articles
            all_articles = repo.find_all()
            ```
        """
        with self._get_session() as session:
            query = session.query(self._model_class)
            
            if offset is not None:
                query = query.offset(offset)
            
            if limit is not None:
                query = query.limit(limit)
            
            return query.all()
    
    def update(self, entity: T) -> T:
        """
        Update an existing entity in the database.
        
        Args:
            entity: The entity instance with updated values
            
        Returns:
            The updated entity
            
        Raises:
            RepositoryException: If update fails
            
        Example:
            ```python
            article = repo.find_by_id(1)
            article.title = "Updated Title"
            updated = repo.update(article)
            ```
        """
        with self._get_session() as session:
            merged = session.merge(entity)
            session.flush()
            session.refresh(merged)
            return merged
    
    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity by its primary key ID.
        
        Args:
            entity_id: The primary key value
            
        Returns:
            True if entity was deleted, False if not found
            
        Raises:
            RepositoryException: If deletion fails
            
        Example:
            ```python
            success = repo.delete(42)
            if success:
                print("Article deleted")
            ```
        """
        with self._get_session() as session:
            entity = session.query(self._model_class).filter(
                self._model_class.id == entity_id
            ).first()
            
            if entity is None:
                return False
            
            session.delete(entity)
            return True
    
    def count(self) -> int:
        """
        Count total number of entities.
        
        Returns:
            Total count of entities
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            total = repo.count()
            print(f"Total articles: {total}")
            ```
        """
        with self._get_session() as session:
            return session.query(self._model_class).count()
    
    def exists(self, entity_id: int) -> bool:
        """
        Check if an entity exists by ID.
        
        Args:
            entity_id: The primary key value
            
        Returns:
            True if entity exists, False otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            if repo.exists(42):
                print("Article exists")
            ```
        """
        with self._get_session() as session:
            return session.query(self._model_class).filter(
                self._model_class.id == entity_id
            ).first() is not None
