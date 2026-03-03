"""
Ranking Service for scoring article exam relevance.

This module implements the Service Layer Pattern for coordinating
article ranking using the RankingAgent with strategy selection.

Demonstrates:
- Service Layer Pattern (business logic coordination)
- Strategy Pattern (runtime strategy selection)
- Dependency Injection (depends on abstractions)
- Error handling and logging
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging
import json

from app.agent.ranking_agent import RankingAgent
from app.agent.abstract_agent import AgentException
from app.database.repositories.article_repository import ArticleRepository
from app.database.repositories.ranking_repository import RankingRepository
from app.database.models import Article, Ranking
from app.services.ranking.abstract_ranking_strategy import ArticleMetadata
from app.services.ranking.upsc_ranking_strategy import UPSCRankingStrategy
from app.services.ranking.ssc_ranking_strategy import SSCRankingStrategy
from app.services.ranking.banking_ranking_strategy import BankingRankingStrategy


logger = logging.getLogger(__name__)


class RankingService:
    """
    Service for ranking articles by exam relevance.
    
    Coordinates between RankingAgent and repositories to score articles
    using exam-specific ranking strategies and persist rankings to database.
    
    Demonstrates:
    - Dependency Inversion Principle (depends on abstractions: agent, repositories)
    - Strategy Pattern (selects appropriate ranking strategy based on exam type)
    - Single Responsibility Principle (only handles ranking orchestration)
    - Error handling for production readiness
    
    Attributes:
        _ranking_agent (RankingAgent): Agent for AI-enhanced ranking
        _article_repo (ArticleRepository): Repository for article data access
        _ranking_repo (RankingRepository): Repository for ranking persistence
    """
    
    # Available exam types
    EXAM_TYPES = ["UPSC", "SSC", "Banking"]
    
    def __init__(
        self,
        ranking_agent: RankingAgent,
        article_repository: ArticleRepository,
        ranking_repository: RankingRepository
    ):
        """
        Initialize the ranking service with dependencies.
        
        Uses dependency injection to receive agent and repository instances,
        demonstrating the Dependency Inversion Principle.
        
        Args:
            ranking_agent: Agent for AI-enhanced ranking
            article_repository: Repository for article data access
            ranking_repository: Repository for ranking persistence
        """
        self._ranking_agent = ranking_agent
        self._article_repo = article_repository
        self._ranking_repo = ranking_repository
        logger.info("RankingService initialized")
    
    def rank_articles(
        self,
        exam_type: str,
        article_ids: Optional[List[int]] = None,
        limit: Optional[int] = None,
        skip_existing: bool = True,
        use_ai_enhancement: bool = False
    ) -> Dict[str, int]:
        """
        Rank multiple articles for a specific exam type.
        
        If article_ids is provided, ranks those specific articles.
        Otherwise, ranks summarized articles that don't have rankings yet.
        
        Args:
            exam_type: Exam type (UPSC, SSC, Banking)
            article_ids: Optional list of specific article IDs to rank
            limit: Maximum number of articles to process (optional)
            skip_existing: If True, skip articles that already have rankings
            use_ai_enhancement: Enable AI enhancement for borderline scores
            
        Returns:
            Dictionary with statistics:
            - 'total_processed': Total articles processed
            - 'successfully_ranked': Articles successfully ranked
            - 'skipped': Articles skipped (already have rankings)
            - 'failed': Articles that failed ranking
            
        Example:
            >>> service = RankingService(agent, article_repo, ranking_repo)
            >>> stats = service.rank_articles(exam_type="UPSC", limit=100)
            >>> print(f"Ranked {stats['successfully_ranked']} articles")
        """
        # Validate exam type
        if exam_type not in self.EXAM_TYPES:
            raise ValueError(
                f"Invalid exam type '{exam_type}'. "
                f"Must be one of: {', '.join(self.EXAM_TYPES)}"
            )
        
        logger.info(f"Starting batch ranking for {exam_type}")
        
        # Select appropriate strategy
        strategy = self._select_strategy(exam_type)
        self._ranking_agent.set_strategy(strategy)
        
        # Get articles to rank
        if article_ids:
            articles = [
                self._article_repo.find_by_id(article_id)
                for article_id in article_ids
            ]
            articles = [a for a in articles if a is not None]
        else:
            # Get articles that have summaries (summary relationship exists)
            # This could be optimized with a dedicated repository method
            all_articles = self._article_repo.find_all()
            articles = [a for a in all_articles if a.summary is not None]
            
            if limit:
                articles = articles[:limit]
        
        logger.info(f"Found {len(articles)} articles to process")
        
        # Statistics tracking
        total_processed = 0
        successfully_ranked = 0
        skipped = 0
        failed = 0
        
        # Rank each article
        for article in articles:
            try:
                # Skip if ranking already exists
                if skip_existing and self._ranking_repo.exists_for_article(article.id):
                    skipped += 1
                    total_processed += 1
                    logger.debug(f"Skipping article {article.id} (ranking exists)")
                    continue
                
                self._rank_article(article, exam_type, use_ai_enhancement)
                successfully_ranked += 1
                total_processed += 1
                
                if total_processed % 10 == 0:
                    logger.info(f"Progress: {total_processed}/{len(articles)} articles")
                    
            except Exception as e:
                failed += 1
                total_processed += 1
                logger.error(
                    f"Failed to rank article {article.id}: {str(e)}",
                    exc_info=True
                )
                # Continue with other articles even if one fails
                continue
        
        # Return statistics
        stats = {
            'total_processed': total_processed,
            'successfully_ranked': successfully_ranked,
            'skipped': skipped,
            'failed': failed
        }
        
        logger.info(f"Ranking complete: {stats}")
        return stats
    
    def _select_strategy(self, exam_type: str):
        """
        Select appropriate ranking strategy based on exam type.
        
        Demonstrates the Strategy Pattern - different algorithms
        are selected based on context (exam type).
        
        Args:
            exam_type: Exam type (UPSC, SSC, Banking)
            
        Returns:
            Appropriate ranking strategy instance
            
        Raises:
            ValueError: If exam type is not supported
        """
        if exam_type == "UPSC":
            return UPSCRankingStrategy()
        elif exam_type == "SSC":
            return SSCRankingStrategy()
        elif exam_type == "Banking":
            return BankingRankingStrategy()
        else:
            raise ValueError(f"Unsupported exam type: {exam_type}")
    
    def _rank_article(
        self,
        article: Article,
        exam_type: str,
        use_ai_enhancement: bool
    ) -> None:
        """
        Rank a single article and persist to database.
        
        Calls the RankingAgent to score the article,
        then creates or updates a Ranking entity.
        
        Args:
            article: The article entity to rank
            exam_type: Exam type for ranking
            use_ai_enhancement: Enable AI enhancement
            
        Raises:
            AgentException: If ranking fails
            Exception: If database operation fails
        """
        logger.debug(f"Ranking article {article.id}: {article.title[:50]}...")
        
        # Prepare metadata for ranking
        metadata = ArticleMetadata(
            category=article.category.name if article.category else 'General',
            source_type=article.source.source_type.value if article.source else 'unknown',
            published_at=article.published_at,
            content_length=len(article.content),
            keywords=self._extract_keywords(article)
        )
        
        # Prepare input for agent
        input_data = {
            'content': article.content,
            'metadata': metadata,
            'use_ai_enhancement': use_ai_enhancement
        }
        
        # Call ranking agent
        try:
            result = self._ranking_agent.execute(input_data)
        except AgentException as e:
            logger.error(f"Agent failed for article {article.id}: {str(e)}")
            raise
        
        # Check if ranking already exists (update) or create new
        existing_ranking = self._ranking_repo.find_by_article_id(article.id)
        
        if existing_ranking:
            # Update existing ranking
            self._update_ranking_entity(existing_ranking, result, exam_type)
            self._ranking_repo.update(existing_ranking)
            logger.debug(f"Updated ranking for article {article.id}")
        else:
            # Create new ranking entity
            ranking = self._create_ranking_entity(article.id, result, exam_type)
            self._ranking_repo.create(ranking)
            logger.debug(f"Created ranking for article {article.id}")
    
    def _extract_keywords(self, article: Article) -> List[str]:
        """
        Extract keywords from article for ranking context.
        
        Simple keyword extraction from title and metadata.
        
        Args:
            article: Article entity
            
        Returns:
            List of keywords
        """
        keywords = []
        
        # Extract from title (split and filter)
        title_words = article.title.lower().split()
        keywords.extend([w for w in title_words if len(w) > 4])
        
        # Extract from metadata if available
        if article.metadata:
            try:
                metadata = json.loads(article.metadata)
                if 'keywords' in metadata:
                    keywords.extend(metadata['keywords'])
            except json.JSONDecodeError:
                pass
        
        # Return unique keywords (limit to 10)
        return list(set(keywords))[:10]
    
    def _create_ranking_entity(
        self,
        article_id: int,
        result,
        exam_type: str
    ) -> Ranking:
        """
        Create a Ranking ORM entity from ranking result.
        
        Converts RankingResult to SQLAlchemy Ranking model.
        
        Args:
            article_id: The article ID this ranking belongs to
            result: Ranking result from agent
            exam_type: Exam type used for ranking
            
        Returns:
            Ranking entity ready for database insertion
        """
        # Serialize factors to JSON string
        factors_json = json.dumps(result.factors)
        
        ranking = Ranking(
            article_id=article_id,
            score=result.score,
            exam_type=exam_type,
            reasoning=result.reasoning,
            factors=factors_json
        )
        
        return ranking
    
    def _update_ranking_entity(
        self,
        ranking: Ranking,
        result,
        exam_type: str
    ) -> None:
        """
        Update an existing Ranking entity with new result.
        
        Args:
            ranking: Existing ranking entity to update
            result: New ranking result
            exam_type: Exam type used for ranking
        """
        # Serialize factors to JSON string
        factors_json = json.dumps(result.factors)
        
        ranking.score = result.score
        ranking.exam_type = exam_type
        ranking.reasoning = result.reasoning
        ranking.factors = factors_json
    
    def rank_single_article(
        self,
        article_id: int,
        exam_type: str,
        use_ai_enhancement: bool = False
    ):
        """
        Rank a single article by ID.
        
        Useful for testing or re-ranking specific articles.
        
        Args:
            article_id: The article ID to rank
            exam_type: Exam type (UPSC, SSC, Banking)
            use_ai_enhancement: Enable AI enhancement
            
        Returns:
            RankingResult with ranking details
            
        Raises:
            ValueError: If article not found or not summarized
            AgentException: If ranking fails
        """
        # Validate exam type
        if exam_type not in self.EXAM_TYPES:
            raise ValueError(
                f"Invalid exam type '{exam_type}'. "
                f"Must be one of: {', '.join(self.EXAM_TYPES)}"
            )
        
        article = self._article_repo.find_by_id(article_id)
        
        if article is None:
            raise ValueError(f"Article with ID {article_id} not found")
        
        if article.summary is None:
            raise ValueError(
                f"Article {article_id} must be summarized before ranking"
            )
        
        logger.info(f"Ranking single article: {article.id} for {exam_type}")
        
        # Select strategy
        strategy = self._select_strategy(exam_type)
        self._ranking_agent.set_strategy(strategy)
        
        # Prepare metadata
        metadata = ArticleMetadata(
            category=article.category.name if article.category else 'General',
            source_type=article.source.source_type.value if article.source else 'unknown',
            published_at=article.published_at,
            content_length=len(article.content),
            keywords=self._extract_keywords(article)
        )
        
        # Prepare input
        input_data = {
            'content': article.content,
            'metadata': metadata,
            'use_ai_enhancement': use_ai_enhancement
        }
        
        # Call agent
        result = self._ranking_agent.execute(input_data)
        
        # Check if ranking exists
        existing_ranking = self._ranking_repo.find_by_article_id(article.id)
        
        if existing_ranking:
            # Update existing
            self._update_ranking_entity(existing_ranking, result, exam_type)
            self._ranking_repo.update(existing_ranking)
            logger.info(f"Updated ranking for article {article.id}")
        else:
            # Create new
            ranking = self._create_ranking_entity(article.id, result, exam_type)
            self._ranking_repo.create(ranking)
            logger.info(f"Created ranking for article {article.id}")
        
        return result
    
    def get_top_articles(
        self,
        n: int,
        exam_type: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> List[tuple[Ranking, Article]]:
        """
        Get top N ranked articles.
        
        Retrieves the highest-scoring articles, optionally filtered
        by exam type and minimum score.
        
        Args:
            n: Number of top articles to retrieve
            exam_type: Filter by exam type (optional)
            min_score: Minimum score threshold (optional)
            
        Returns:
            List of (Ranking, Article) tuples
        """
        return self._ranking_repo.find_top_n_with_articles(
            n=n,
            exam_type=exam_type,
            min_score=min_score
        )
    
    def rerank_articles_for_exam(
        self,
        exam_type: str,
        limit: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Re-rank all articles for a specific exam type.
        
        Useful for updating rankings after strategy improvements.
        
        Args:
            exam_type: Exam type to re-rank for
            limit: Maximum number of articles to process
            
        Returns:
            Dictionary with statistics (same format as rank_articles)
        """
        logger.info(f"Re-ranking articles for {exam_type}")
        
        # Get all articles with summaries
        all_articles = self._article_repo.find_all()
        articles = [a for a in all_articles if a.summary is not None]
        
        if limit:
            articles = articles[:limit]
        
        # Rank with skip_existing=False to force re-ranking
        article_ids = [article.id for article in articles]
        return self.rank_articles(
            exam_type=exam_type,
            article_ids=article_ids,
            skip_existing=False
        )
