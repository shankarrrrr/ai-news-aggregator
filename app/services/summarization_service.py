"""
Summarization Service for generating exam-focused summaries.

This module implements the Service Layer Pattern for coordinating
article summarization using the SummarizationAgent.

Demonstrates:
- Service Layer Pattern (business logic coordination)
- Dependency Injection (depends on abstractions)
- Error handling and logging
"""

from typing import List, Dict, Optional
import logging
import json

from app.agent.summarization_agent import SummarizationAgent, SummaryResult
from app.agent.abstract_agent import AgentException
from app.database.repositories.article_repository import ArticleRepository
from app.database.repositories.summary_repository import SummaryRepository
from app.database.models import Article, Summary


logger = logging.getLogger(__name__)


class SummarizationService:
    """
    Service for generating AI-powered summaries for articles.
    
    Coordinates between SummarizationAgent and repositories to generate
    exam-focused summaries and persist them to the database.
    
    Demonstrates:
    - Dependency Inversion Principle (depends on abstractions: agent, repositories)
    - Single Responsibility Principle (only handles summarization orchestration)
    - Error handling for production readiness
    
    Attributes:
        _summarization_agent (SummarizationAgent): Agent for AI summarization
        _article_repo (ArticleRepository): Repository for article data access
        _summary_repo (SummaryRepository): Repository for summary persistence
    """
    
    def __init__(
        self,
        summarization_agent: SummarizationAgent,
        article_repository: ArticleRepository,
        summary_repository: SummaryRepository
    ):
        """
        Initialize the summarization service with dependencies.
        
        Uses dependency injection to receive agent and repository instances,
        demonstrating the Dependency Inversion Principle.
        
        Args:
            summarization_agent: Agent for AI-powered summarization
            article_repository: Repository for article data access
            summary_repository: Repository for summary persistence
        """
        self._summarization_agent = summarization_agent
        self._article_repo = article_repository
        self._summary_repo = summary_repository
        logger.info("SummarizationService initialized")
    
    def summarize_articles(
        self,
        article_ids: Optional[List[int]] = None,
        limit: Optional[int] = None,
        skip_existing: bool = True
    ) -> Dict[str, int]:
        """
        Generate summaries for multiple articles in batch.
        
        If article_ids is provided, summarizes those specific articles.
        Otherwise, summarizes categorized articles that don't have summaries yet.
        
        Args:
            article_ids: Optional list of specific article IDs to summarize
            limit: Maximum number of articles to process (optional)
            skip_existing: If True, skip articles that already have summaries
            
        Returns:
            Dictionary with statistics:
            - 'total_processed': Total articles processed
            - 'successfully_summarized': Articles successfully summarized
            - 'skipped': Articles skipped (already have summaries)
            - 'failed': Articles that failed summarization
            
        Example:
            >>> service = SummarizationService(agent, article_repo, summary_repo)
            >>> stats = service.summarize_articles(limit=100)
            >>> print(f"Summarized {stats['successfully_summarized']} articles")
        """
        logger.info("Starting batch summarization")
        
        # Get articles to summarize
        if article_ids:
            articles = [
                self._article_repo.find_by_id(article_id)
                for article_id in article_ids
            ]
            articles = [a for a in articles if a is not None]
        else:
            # Get categorized articles (category_id is not None)
            # This could be optimized with a dedicated repository method
            all_articles = self._article_repo.find_all()
            articles = [a for a in all_articles if a.category_id is not None]
            
            if limit:
                articles = articles[:limit]
        
        logger.info(f"Found {len(articles)} articles to process")
        
        # Statistics tracking
        total_processed = 0
        successfully_summarized = 0
        skipped = 0
        failed = 0
        
        # Summarize each article
        for article in articles:
            try:
                # Skip if summary already exists
                if skip_existing and self._summary_repo.exists_for_article(article.id):
                    skipped += 1
                    total_processed += 1
                    logger.debug(f"Skipping article {article.id} (summary exists)")
                    continue
                
                self._summarize_article(article)
                successfully_summarized += 1
                total_processed += 1
                
                if total_processed % 10 == 0:
                    logger.info(f"Progress: {total_processed}/{len(articles)} articles")
                    
            except Exception as e:
                failed += 1
                total_processed += 1
                logger.error(
                    f"Failed to summarize article {article.id}: {str(e)}",
                    exc_info=True
                )
                # Continue with other articles even if one fails
                continue
        
        # Return statistics
        stats = {
            'total_processed': total_processed,
            'successfully_summarized': successfully_summarized,
            'skipped': skipped,
            'failed': failed
        }
        
        logger.info(f"Summarization complete: {stats}")
        return stats
    
    def _summarize_article(self, article: Article) -> None:
        """
        Generate summary for a single article and persist to database.
        
        Calls the SummarizationAgent to generate the summary,
        then creates a Summary entity and stores it in the database.
        
        Args:
            article: The article entity to summarize
            
        Raises:
            AgentException: If summarization fails
            Exception: If database operation fails
        """
        logger.debug(f"Summarizing article {article.id}: {article.title[:50]}...")
        
        # Get category name for context
        category_name = article.category.name if article.category else 'General'
        
        # Prepare input for agent
        input_data = {
            'title': article.title,
            'content': article.content,
            'category': category_name,
            'source_type': article.source.source_type.value if article.source else 'unknown'
        }
        
        # Call summarization agent
        try:
            result: SummaryResult = self._summarization_agent.execute(input_data)
        except AgentException as e:
            logger.error(f"Agent failed for article {article.id}: {str(e)}")
            raise
        
        # Check if summary already exists (update) or create new
        existing_summary = self._summary_repo.find_by_article_id(article.id)
        
        if existing_summary:
            # Update existing summary
            self._update_summary_entity(existing_summary, result)
            self._summary_repo.update(existing_summary)
            logger.debug(f"Updated summary for article {article.id}")
        else:
            # Create new summary entity
            summary = self._create_summary_entity(article.id, result)
            self._summary_repo.create(summary)
            logger.debug(f"Created summary for article {article.id}")
    
    def _create_summary_entity(
        self,
        article_id: int,
        result: SummaryResult
    ) -> Summary:
        """
        Create a Summary ORM entity from summarization result.
        
        Converts SummaryResult Pydantic model to SQLAlchemy Summary model.
        
        Args:
            article_id: The article ID this summary belongs to
            result: Summarization result from agent
            
        Returns:
            Summary entity ready for database insertion
        """
        # Serialize lists to JSON strings
        possible_questions_json = json.dumps(result.possible_questions)
        key_facts_json = json.dumps(result.key_facts)
        
        summary = Summary(
            article_id=article_id,
            summary_text=result.main_summary,
            exam_relevance=result.why_important,
            prelims_relevance=result.prelims_relevance,
            mains_relevance=result.mains_relevance,
            possible_questions=possible_questions_json,
            key_facts=key_facts_json
        )
        
        return summary
    
    def _update_summary_entity(
        self,
        summary: Summary,
        result: SummaryResult
    ) -> None:
        """
        Update an existing Summary entity with new result.
        
        Args:
            summary: Existing summary entity to update
            result: New summarization result
        """
        # Serialize lists to JSON strings
        possible_questions_json = json.dumps(result.possible_questions)
        key_facts_json = json.dumps(result.key_facts)
        
        summary.summary_text = result.main_summary
        summary.exam_relevance = result.why_important
        summary.prelims_relevance = result.prelims_relevance
        summary.mains_relevance = result.mains_relevance
        summary.possible_questions = possible_questions_json
        summary.key_facts = key_facts_json
    
    def summarize_single_article(self, article_id: int) -> SummaryResult:
        """
        Generate summary for a single article by ID.
        
        Useful for testing or re-summarizing specific articles.
        
        Args:
            article_id: The article ID to summarize
            
        Returns:
            SummaryResult with summary details
            
        Raises:
            ValueError: If article not found or not categorized
            AgentException: If summarization fails
        """
        article = self._article_repo.find_by_id(article_id)
        
        if article is None:
            raise ValueError(f"Article with ID {article_id} not found")
        
        if article.category_id is None:
            raise ValueError(
                f"Article {article_id} must be categorized before summarization"
            )
        
        logger.info(f"Summarizing single article: {article.id}")
        
        # Get category name
        category_name = article.category.name if article.category else 'General'
        
        # Prepare input
        input_data = {
            'title': article.title,
            'content': article.content,
            'category': category_name,
            'source_type': article.source.source_type.value if article.source else 'unknown'
        }
        
        # Call agent
        result = self._summarization_agent.execute(input_data)
        
        # Check if summary exists
        existing_summary = self._summary_repo.find_by_article_id(article.id)
        
        if existing_summary:
            # Update existing
            self._update_summary_entity(existing_summary, result)
            self._summary_repo.update(existing_summary)
            logger.info(f"Updated summary for article {article.id}")
        else:
            # Create new
            summary = self._create_summary_entity(article.id, result)
            self._summary_repo.create(summary)
            logger.info(f"Created summary for article {article.id}")
        
        return result
    
    def get_summary_for_article(self, article_id: int) -> Optional[Summary]:
        """
        Retrieve existing summary for an article.
        
        Args:
            article_id: The article ID
            
        Returns:
            Summary entity if exists, None otherwise
        """
        return self._summary_repo.find_by_article_id(article_id)
    
    def regenerate_summaries_for_category(
        self,
        category_name: str,
        limit: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Regenerate summaries for all articles in a category.
        
        Useful for improving summaries after model updates.
        
        Args:
            category_name: Name of category to regenerate summaries for
            limit: Maximum number of articles to process
            
        Returns:
            Dictionary with statistics (same format as summarize_articles)
            
        Raises:
            ValueError: If category not found
        """
        from app.database.repositories.category_repository import CategoryRepository
        
        category_repo = CategoryRepository()
        category_id = category_repo.get_category_id_by_name(category_name)
        
        if category_id is None:
            raise ValueError(f"Category '{category_name}' not found")
        
        logger.info(f"Regenerating summaries for category: {category_name}")
        
        # Get articles in this category
        articles = self._article_repo.find_by_category(category_id, limit=limit)
        
        # Summarize with skip_existing=False to force regeneration
        article_ids = [article.id for article in articles]
        return self.summarize_articles(article_ids=article_ids, skip_existing=False)
