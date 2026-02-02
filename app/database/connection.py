import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

def get_database_url() -> str:
    """
    Get database URL from environment.
    Supports both DATABASE_URL (Render) and individual components (local).
    """
    # Check for DATABASE_URL first (Render/production)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Fall back to individual components (local development)
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ai_news_aggregator")
    
    # For Windows, explicitly use 127.0.0.1 instead of localhost to avoid socket issues
    if host == "localhost":
        host = "127.0.0.1"
    
    # URL-encode the password to handle special characters like @
    password_encoded = quote_plus(password)
    
    return f"postgresql://{user}:{password_encoded}@{host}:{port}/{db}"

def get_engine():
    """
    Create SQLAlchemy engine with connection pooling for production.
    """
    database_url = get_database_url()
    
    # Connection pool settings for production reliability
    # For Windows, add connect_args to force TCP/IP connection
    connect_args = {}
    if os.name == 'nt':  # Windows
        connect_args = {'host': '127.0.0.1'}
    
    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections after 1 hour
        echo=False,
        connect_args=connect_args
    )

# Global engine and session factory
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Get a new database session."""
    return SessionLocal()

