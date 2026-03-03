"""
Source repository for content sources.

This module provides repository for Source entities with queries
for finding sources by type and active status.

Demonstrates:
- Repository Pattern specialization
- Reference data management
"""

from typing import List, Optional
from app.database.models import Source, SourceType
from app.database.repositories.base_repository import BaseRepository


class SourceRepository(BaseRepository[Source]):
    """
    Repository for Source entities.
    
    Inherits from BaseRepository[Source] and adds specialized query methods
    for finding sources by type and active status.
    
    Sources represent content origins (YouTube channels, PIB, government portals)
    that are seeded during database initialization.
    
    Demonstrates:
    - Liskov Substitution Principle (can be used wherever BaseRepository is expected)
    - Single Responsibility Principle (only handles source data access)
    """
    
    def __init__(self):
        """Initialize the source repository."""
        super().__init__(Source)
    
    def find_by_type(self, source_type: SourceType) -> List[Source]:
        """
        Find all sources of a specific type.
        
        Args:
            source_type: The source type (YOUTUBE, PIB, GOVERNMENT_SCHEMES)
            
        Returns:
            List of sources of the specified type
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            from app.database.models import SourceType
            
            youtube_sources = repo.find_by_type(SourceType.YOUTUBE)
            for source in youtube_sources:
                print(f"{source.name}: {source.url}")
            ```
        """
        with self._get_session() as session:
            return session.query(Source).filter(
                Source.source_type == source_type
            ).all()
    
    def find_active_sources(self) -> List[Source]:
        """
        Find all active sources (is_active = True).
        
        Used by scraping service to determine which sources to scrape.
        
        Returns:
            List of active sources
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            active = repo.find_active_sources()
            for source in active:
                # Scrape this source
                pass
            ```
        """
        with self._get_session() as session:
            return session.query(Source).filter(
                Source.is_active == True
            ).all()
    
    def find_active_by_type(self, source_type: SourceType) -> List[Source]:
        """
        Find active sources of a specific type.
        
        Combines type and active status filters.
        
        Args:
            source_type: The source type to filter by
            
        Returns:
            List of active sources of the specified type
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            from app.database.models import SourceType
            
            active_youtube = repo.find_active_by_type(SourceType.YOUTUBE)
            ```
        """
        with self._get_session() as session:
            return session.query(Source).filter(
                Source.source_type == source_type,
                Source.is_active == True
            ).all()
    
    def find_by_name(self, name: str) -> Optional[Source]:
        """
        Find a source by its name.
        
        Uses unique index on name for fast lookup.
        
        Args:
            name: The source name
            
        Returns:
            The source if found, None otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            pib = repo.find_by_name("Press Information Bureau")
            if pib:
                print(f"Source ID: {pib.id}")
            ```
        """
        with self._get_session() as session:
            return session.query(Source).filter(
                Source.name == name
            ).first()
    
    def find_by_url(self, url: str) -> Optional[Source]:
        """
        Find a source by its URL.
        
        Used to check for duplicate sources during seeding.
        
        Args:
            url: The source URL
            
        Returns:
            The source if found, None otherwise
            
        Raises:
            RepositoryException: If query fails
            
        Example:
            ```python
            existing = repo.find_by_url("https://pib.gov.in")
            if existing:
                print("Source already exists")
            ```
        """
        with self._get_session() as session:
            return session.query(Source).filter(
                Source.url == url
            ).first()
    
    def deactivate_source(self, source_id: int) -> bool:
        """
        Deactivate a source (set is_active = False).
        
        Useful for temporarily disabling sources without deleting them.
        
        Args:
            source_id: The source ID to deactivate
            
        Returns:
            True if source was deactivated, False if not found
            
        Raises:
            RepositoryException: If update fails
            
        Example:
            ```python
            success = repo.deactivate_source(source_id=3)
            if success:
                print("Source deactivated")
            ```
        """
        with self._get_session() as session:
            source = session.query(Source).filter(
                Source.id == source_id
            ).first()
            
            if source is None:
                return False
            
            source.is_active = False
            return True
    
    def activate_source(self, source_id: int) -> bool:
        """
        Activate a source (set is_active = True).
        
        Re-enables a previously deactivated source.
        
        Args:
            source_id: The source ID to activate
            
        Returns:
            True if source was activated, False if not found
            
        Raises:
            RepositoryException: If update fails
            
        Example:
            ```python
            success = repo.activate_source(source_id=3)
            if success:
                print("Source activated")
            ```
        """
        with self._get_session() as session:
            source = session.query(Source).filter(
                Source.id == source_id
            ).first()
            
            if source is None:
                return False
            
            source.is_active = True
            return True
