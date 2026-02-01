#!/usr/bin/env python3
"""
Production-ready pipeline runner with fail-fast validation and CLI options.
"""
import os
import sys
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv

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
    """Fail-fast environment validation."""
    required_vars = {
        "GEMINI_API_KEY": "Google Gemini API key for LLM operations",
        "DATABASE_URL": "PostgreSQL connection string",
    }
    
    email_vars = {
        "SMTP_HOST": "SMTP server hostname",
        "SMTP_PORT": "SMTP server port",
        "SMTP_USERNAME": "SMTP username",
        "SMTP_PASSWORD": "SMTP password",
        "EMAIL_FROM": "Sender email address",
        "EMAIL_TO": "Recipient email address",
    }
    
    missing = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing.append(f"  - {var}: {description}")
    
    if missing:
        logger.error("Missing required environment variables:")
        for msg in missing:
            logger.error(msg)
        sys.exit(1)
    
    # Check email vars (warning only)
    missing_email = []
    for var, description in email_vars.items():
        if not os.getenv(var):
            missing_email.append(f"  - {var}: {description}")
    
    if missing_email:
        logger.warning("Missing email configuration (email sending will be disabled):")
        for msg in missing_email:
            logger.warning(msg)
    
    logger.info("✓ Environment validation passed")


def test_database_connection():
    """Test database connectivity."""
    try:
        from app.database.connection import get_engine
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✓ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="AI News Aggregator Pipeline - Production Runner"
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
        help="Number of top articles to include in email (default: 10)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline without sending email"
    )
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Skip email generation and sending"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip environment validation (not recommended)"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("AI News Aggregator - Production Pipeline")
    logger.info("=" * 70)
    logger.info(f"Environment: {os.getenv('ENV', 'development')}")
    logger.info(f"Hours lookback: {args.hours}")
    logger.info(f"Top N articles: {args.top_n}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"No email: {args.no_email}")
    logger.info("=" * 70)
    
    # Validation
    if not args.skip_validation:
        validate_environment()
        if not test_database_connection():
            logger.error("Database connection test failed. Exiting.")
            sys.exit(1)
    
    # Import and run pipeline
    try:
        from app.daily_runner import run_daily_pipeline
        
        # Override email settings if needed
        if args.dry_run or args.no_email:
            os.environ["SKIP_EMAIL"] = "true"
            logger.info("Email sending disabled")
        
        result = run_daily_pipeline(hours=args.hours, top_n=args.top_n)
        
        if result["success"]:
            logger.info("✓ Pipeline completed successfully")
            sys.exit(0)
        else:
            logger.error("✗ Pipeline completed with errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Pipeline failed with exception: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
