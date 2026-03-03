#!/usr/bin/env python3
"""
Competitive Exam Intelligence System - Production Pipeline Runner

This script runs the complete exam intelligence pipeline with comprehensive
configuration validation, dependency injection, and error handling.

Usage:
    python scripts/run_pipeline.py [hours] [top_n] [options]

Examples:
    python scripts/run_pipeline.py 24 10 --exam-type UPSC
    python scripts/run_pipeline.py 48 15 --exam-type SSC --dry-run
    python scripts/run_pipeline.py --exam-type Banking --no-email
"""
import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Add parent directory to path for app imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def validate_environment():
    """
    Comprehensive environment validation using the new config validator.
    
    Uses the ConfigValidator class for thorough validation of all
    system configuration including API keys, database, and business logic.
    """
    try:
        from app.config_validator import validate_configuration
        validate_configuration()
        logger.info("✓ Configuration validation passed")
    except Exception as e:
        logger.error(f"✗ Configuration validation failed: {e}")
        sys.exit(1)


def initialize_dependencies():
    """
    Initialize all pipeline dependencies using dependency injection.
    
    Creates and configures all services, agents, repositories, and factories
    required for the exam intelligence pipeline.
    
    Returns:
        Tuple of (pipeline_instance, services_dict) for execution and cleanup
    """
    try:
        # Import all required components
        from app.agent.abstract_agent import AgentConfig
        from app.agent.categorization_agent import CategorizationAgent
        from app.agent.summarization_agent import SummarizationAgent
        from app.agent.ranking_agent import RankingAgent
        from app.agent.digest_agent import DigestAgent
        
        from app.scrapers.scraper_factory import ScraperFactory
        
        from app.services.ranking.upsc_ranking_strategy import UPSCRankingStrategy
        from app.services.ranking.ssc_ranking_strategy import SSCRankingStrategy
        from app.services.ranking.banking_ranking_strategy import BankingRankingStrategy
        
        from app.database.repositories.article_repository import ArticleRepository
        from app.database.repositories.summary_repository import SummaryRepository
        from app.database.repositories.ranking_repository import RankingRepository
        from app.database.repositories.category_repository import CategoryRepository
        from app.database.repositories.source_repository import SourceRepository
        
        from app.services.scraping_service import ScrapingService
        from app.services.categorization_service import CategorizationService
        from app.services.summarization_service import SummarizationService
        from app.services.ranking_service import RankingService
        from app.services.digest_generation_service import DigestGenerationService
        
        from app.pipeline.pipeline import Pipeline
        
        logger.info("Initializing pipeline dependencies...")
        
        # Initialize agent configuration
        agent_config = AgentConfig(
            model_name="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=2048,
            api_key=os.getenv('GEMINI_API_KEY')
        )
        
        # Initialize agents
        categorization_agent = CategorizationAgent(agent_config)
        summarization_agent = SummarizationAgent(agent_config)
        digest_agent = DigestAgent(agent_config)
        
        # Initialize ranking strategies
        ranking_strategies = {
            'UPSC': UPSCRankingStrategy(),
            'SSC': SSCRankingStrategy(),
            'Banking': BankingRankingStrategy()
        }
        
        # Initialize ranking agent with default strategy
        ranking_agent = RankingAgent(
            config=agent_config,
            strategy=ranking_strategies['UPSC']  # Default strategy
        )
        
        # Initialize repositories
        article_repo = ArticleRepository()
        summary_repo = SummaryRepository()
        ranking_repo = RankingRepository()
        category_repo = CategoryRepository()
        source_repo = SourceRepository()
        
        # Initialize scraper factory
        scraper_factory = ScraperFactory()
        
        # Initialize services
        scraping_service = ScrapingService(
            scraper_factory=scraper_factory,
            article_repository=article_repo,
            source_repository=source_repo
        )
        
        categorization_service = CategorizationService(
            categorization_agent=categorization_agent,
            article_repository=article_repo,
            category_repository=category_repo
        )
        
        summarization_service = SummarizationService(
            summarization_agent=summarization_agent,
            article_repository=article_repo,
            summary_repository=summary_repo
        )
        
        ranking_service = RankingService(
            ranking_agent=ranking_agent,
            article_repository=article_repo,
            ranking_repository=ranking_repo
        )
        
        digest_service = DigestGenerationService(
            digest_agent=digest_agent,
            ranking_repository=ranking_repo
        )
        
        # Initialize pipeline
        pipeline = Pipeline(
            scraping_service=scraping_service,
            categorization_service=categorization_service,
            summarization_service=summarization_service,
            ranking_service=ranking_service,
            digest_service=digest_service,
            logger=logger
        )
        
        services = {
            'scraping': scraping_service,
            'categorization': categorization_service,
            'summarization': summarization_service,
            'ranking': ranking_service,
            'digest': digest_service
        }
        
        logger.info("✓ Pipeline dependencies initialized successfully")
        return pipeline, services
        
    except ImportError as e:
        logger.error(f"✗ Failed to import required modules: {e}")
        logger.error("Ensure all pipeline components are implemented")
        sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Failed to initialize dependencies: {e}")
        sys.exit(1)


def test_database_connection():
    """Test database connectivity."""
    try:
        from app.database.connection import get_engine
        from sqlalchemy import text
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


def display_digest_output(digest_content: str, top_n: int) -> None:
    """
    Display the generated digest output in a formatted way.
    
    Args:
        digest_content: The generated digest content
        top_n: Number of articles requested
    """
    if not digest_content:
        logger.warning("No digest content generated")
        return
    
    print("\n" + "=" * 80)
    print(f"COMPETITIVE EXAM INTELLIGENCE DIGEST - TOP {top_n} ARTICLES")
    print("=" * 80)
    print(digest_content)
    print("=" * 80)


def send_email_digest(digest_content: str, exam_type: str, hours: int, top_n: int) -> bool:
    """
    Send the digest via email if email is configured.
    
    Args:
        digest_content: The digest content to send
        exam_type: Type of exam for subject line
        hours: Hours lookback for subject line
        top_n: Number of articles for subject line
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        from app.services.email import send_email_to_self
        
        subject = f"Exam Intelligence Digest - {exam_type} - {hours}h - Top {top_n}"
        send_email_to_self(subject, digest_content)
        logger.info("✓ Digest email sent successfully")
        return True
    except ImportError:
        logger.warning("Email service not available")
        return False
    except Exception as e:
        logger.error(f"✗ Failed to send digest email: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Competitive Exam Intelligence System - Production Pipeline Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 24 10 --exam-type UPSC
  %(prog)s 48 15 --exam-type SSC --dry-run
  %(prog)s --exam-type Banking --no-email
        """
    )
    parser.add_argument(
        "hours",
        type=int,
        nargs="?",
        default=24,
        help="Number of hours to look back for articles (default: 24)"
    )
    parser.add_argument(
        "top_n",
        type=int,
        nargs="?",
        default=10,
        help="Number of top articles to include in digest (default: 10)"
    )
    parser.add_argument(
        "--exam-type",
        choices=["UPSC", "SSC", "Banking"],
        default="UPSC",
        help="Type of exam for ranking strategy (default: UPSC)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline without database writes or email sending"
    )
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Skip email generation and sending (still writes to database)"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip environment validation (not recommended for production)"
    )
    
    args = parser.parse_args()
    
    # Validate exam type
    exam_type = args.exam_type.upper()
    
    logger.info("=" * 80)
    logger.info("COMPETITIVE EXAM INTELLIGENCE SYSTEM - PRODUCTION PIPELINE")
    logger.info("=" * 80)
    logger.info(f"Environment: {os.getenv('ENV', 'development')}")
    logger.info(f"Exam Type: {exam_type}")
    logger.info(f"Hours lookback: {args.hours}")
    logger.info(f"Top N articles: {args.top_n}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"No email: {args.no_email}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 80)
    
    # Validation phase
    if not args.skip_validation:
        logger.info("Phase 1: Configuration Validation")
        validate_environment()
        
        logger.info("Phase 2: Database Connection Test")
        if not test_database_connection():
            logger.error("Database connection test failed. Exiting.")
            sys.exit(1)
    else:
        logger.warning("Skipping validation - not recommended for production")
    
    # Dependency initialization phase
    logger.info("Phase 3: Dependency Initialization")
    try:
        pipeline, services = initialize_dependencies()
    except Exception as e:
        logger.error(f"Failed to initialize pipeline dependencies: {e}")
        sys.exit(1)
    
    # Pipeline execution phase
    logger.info("Phase 4: Pipeline Execution")
    try:
        # Execute the pipeline
        result = pipeline.execute(
            hours=args.hours,
            top_n=args.top_n,
            exam_type=exam_type,
            dry_run=args.dry_run
        )
        
        # Display results
        logger.info("Phase 5: Results Processing")
        
        if result.success:
            logger.info("✓ Pipeline completed successfully")
            
            # Display digest output
            if result.digest_content:
                display_digest_output(result.digest_content, args.top_n)
            
            # Send email if configured and not disabled
            if not args.dry_run and not args.no_email and result.digest_content:
                logger.info("Phase 6: Email Delivery")
                email_sent = send_email_digest(
                    result.digest_content, 
                    exam_type, 
                    args.hours, 
                    args.top_n
                )
                if not email_sent:
                    logger.warning("Email delivery failed, but pipeline succeeded")
            elif args.dry_run:
                logger.info("Skipping email delivery (dry run mode)")
            elif args.no_email:
                logger.info("Skipping email delivery (--no-email flag)")
            else:
                logger.info("Skipping email delivery (no digest content)")
            
            # Final summary
            logger.info("\n" + "=" * 80)
            logger.info("PIPELINE EXECUTION SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Status: SUCCESS")
            logger.info(f"Execution Time: {result.execution_time_seconds:.2f} seconds")
            logger.info(f"Articles Scraped: {result.articles_scraped}")
            logger.info(f"Articles Categorized: {result.articles_categorized}")
            logger.info(f"Articles Summarized: {result.articles_summarized}")
            logger.info(f"Articles Ranked: {result.articles_ranked}")
            logger.info(f"Top Articles Selected: {result.top_articles_selected}")
            
            if result.errors:
                logger.info(f"Errors Encountered: {len(result.errors)}")
                for error in result.errors:
                    logger.warning(f"  - {error}")
            else:
                logger.info("No errors encountered")
            
            logger.info("=" * 80)
            sys.exit(0)
            
        else:
            logger.error("✗ Pipeline completed with failures")
            
            # Display error summary
            logger.error("\n" + "=" * 80)
            logger.error("PIPELINE FAILURE SUMMARY")
            logger.error("=" * 80)
            logger.error(f"Status: FAILED")
            logger.error(f"Execution Time: {result.execution_time_seconds:.2f} seconds")
            
            if result.errors:
                logger.error(f"Errors Encountered: {len(result.errors)}")
                for error in result.errors:
                    logger.error(f"  - {error}")
            
            logger.error("=" * 80)
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Pipeline failed with unexpected exception: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
