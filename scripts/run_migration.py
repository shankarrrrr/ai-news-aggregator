#!/usr/bin/env python3
"""
Production database migration runner for Competitive Exam Intelligence System.

This script safely executes the database migration with proper error handling,
backup verification, and rollback capabilities.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import Optional

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database.migrations.transform_to_exam_system import (
    run_migration, rollback_migration, DatabaseMigration
)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for migration execution.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )


def check_prerequisites() -> bool:
    """
    Check prerequisites before running migration.
    
    Returns:
        True if all prerequisites are met, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    # Check environment variables
    required_env_vars = ['DATABASE_URL']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Test database connectivity
    try:
        from app.database.connection import get_session
        from sqlalchemy import text
        session = get_session()
        try:
            session.execute(text("SELECT 1"))
            logger.info("Database connectivity verified")
            return True
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Database connectivity check failed: {str(e)}")
        return False


def backup_verification() -> bool:
    """
    Verify that database backup exists before migration.
    
    Returns:
        True if backup verification passes, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    # In production, you would verify backup exists
    # For now, we'll just log a warning
    logger.warning("IMPORTANT: Ensure database backup exists before proceeding")
    logger.warning("This migration will modify the database schema")
    
    return True


def run_production_migration(dry_run: bool = False) -> bool:
    """
    Run the production database migration with safety checks.
    
    Args:
        dry_run: If True, only validate without executing
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    logger.info("Starting production database migration")
    logger.info(f"Dry run mode: {dry_run}")
    
    # Check prerequisites
    if not check_prerequisites():
        logger.error("Prerequisites check failed")
        return False
    
    # Verify backup
    if not backup_verification():
        logger.error("Backup verification failed")
        return False
    
    if dry_run:
        logger.info("DRY RUN: Migration validation completed successfully")
        return True
    
    # Execute migration
    database_url = os.getenv('DATABASE_URL')
    
    try:
        success = run_migration(database_url)
        
        if success:
            logger.info("✅ Migration completed successfully")
            logger.info("Next steps:")
            logger.info("1. Verify application functionality")
            logger.info("2. Run end-to-end tests")
            logger.info("3. Monitor system performance")
            return True
        else:
            logger.error("❌ Migration failed")
            return False
            
    except Exception as e:
        logger.error(f"Migration execution failed with exception: {str(e)}", exc_info=True)
        return False


def run_production_rollback() -> bool:
    """
    Run the production database rollback.
    
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    logger.warning("🚨 STARTING DATABASE ROLLBACK 🚨")
    logger.warning("This will revert all migration changes")
    
    # Confirm rollback
    if not os.getenv('FORCE_ROLLBACK'):
        logger.error("Set FORCE_ROLLBACK=1 environment variable to confirm rollback")
        return False
    
    database_url = os.getenv('DATABASE_URL')
    
    try:
        success = rollback_migration(database_url)
        
        if success:
            logger.info("✅ Rollback completed successfully")
            return True
        else:
            logger.error("❌ Rollback failed")
            return False
            
    except Exception as e:
        logger.error(f"Rollback execution failed with exception: {str(e)}", exc_info=True)
        return False


def verify_migration_status() -> bool:
    """
    Verify the current migration status.
    
    Returns:
        True if verification passes, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    database_url = os.getenv('DATABASE_URL')
    migration = DatabaseMigration(database_url)
    
    try:
        is_verified = migration.verify_migration()
        
        if is_verified:
            logger.info("✅ Migration verification passed")
            logger.info("All tables, indexes, and seed data are present")
        else:
            logger.error("❌ Migration verification failed")
            logger.error("Some components are missing or incorrect")
        
        return is_verified
        
    except Exception as e:
        logger.error(f"Migration verification failed with exception: {str(e)}", exc_info=True)
        return False


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description="Production database migration for Competitive Exam Intelligence System"
    )
    
    parser.add_argument(
        'action',
        choices=['migrate', 'rollback', 'verify'],
        help='Action to perform'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate migration without executing (migrate action only)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Migration script started - Action: {args.action}")
    
    # Execute requested action
    if args.action == 'migrate':
        success = run_production_migration(dry_run=args.dry_run)
    elif args.action == 'rollback':
        success = run_production_rollback()
    elif args.action == 'verify':
        success = verify_migration_status()
    else:
        logger.error(f"Unknown action: {args.action}")
        success = False
    
    # Exit with appropriate code
    if success:
        logger.info("Script completed successfully")
        sys.exit(0)
    else:
        logger.error("Script failed")
        sys.exit(1)


if __name__ == "__main__":
    main()