"""
Database migration: Transform AI News Aggregator to Competitive Exam Intelligence System

This migration script transforms the existing database schema to support
the competitive exam intelligence system with proper relationships,
indexes, and seed data.

Migration: 001_transform_to_exam_system
Created: 2024-03-03
"""

import logging
from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, Text, 
    DateTime, Float, Boolean, ForeignKey, Index, text
)
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


# Exam categories for competitive exams
EXAM_CATEGORIES = [
    {
        'name': 'Polity',
        'description': 'Constitution, governance, political science topics',
        'priority': 1
    },
    {
        'name': 'Economy', 
        'description': 'Economic policies, budget, financial markets',
        'priority': 2
    },
    {
        'name': 'International Relations',
        'description': 'Foreign policy, international organizations, treaties',
        'priority': 3
    },
    {
        'name': 'Science & Tech',
        'description': 'Scientific developments, technology, innovation',
        'priority': 4
    },
    {
        'name': 'Environment & Ecology',
        'description': 'Environmental issues, climate change, conservation',
        'priority': 5
    },
    {
        'name': 'Defence & Security',
        'description': 'Defense policies, security issues, military affairs',
        'priority': 6
    },
    {
        'name': 'Government Schemes',
        'description': 'Welfare programs, government initiatives, policies',
        'priority': 7
    },
    {
        'name': 'Social Issues',
        'description': 'Social problems, demographics, cultural topics',
        'priority': 8
    }
]


# Content sources for the system
CONTENT_SOURCES = [
    {
        'name': 'YouTube Exam Channels',
        'source_type': 'youtube',
        'base_url': 'https://www.youtube.com',
        'is_active': True,
        'description': 'Exam preparation YouTube channels with transcripts'
    },
    {
        'name': 'Press Information Bureau',
        'source_type': 'pib',
        'base_url': 'https://pib.gov.in',
        'is_active': True,
        'description': 'Official government press releases'
    },
    {
        'name': 'Government Schemes Portal',
        'source_type': 'government_schemes',
        'base_url': 'https://www.india.gov.in',
        'is_active': True,
        'description': 'Government welfare schemes and programs'
    }
]


class DatabaseMigration:
    """
    Database migration handler for transforming to exam system.
    
    Handles forward migration, rollback, and verification procedures.
    """
    
    def __init__(self, database_url: str):
        """
        Initialize migration handler.
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.metadata = MetaData()
    
    def execute_migration(self) -> bool:
        """
        Execute the complete migration.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting database migration: 001_transform_to_exam_system")
        
        try:
            with self.engine.begin() as conn:
                # Create new tables
                self._create_categories_table(conn)
                self._create_sources_table(conn)
                self._create_summaries_table(conn)
                self._create_rankings_table(conn)
                self._create_user_profiles_table(conn)
                
                # Modify existing articles table
                self._modify_articles_table(conn)
                
                # Create indexes
                self._create_indexes(conn)
                
                # Seed data
                self._seed_categories(conn)
                self._seed_sources(conn)
                
                # Record migration
                self._record_migration(conn)
                
            logger.info("Migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}", exc_info=True)
            return False
    
    def rollback_migration(self) -> bool:
        """
        Rollback the migration changes.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting migration rollback: 001_transform_to_exam_system")
        
        try:
            with self.engine.begin() as conn:
                # Drop new tables (in reverse order due to foreign keys)
                self._drop_table_if_exists(conn, 'user_profiles')
                self._drop_table_if_exists(conn, 'rankings')
                self._drop_table_if_exists(conn, 'summaries')
                self._drop_table_if_exists(conn, 'sources')
                self._drop_table_if_exists(conn, 'categories')
                
                # Revert articles table changes
                self._revert_articles_table(conn)
                
                # Remove migration record
                self._remove_migration_record(conn)
                
            logger.info("Migration rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration rollback failed: {str(e)}", exc_info=True)
            return False
    
    def verify_migration(self) -> bool:
        """
        Verify migration was applied correctly.
        
        Returns:
            True if verification passes, False otherwise
        """
        logger.info("Verifying migration: 001_transform_to_exam_system")
        
        try:
            with self.engine.connect() as conn:
                # Check all tables exist
                required_tables = [
                    'categories', 'sources', 'summaries', 
                    'rankings', 'user_profiles', 'articles'
                ]
                
                for table_name in required_tables:
                    result = conn.execute(text(
                        f"SELECT COUNT(*) FROM information_schema.tables "
                        f"WHERE table_name = '{table_name}'"
                    ))
                    if result.scalar() == 0:
                        logger.error(f"Table {table_name} not found")
                        return False
                
                # Check seed data
                result = conn.execute(text("SELECT COUNT(*) FROM categories"))
                if result.scalar() != len(EXAM_CATEGORIES):
                    logger.error("Categories not seeded correctly")
                    return False
                
                result = conn.execute(text("SELECT COUNT(*) FROM sources"))
                if result.scalar() != len(CONTENT_SOURCES):
                    logger.error("Sources not seeded correctly")
                    return False
                
                # Check indexes exist
                required_indexes = [
                    'idx_articles_published_at',
                    'idx_articles_category_id',
                    'idx_articles_source_id',
                    'idx_rankings_score'
                ]
                
                for index_name in required_indexes:
                    result = conn.execute(text(
                        f"SELECT COUNT(*) FROM pg_indexes "
                        f"WHERE indexname = '{index_name}'"
                    ))
                    if result.scalar() == 0:
                        logger.warning(f"Index {index_name} not found")
                
            logger.info("Migration verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration verification failed: {str(e)}", exc_info=True)
            return False
    
    def _create_categories_table(self, conn) -> None:
        """Create the categories table."""
        logger.info("Creating categories table")
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
    
    def _create_sources_table(self, conn) -> None:
        """Create the sources table."""
        logger.info("Creating sources table")
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sources (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                source_type VARCHAR(50) NOT NULL,
                base_url VARCHAR(500),
                is_active BOOLEAN DEFAULT TRUE,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, source_type)
            )
        """))
    
    def _create_summaries_table(self, conn) -> None:
        """Create the summaries table."""
        logger.info("Creating summaries table")
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS summaries (
                id SERIAL PRIMARY KEY,
                article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
                summary_text TEXT NOT NULL,
                exam_relevance TEXT,
                prelims_relevance TEXT,
                mains_relevance TEXT,
                possible_questions TEXT,
                key_facts TEXT,
                word_count INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(article_id)
            )
        """))
    
    def _create_rankings_table(self, conn) -> None:
        """Create the rankings table."""
        logger.info("Creating rankings table")
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rankings (
                id SERIAL PRIMARY KEY,
                article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
                exam_type VARCHAR(50) NOT NULL,
                score DECIMAL(4,2) NOT NULL CHECK (score >= 0.0 AND score <= 10.0),
                reasoning TEXT,
                factors JSONB,
                strategy_used VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(article_id, exam_type)
            )
        """))
    
    def _create_user_profiles_table(self, conn) -> None:
        """Create the user_profiles table for future extensibility."""
        logger.info("Creating user_profiles table")
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) UNIQUE,
                exam_preferences JSONB,
                notification_settings JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
    
    def _modify_articles_table(self, conn) -> None:
        """Add foreign key columns to existing articles table."""
        logger.info("Modifying articles table")
        
        # Check if columns already exist
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'articles' AND column_name IN ('category_id', 'source_id')
        """))
        existing_columns = [row[0] for row in result]
        
        # Add category_id column if it doesn't exist
        if 'category_id' not in existing_columns:
            conn.execute(text("""
                ALTER TABLE articles 
                ADD COLUMN category_id INTEGER REFERENCES categories(id)
            """))
        
        # Add source_id column if it doesn't exist
        if 'source_id' not in existing_columns:
            conn.execute(text("""
                ALTER TABLE articles 
                ADD COLUMN source_id INTEGER REFERENCES sources(id)
            """))
        
        # Add metadata column for additional data
        if 'metadata' not in existing_columns:
            conn.execute(text("""
                ALTER TABLE articles 
                ADD COLUMN metadata JSONB DEFAULT '{}'
            """))
    
    def _create_indexes(self, conn) -> None:
        """Create performance indexes."""
        logger.info("Creating database indexes")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_articles_category_id ON articles(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_articles_source_id ON articles(source_id)",
            "CREATE INDEX IF NOT EXISTS idx_rankings_score ON rankings(score DESC)",
            "CREATE INDEX IF NOT EXISTS idx_rankings_exam_type ON rankings(exam_type)",
            "CREATE INDEX IF NOT EXISTS idx_summaries_article_id ON summaries(article_id)",
            "CREATE INDEX IF NOT EXISTS idx_sources_type_active ON sources(source_type, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_categories_priority ON categories(priority)"
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
            except Exception as e:
                logger.warning(f"Failed to create index: {str(e)}")
    
    def _seed_categories(self, conn) -> None:
        """Seed the categories table with exam categories."""
        logger.info("Seeding categories table")
        
        for category in EXAM_CATEGORIES:
            conn.execute(text("""
                INSERT INTO categories (name, description, priority)
                VALUES (:name, :description, :priority)
                ON CONFLICT (name) DO UPDATE SET
                    description = EXCLUDED.description,
                    priority = EXCLUDED.priority,
                    updated_at = CURRENT_TIMESTAMP
            """), category)
    
    def _seed_sources(self, conn) -> None:
        """Seed the sources table with content sources."""
        logger.info("Seeding sources table")
        
        for source in CONTENT_SOURCES:
            conn.execute(text("""
                INSERT INTO sources (name, source_type, base_url, is_active, description)
                VALUES (:name, :source_type, :base_url, :is_active, :description)
                ON CONFLICT (name, source_type) DO UPDATE SET
                    base_url = EXCLUDED.base_url,
                    is_active = EXCLUDED.is_active,
                    description = EXCLUDED.description,
                    updated_at = CURRENT_TIMESTAMP
            """), source)
    
    def _record_migration(self, conn) -> None:
        """Record migration in migrations table."""
        # Create migrations table if it doesn't exist
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) NOT NULL UNIQUE,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                rollback_sql TEXT
            )
        """))
        
        # Record this migration
        conn.execute(text("""
            INSERT INTO migrations (migration_name, rollback_sql)
            VALUES ('001_transform_to_exam_system', 'See rollback_migration() method')
            ON CONFLICT (migration_name) DO NOTHING
        """))
    
    def _drop_table_if_exists(self, conn, table_name: str) -> None:
        """Drop table if it exists."""
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
    
    def _revert_articles_table(self, conn) -> None:
        """Revert changes to articles table."""
        logger.info("Reverting articles table changes")
        
        try:
            conn.execute(text("ALTER TABLE articles DROP COLUMN IF EXISTS category_id"))
            conn.execute(text("ALTER TABLE articles DROP COLUMN IF EXISTS source_id"))
            conn.execute(text("ALTER TABLE articles DROP COLUMN IF EXISTS metadata"))
        except Exception as e:
            logger.warning(f"Failed to revert articles table: {str(e)}")
    
    def _remove_migration_record(self, conn) -> None:
        """Remove migration record."""
        conn.execute(text("""
            DELETE FROM migrations WHERE migration_name = '001_transform_to_exam_system'
        """))


def run_migration(database_url: str) -> bool:
    """
    Run the database migration.
    
    Args:
        database_url: Database connection URL
        
    Returns:
        True if successful, False otherwise
    """
    migration = DatabaseMigration(database_url)
    
    if migration.execute_migration():
        if migration.verify_migration():
            logger.info("Migration completed and verified successfully")
            return True
        else:
            logger.error("Migration verification failed")
            return False
    else:
        logger.error("Migration execution failed")
        return False


def rollback_migration(database_url: str) -> bool:
    """
    Rollback the database migration.
    
    Args:
        database_url: Database connection URL
        
    Returns:
        True if successful, False otherwise
    """
    migration = DatabaseMigration(database_url)
    return migration.rollback_migration()


if __name__ == "__main__":
    import os
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        success = rollback_migration(database_url)
        action = "rollback"
    else:
        success = run_migration(database_url)
        action = "migration"
    
    if success:
        logger.info(f"Database {action} completed successfully")
        sys.exit(0)
    else:
        logger.error(f"Database {action} failed")
        sys.exit(1)