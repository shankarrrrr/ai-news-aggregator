"""
Repository package for data access layer.

This package implements the Repository Pattern to abstract database operations.
All repositories inherit from BaseRepository and provide type-safe CRUD operations.

Available Repositories:
- BaseRepository: Generic base repository with common CRUD operations
- ArticleRepository: Repository for Article entities with exam-specific queries
- SummaryRepository: Repository for Summary entities
- RankingRepository: Repository for Ranking entities with top-N queries
- CategoryRepository: Repository for Category entities
- SourceRepository: Repository for Source entities

Example Usage:
    ```python
    from app.database.repositories import ArticleRepository, CategoryRepository
    
    article_repo = ArticleRepository()
    category_repo = CategoryRepository()
    
    # Find articles from last 24 hours
    from datetime import datetime, timedelta
    end = datetime.now()
    start = end - timedelta(hours=24)
    recent = article_repo.find_by_date_range(start, end)
    
    # Get all categories
    categories = category_repo.find_all_ordered()
    ```
"""

from app.database.repositories.base_repository import BaseRepository, RepositoryException
from app.database.repositories.article_repository import ArticleRepository
from app.database.repositories.summary_repository import SummaryRepository
from app.database.repositories.ranking_repository import RankingRepository
from app.database.repositories.category_repository import CategoryRepository
from app.database.repositories.source_repository import SourceRepository

__all__ = [
    "BaseRepository",
    "RepositoryException",
    "ArticleRepository",
    "SummaryRepository",
    "RankingRepository",
    "CategoryRepository",
    "SourceRepository",
]
