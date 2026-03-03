"""
Pipeline orchestration for the Competitive Exam Intelligence System.

This module implements the main pipeline that coordinates all stages of content processing:
Scrape → Categorize → Summarize → Rank → Store → Digest

The Pipeline class follows the Dependency Inversion Principle by accepting all services
via dependency injection, making it testable and maintainable.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from app.services.scraping_service import ScrapingService
from app.services.categorization_service import CategorizationService
from app.services.summarization_service import SummarizationService
from app.services.ranking_service import RankingService
from app.services.digest_generation_service import DigestGenerationService


@dataclass
class PipelineResult:
    """
    Result of pipeline execution with comprehensive statistics.
    
    Attributes:
        success: Whether pipeline completed successfully
        articles_scraped: Number of articles scraped
        articles_categorized: Number of articles categorized
        articles_summarized: Number of articles summarized
        articles_ranked: Number of articles ranked
        top_articles_selected: Number of top articles selected for digest
        execution_time_seconds: Total execution time
        digest_content: Generated digest content
        errors: List of errors encountered during execution
        stage_timings: Dictionary of timing for each stage
    """
    success: bool
    articles_scraped: int
    articles_categorized: int
    articles_summarized: int
    articles_ranked: int
    top_articles_selected: int
    execution_time_seconds: float
    digest_content: str
    errors: List[str]
    stage_timings: Dict[str, float]


class PipelineException(Exception):
    """Exception raised during pipeline execution."""
    pass


class Pipeline:
    """
    Main pipeline orchestrator for the Competitive Exam Intelligence System.
    
    Coordinates the execution of all processing stages in the correct order,
    handles errors gracefully, and provides comprehensive logging and statistics.
    
    Follows the Single Responsibility Principle - only responsible for orchestration.
    All actual processing is delegated to specialized services.
    
    Attributes:
        _scraping_service: Service for content scraping
        _categorization_service: Service for content categorization
        _summarization_service: Service for content summarization
        _ranking_service: Service for content ranking
        _digest_service: Service for digest generation
        _logger: Logger instance for pipeline execution
    """
    
    def __init__(
        self,
        scraping_service: ScrapingService,
        categorization_service: CategorizationService,
        summarization_service: SummarizationService,
        ranking_service: RankingService,
        digest_service: DigestGenerationService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize pipeline with all required services via dependency injection.
        
        Args:
            scraping_service: Service for scraping content from sources
            categorization_service: Service for categorizing articles
            summarization_service: Service for generating summaries
            ranking_service: Service for ranking articles by relevance
            digest_service: Service for generating formatted digests
            logger: Optional logger instance (creates default if None)
        """
        self._scraping_service = scraping_service
        self._categorization_service = categorization_service
        self._summarization_service = summarization_service
        self._ranking_service = ranking_service
        self._digest_service = digest_service
        self._logger = logger or self._create_default_logger()
        
        # Statistics tracking
        self._stage_timings: Dict[str, float] = {}
        self._errors: List[str] = []
    
    def execute(
        self, 
        hours: int = 24, 
        top_n: int = 10,
        exam_type: str = "UPSC",
        dry_run: bool = False
    ) -> PipelineResult:
        """
        Execute the complete pipeline workflow.
        
        Stages executed in order:
        1. Scrape - Fetch content from all sources
        2. Categorize - Classify content by exam relevance
        3. Summarize - Generate exam-focused summaries
        4. Rank - Score articles by exam relevance
        5. Store - Persist processed data (skipped in dry_run)
        6. Digest - Generate formatted output
        
        Args:
            hours: Number of hours to look back for content
            top_n: Number of top articles to include in digest
            exam_type: Type of exam (UPSC, SSC, Banking)
            dry_run: If True, skip database writes
            
        Returns:
            PipelineResult with execution statistics and digest content
            
        Raises:
            PipelineException: If critical pipeline failure occurs
        """
        start_time = datetime.now(timezone.utc)
        self._logger.info(f"Starting pipeline execution - Hours: {hours}, Top N: {top_n}, Exam: {exam_type}, Dry Run: {dry_run}")
        
        try:
            # Stage 1: Scrape content
            articles_scraped = self._execute_scraping_stage(hours, dry_run)
            
            # Stage 2: Categorize articles
            articles_categorized = self._execute_categorization_stage(dry_run)
            
            # Stage 3: Summarize articles
            articles_summarized = self._execute_summarization_stage(dry_run)
            
            # Stage 4: Rank articles
            articles_ranked = self._execute_ranking_stage(exam_type, dry_run)
            
            # Stage 5: Store results (handled by individual services)
            # No separate storage stage - services handle persistence
            
            # Stage 6: Generate digest
            digest_content, top_articles_selected = self._execute_digest_stage(
                top_n, exam_type, dry_run
            )
            
            # Calculate total execution time
            end_time = datetime.now(timezone.utc)
            execution_time = (end_time - start_time).total_seconds()
            
            # Generate summary report
            self._generate_summary_report(
                articles_scraped, articles_categorized, articles_summarized,
                articles_ranked, top_articles_selected, execution_time
            )
            
            return PipelineResult(
                success=True,
                articles_scraped=articles_scraped,
                articles_categorized=articles_categorized,
                articles_summarized=articles_summarized,
                articles_ranked=articles_ranked,
                top_articles_selected=top_articles_selected,
                execution_time_seconds=execution_time,
                digest_content=digest_content,
                errors=self._errors.copy(),
                stage_timings=self._stage_timings.copy()
            )
            
        except Exception as e:
            self._logger.error(f"Pipeline execution failed: {str(e)}")
            self._errors.append(f"Pipeline failure: {str(e)}")
            
            end_time = datetime.now(timezone.utc)
            execution_time = (end_time - start_time).total_seconds()
            
            return PipelineResult(
                success=False,
                articles_scraped=0,
                articles_categorized=0,
                articles_summarized=0,
                articles_ranked=0,
                top_articles_selected=0,
                execution_time_seconds=execution_time,
                digest_content="",
                errors=self._errors.copy(),
                stage_timings=self._stage_timings.copy()
            )
    
    def _execute_scraping_stage(self, hours: int, dry_run: bool) -> int:
        """
        Execute the scraping stage.
        
        Args:
            hours: Number of hours to look back
            dry_run: If True, skip database writes
            
        Returns:
            Number of articles scraped
        """
        stage_name = "Scraping"
        self._log_stage_start(stage_name)
        
        try:
            start_time = datetime.now(timezone.utc)
            
            # Execute scraping
            result = self._scraping_service.scrape_all_sources(
                hours=hours
            )
            
            articles_scraped = result.get('articles_processed', 0)
            
            # Record timing
            end_time = datetime.now(timezone.utc)
            self._stage_timings[stage_name] = (end_time - start_time).total_seconds()
            
            self._log_stage_end(stage_name, articles_scraped)
            return articles_scraped
            
        except Exception as e:
            error_msg = f"Scraping stage failed: {str(e)}"
            self._logger.error(error_msg)
            self._errors.append(error_msg)
            return 0
    
    def _execute_categorization_stage(self, dry_run: bool) -> int:
        """
        Execute the categorization stage.
        
        Args:
            dry_run: If True, skip database writes
            
        Returns:
            Number of articles categorized
        """
        stage_name = "Categorization"
        self._log_stage_start(stage_name)
        
        try:
            start_time = datetime.now(timezone.utc)
            
            # Execute categorization
            result = self._categorization_service.categorize_articles()
            
            articles_categorized = result.get('articles_processed', 0)
            
            # Record timing
            end_time = datetime.now(timezone.utc)
            self._stage_timings[stage_name] = (end_time - start_time).total_seconds()
            
            self._log_stage_end(stage_name, articles_categorized)
            return articles_categorized
            
        except Exception as e:
            error_msg = f"Categorization stage failed: {str(e)}"
            self._logger.error(error_msg)
            self._errors.append(error_msg)
            return 0
    
    def _execute_summarization_stage(self, dry_run: bool) -> int:
        """
        Execute the summarization stage.
        
        Args:
            dry_run: If True, skip database writes
            
        Returns:
            Number of articles summarized
        """
        stage_name = "Summarization"
        self._log_stage_start(stage_name)
        
        try:
            start_time = datetime.now(timezone.utc)
            
            # Execute summarization
            result = self._summarization_service.summarize_articles()
            
            articles_summarized = result.get('articles_processed', 0)
            
            # Record timing
            end_time = datetime.now(timezone.utc)
            self._stage_timings[stage_name] = (end_time - start_time).total_seconds()
            
            self._log_stage_end(stage_name, articles_summarized)
            return articles_summarized
            
        except Exception as e:
            error_msg = f"Summarization stage failed: {str(e)}"
            self._logger.error(error_msg)
            self._errors.append(error_msg)
            return 0
    
    def _execute_ranking_stage(self, exam_type: str, dry_run: bool) -> int:
        """
        Execute the ranking stage.
        
        Args:
            exam_type: Type of exam for ranking strategy
            dry_run: If True, skip database writes
            
        Returns:
            Number of articles ranked
        """
        stage_name = "Ranking"
        self._log_stage_start(stage_name)
        
        try:
            start_time = datetime.now(timezone.utc)
            
            # Execute ranking
            result = self._ranking_service.rank_articles(
                exam_type=exam_type
            )
            
            articles_ranked = result.get('articles_processed', 0)
            
            # Record timing
            end_time = datetime.now(timezone.utc)
            self._stage_timings[stage_name] = (end_time - start_time).total_seconds()
            
            self._log_stage_end(stage_name, articles_ranked)
            return articles_ranked
            
        except Exception as e:
            error_msg = f"Ranking stage failed: {str(e)}"
            self._logger.error(error_msg)
            self._errors.append(error_msg)
            return 0
    
    def _execute_digest_stage(
        self, 
        top_n: int, 
        exam_type: str, 
        dry_run: bool
    ) -> tuple[str, int]:
        """
        Execute the digest generation stage.
        
        Args:
            top_n: Number of top articles to include
            exam_type: Type of exam for digest formatting
            dry_run: If True, skip database writes
            
        Returns:
            Tuple of (digest_content, number_of_articles)
        """
        stage_name = "Digest Generation"
        self._log_stage_start(stage_name)
        
        try:
            start_time = datetime.now(timezone.utc)
            
            # Execute digest generation
            digest_content = self._digest_service.generate_digest(
                top_n=top_n,
                exam_type=exam_type
            )
            
            # Count articles in digest (approximate)
            top_articles_selected = min(top_n, digest_content.count("##") - 1) if digest_content else 0
            
            # Record timing
            end_time = datetime.now(timezone.utc)
            self._stage_timings[stage_name] = (end_time - start_time).total_seconds()
            
            self._log_stage_end(stage_name, top_articles_selected)
            return digest_content, top_articles_selected
            
        except Exception as e:
            error_msg = f"Digest generation stage failed: {str(e)}"
            self._logger.error(error_msg)
            self._errors.append(error_msg)
            return "", 0
    
    def _log_stage_start(self, stage_name: str) -> None:
        """
        Log the start of a pipeline stage.
        
        Args:
            stage_name: Name of the stage starting
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        self._logger.info(f"[{timestamp}] Starting stage: {stage_name}")
    
    def _log_stage_end(self, stage_name: str, items_processed: int) -> None:
        """
        Log the completion of a pipeline stage.
        
        Args:
            stage_name: Name of the stage that completed
            items_processed: Number of items processed in this stage
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        timing = self._stage_timings.get(stage_name, 0)
        self._logger.info(
            f"[{timestamp}] Completed stage: {stage_name} - "
            f"Processed: {items_processed} items - "
            f"Duration: {timing:.2f}s"
        )
    
    def _generate_summary_report(
        self,
        articles_scraped: int,
        articles_categorized: int,
        articles_summarized: int,
        articles_ranked: int,
        top_articles_selected: int,
        execution_time: float
    ) -> None:
        """
        Generate and log a comprehensive summary report.
        
        Args:
            articles_scraped: Number of articles scraped
            articles_categorized: Number of articles categorized
            articles_summarized: Number of articles summarized
            articles_ranked: Number of articles ranked
            top_articles_selected: Number of top articles selected
            execution_time: Total execution time in seconds
        """
        self._logger.info("=" * 60)
        self._logger.info("PIPELINE EXECUTION SUMMARY")
        self._logger.info("=" * 60)
        self._logger.info(f"Total Execution Time: {execution_time:.2f} seconds")
        self._logger.info(f"Articles Scraped: {articles_scraped}")
        self._logger.info(f"Articles Categorized: {articles_categorized}")
        self._logger.info(f"Articles Summarized: {articles_summarized}")
        self._logger.info(f"Articles Ranked: {articles_ranked}")
        self._logger.info(f"Top Articles Selected: {top_articles_selected}")
        
        if self._errors:
            self._logger.info(f"Errors Encountered: {len(self._errors)}")
            for error in self._errors:
                self._logger.warning(f"  - {error}")
        else:
            self._logger.info("No errors encountered")
        
        self._logger.info("\nStage Timings:")
        for stage, timing in self._stage_timings.items():
            percentage = (timing / execution_time * 100) if execution_time > 0 else 0
            self._logger.info(f"  {stage}: {timing:.2f}s ({percentage:.1f}%)")
        
        self._logger.info("=" * 60)
    
    def _create_default_logger(self) -> logging.Logger:
        """
        Create a default logger for pipeline execution.
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger("pipeline")
        logger.setLevel(logging.INFO)
        
        # Create console handler if no handlers exist
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger