"""
Categorization Service for article classification.

This module implements the Service Layer Pattern for coordinating
article categorization using the CategorizationAgent.

Demonstrates:
- Service Layer Pattern (business logic coordination)
- Dependency Injection (depends on abstractions)
- Error handling and logging
"""

from typing import List, Dict, Optional
import logging
import json

from app.agent.categorization_agent import CategorizationAgent, CategoryResult
from app.agent.abstract_agent import AgentException
from app.database.repositories.article_repository import ArticleRepository
from app.database.repositories.category_repository import CategoryRepository
from app.database.models import Article


logger = logging.getLogger(__name__)


class CategorizationService:
    """
    Service for categorizing articles using AI.
    
    Coordinates between CategorizationAgent and repositories to classify
    articles into exam-relevant categories and update the database.
    
    Demonstrates:
    - Dependency Inversion Principle (depends on abstractions: agent, repositories)
    - Single Responsibility Principle (only handles categorization orchestration)
    - Error handling for production readiness
    
    Attributes:
        _categorization_agent (CategorizationAgent): Agent for AI categorization
        _article_repo (ArticleRepository): Repository for article persistence
        _category_repo (CategoryRepository): Repository for category lookup
    """
    
    def __init__(
        self,
        categorization_agent: CategorizationAgent,
        article_repository: ArticleRepository,
        category_repository: CategoryRepository
    ):
        """
        Initialize the categorization service with dependencies.
        
        Uses dependency injection to receive agent and repository instances,
        demonstrating the Dependency Inversion Principle.
        
        Args:
            categorization_agent: Agent for AI-powered categorization
            article_repository: Repository for article data access
            category_repository: Repository for category data access
        """
        self._categorization_agent = categorization_agent
        self._article_repo = article_repository
        self._category_repo = category_repository
        logger.info("CategorizationService initialized")
    
    def categorize_articles(
        self,
        article_ids: Optional[List[int]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Categorize multiple articles in batch.
        
        If article_ids is provided, categorizes those specific articles.
        Otherwise, categorizes uncategorized articles (category_id is None).
        
        Args:
            article_ids: Optional list of specific article IDs to categorize
            limit: Maximum number of articles to process (optional)
            
        Returns:
            Dictionary with statistics:
            - 'total_processed': Total articles processed
            - 'successfully_categorized': Articles successfully categorized
            - 'failed': Articles that failed categorization
            
        Example:
            >>> service = CategorizationService(agent, article_repo, category_repo)
            >>> stats = service.categorize_articles(limit=100)
            >>> print(f"Categorized {stats['successfully_categorized']} articles")
        """
        logger.info("Starting batch categorization")
        
        # Get articles to categorize
        if article_ids:
            articles = [
                self._article_repo.find_by_id(article_id)
                for article_id in article_ids
            ]
            articles = [a for a in articles if a is not None]
        else:
            articles = self._article_repo.find_uncategorized(limit=limit)
        
        logger.info(f"Found {len(articles)} articles to categorize")
        
        # Statistics tracking
        total_processed = 0
        successfully_categorized = 0
        failed = 0
        
        # Categorize each article
        for article in articles:
            try:
                self._categorize_article(article)
                successfully_categorized += 1
                total_processed += 1
                
                if total_processed % 10 == 0:
                    logger.info(f"Progress: {total_processed}/{len(articles)} articles")
                    
            except Exception as e:
                failed += 1
                total_processed += 1
                logger.error(
                    f"Failed to categorize article {article.id}: {str(e)}",
                    exc_info=True
                )
                # Continue with other articles even if one fails
                continue
        
        # Return statistics
        stats = {
            'total_processed': total_processed,
            'successfully_categorized': successfully_categorized,
            'failed': failed
        }
        
        logger.info(f"Categorization complete: {stats}")
        return stats
    
    def _categorize_article(self, article: Article) -> None:
        """
        Categorize a single article and update the database.
        
        Calls the CategorizationAgent to classify the article,
        then updates the article's category_id and secondary_categories.
        
        Args:
            article: The article entity to categorize
            
        Raises:
            AgentException: If categorization fails
            Exception: If database update fails
        """
        logger.debug(f"Categorizing article {article.id}: {article.title[:50]}...")
        
        # Prepare input for agent
        input_data = {
            'title': article.title,
            'content': article.content,
            'source_type': article.source.source_type.value if article.source else 'unknown'
        }
        
        # Call categorization agent
        try:
            result: CategoryResult = self._categorization_agent.execute(input_data)
        except AgentException as e:
            logger.error(f"Agent failed for article {article.id}: {str(e)}")
            raise
        
        # Get category ID for primary category
        primary_category_id = self._category_repo.get_category_id_by_name(
            result.primary_category
        )
        
        if primary_category_id is None:
            raise ValueError(
                f"Category '{result.primary_category}' not found in database"
            )
        
        # Update article with categorization results
        article.category_id = primary_category_id
        
        # Store secondary categories as comma-separated string
        if result.secondary_categories:
            article.secondary_categories = ','.join(result.secondary_categories)
        else:
            article.secondary_categories = None
        
        # Store categorization metadata (confidence, reasoning)
        metadata = {}
        if article.metadata:
            try:
                metadata = json.loads(article.metadata)
            except json.JSONDecodeError:
                metadata = {}
        
        metadata['categorization'] = {
            'confidence': result.confidence,
            'reasoning': result.reasoning,
            'primary_category': result.primary_category,
            'secondary_categories': result.secondary_categories
        }
        
        article.metadata = json.dumps(metadata)
        
        # Update in database
        self._article_repo.update(article)
        
        logger.debug(
            f"Article {article.id} categorized as {result.primary_category} "
            f"(confidence: {result.confidence:.2f})"
        )
    
    def categorize_single_article(self, article_id: int) -> CategoryResult:
        """
        Categorize a single article by ID.
        
        Useful for testing or re-categorizing specific articles.
        
        Args:
            article_id: The article ID to categorize
            
        Returns:
            CategoryResult with categorization details
            
        Raises:
            ValueError: If article not found
            AgentException: If categorization fails
        """
        article = self._article_repo.find_by_id(article_id)
        
        if article is None:
            raise ValueError(f"Article with ID {article_id} not found")
        
        logger.info(f"Categorizing single article: {article.id}")
        
        # Prepare input
        input_data = {
            'title': article.title,
            'content': article.content,
            'source_type': article.source.source_type.value if article.source else 'unknown'
        }
        
        # Call agent
        result = self._categorization_agent.execute(input_data)
        
        # Update article
        primary_category_id = self._category_repo.get_category_id_by_name(
            result.primary_category
        )
        
        if primary_category_id is None:
            raise ValueError(
                f"Category '{result.primary_category}' not found in database"
            )
        
        article.category_id = primary_category_id
        
        if result.secondary_categories:
            article.secondary_categories = ','.join(result.secondary_categories)
        else:
            article.secondary_categories = None
        
        # Store metadata
        metadata = {}
        if article.metadata:
            try:
                metadata = json.loads(article.metadata)
            except json.JSONDecodeError:
                metadata = {}
        
        metadata['categorization'] = {
            'confidence': result.confidence,
            'reasoning': result.reasoning,
            'primary_category': result.primary_category,
            'secondary_categories': result.secondary_categories
        }
        
        article.metadata = json.dumps(metadata)
        
        # Update in database
        self._article_repo.update(article)
        
        logger.info(
            f"Article {article.id} categorized as {result.primary_category}"
        )
        
        return result
    
    def recategorize_articles(
        self,
        category_name: str,
        limit: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Re-categorize articles in a specific category.
        
        Useful for improving categorization after model updates.
        
        Args:
            category_name: Name of category to re-categorize
            limit: Maximum number of articles to process
            
        Returns:
            Dictionary with statistics (same format as categorize_articles)
            
        Raises:
            ValueError: If category not found
        """
        category_id = self._category_repo.get_category_id_by_name(category_name)
        
        if category_id is None:
            raise ValueError(f"Category '{category_name}' not found")
        
        logger.info(f"Re-categorizing articles in category: {category_name}")
        
        # Get articles in this category
        articles = self._article_repo.find_by_category(category_id, limit=limit)
        
        # Reset category_id to trigger re-categorization
        for article in articles:
            article.category_id = None
        
        # Use batch categorization
        article_ids = [article.id for article in articles]
        return self.categorize_articles(article_ids=article_ids)
