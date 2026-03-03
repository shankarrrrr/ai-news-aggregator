"""
Database models for the Competitive Exam Intelligence System.

This module defines SQLAlchemy ORM models for storing exam-relevant content,
implementing proper relationships, indexes, and the Repository Pattern.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column, String, DateTime, Text, Integer, Float, Boolean,
    ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum


Base = declarative_base()


class TimestampMixin:
    """
    Mixin class providing timestamp fields for all models.
    
    Demonstrates OOP principle: Composition over inheritance for shared behavior.
    
    Attributes:
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SourceType(str, Enum):
    """Enumeration of content source types."""
    YOUTUBE = "youtube"
    PIB = "pib"
    GOVERNMENT_SCHEMES = "government_schemes"


class Source(Base, TimestampMixin):
    """
    Model representing content sources (YouTube channels, PIB, government portals).
    
    Implements Single Responsibility Principle: Only manages source metadata.
    
    Attributes:
        id: Primary key
        name: Human-readable source name
        source_type: Type of source (youtube, pib, government_schemes)
        url: Base URL or identifier for the source
        is_active: Whether this source is currently being scraped
        metadata: JSON field for source-specific configuration
        articles: Relationship to articles from this source
    """
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    source_type = Column(SQLEnum(SourceType), nullable=False)
    url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    source_metadata = Column(Text, nullable=True)  # JSON string for flexibility
    
    # Relationships
    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Source(id={self.id}, name='{self.name}', type='{self.source_type}')>"


class Category(Base, TimestampMixin):
    """
    Model representing exam-relevant content categories.
    
    Categories: Polity, Economy, International Relations, Science & Tech,
    Environment & Ecology, Defence & Security, Government Schemes, Social Issues.
    
    Attributes:
        id: Primary key
        name: Category name (unique)
        description: Category description
        articles: Relationship to articles in this category
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    articles = relationship("Article", back_populates="category")
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"


class Article(Base, TimestampMixin):
    """
    Model representing scraped articles/content.
    
    Central entity linking sources, categories, summaries, and rankings.
    Demonstrates proper use of foreign keys and relationships.
    
    Attributes:
        id: Primary key
        title: Article title
        content: Full article content/transcript
        url: Original article URL (unique for duplicate detection)
        published_at: Original publication timestamp
        source_id: Foreign key to Source
        category_id: Foreign key to Category (assigned by CategorizationAgent)
        secondary_categories: Comma-separated secondary category names
        metadata: JSON field for article-specific data
        source: Relationship to Source
        category: Relationship to Category
        summary: Relationship to Summary (one-to-one)
        ranking: Relationship to Ranking (one-to-one)
    """
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    secondary_categories = Column(String(200), nullable=True)  # Comma-separated
    article_metadata = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    source = relationship("Source", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    summary = relationship("Summary", back_populates="article", uselist=False, cascade="all, delete-orphan")
    ranking = relationship("Ranking", back_populates="article", uselist=False, cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_article_published_at", "published_at"),
        Index("idx_article_category_id", "category_id"),
        Index("idx_article_source_id", "source_id"),
        Index("idx_article_url", "url"),
    )
    
    def __repr__(self) -> str:
        return f"<Article(id={self.id}, title='{self.title[:50]}...', source_id={self.source_id})>"


class Summary(Base, TimestampMixin):
    """
    Model representing AI-generated summaries for articles.
    
    Stores exam-focused summaries with prelims/mains relevance.
    
    Attributes:
        id: Primary key
        article_id: Foreign key to Article (one-to-one)
        summary_text: Main summary content
        exam_relevance: Why important for exam preparation
        prelims_relevance: Relevance for preliminary exam
        mains_relevance: Relevance for main exam
        possible_questions: Suggested exam questions (JSON array)
        key_facts: Important facts to remember (JSON array)
        article: Relationship to Article
    """
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, unique=True)
    summary_text = Column(Text, nullable=False)
    exam_relevance = Column(Text, nullable=True)
    prelims_relevance = Column(Text, nullable=True)
    mains_relevance = Column(Text, nullable=True)
    possible_questions = Column(Text, nullable=True)  # JSON array
    key_facts = Column(Text, nullable=True)  # JSON array
    
    # Relationships
    article = relationship("Article", back_populates="summary")
    
    def __repr__(self) -> str:
        return f"<Summary(id={self.id}, article_id={self.article_id})>"


class Ranking(Base, TimestampMixin):
    """
    Model representing exam relevance rankings for articles.
    
    Stores scores calculated by ranking strategies (UPSC, SSC, Banking).
    
    Attributes:
        id: Primary key
        article_id: Foreign key to Article (one-to-one)
        score: Relevance score (0.0 to 10.0)
        exam_type: Exam type used for ranking (UPSC, SSC, Banking)
        reasoning: Explanation of the score
        factors: JSON object with individual factor scores
        article: Relationship to Article
    """
    __tablename__ = "rankings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, unique=True)
    score = Column(Float, nullable=False)
    exam_type = Column(String(50), nullable=False)
    reasoning = Column(Text, nullable=True)
    factors = Column(Text, nullable=True)  # JSON object
    
    # Relationships
    article = relationship("Article", back_populates="ranking")
    
    # Index for performance (top-N queries)
    __table_args__ = (
        Index("idx_ranking_score", "score"),
    )
    
    def __repr__(self) -> str:
        return f"<Ranking(id={self.id}, article_id={self.article_id}, score={self.score})>"


class UserProfile(Base, TimestampMixin):
    """
    Model representing user profiles for future extensibility.
    
    Allows personalization of content ranking and filtering.
    Currently not used but included for future features.
    
    Attributes:
        id: Primary key
        email: User email (unique)
        exam_type: Primary exam type (UPSC, SSC, Banking, etc.)
        preferred_categories: Comma-separated category preferences
        notification_enabled: Whether to send email notifications
        metadata: JSON field for additional preferences
    """
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    exam_type = Column(String(50), nullable=True)
    preferred_categories = Column(String(500), nullable=True)  # Comma-separated
    notification_enabled = Column(Boolean, default=True, nullable=False)
    user_metadata = Column(Text, nullable=True)  # JSON string
    
    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, email='{self.email}', exam_type='{self.exam_type}')>"


# Legacy models (kept for backward compatibility during migration)
class YouTubeVideo(Base):
    """Legacy model for YouTube videos (pre-transformation)."""
    __tablename__ = "youtube_videos"
    
    video_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    description = Column(Text)
    transcript = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class OpenAIArticle(Base):
    """Legacy model for OpenAI articles (pre-transformation)."""
    __tablename__ = "openai_articles"
    
    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnthropicArticle(Base):
    """Legacy model for Anthropic articles (pre-transformation)."""
    __tablename__ = "anthropic_articles"
    
    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)
    markdown = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Digest(Base):
    """Legacy model for digests (pre-transformation)."""
    __tablename__ = "digests"
    
    id = Column(String, primary_key=True)
    article_type = Column(String, nullable=False)
    article_id = Column(String, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
