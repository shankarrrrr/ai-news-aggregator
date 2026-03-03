# Design Document: Competitive Exam Intelligence System

## Overview

### Purpose

This document provides a comprehensive technical design for transforming the existing "AI News Aggregator - Gemini Powered" system into an "AI-Powered Competitive Exam News Intelligence System". The transformation maintains all production infrastructure (Google Gemini 1.5 Flash API, PostgreSQL, Docker, Render deployment) while implementing strong Object-Oriented Programming (OOP) principles and design patterns suitable for academic documentation.

### System Context

The system aggregates, categorizes, summarizes, and ranks news content specifically relevant to competitive exam aspirants in India (UPSC, MPSC, SSC, Banking, NDA/CDS, State PSC). It replaces AI technology news sources with exam-relevant sources including:

- YouTube exam preparation channels (11 channels)
- Press Information Bureau (PIB) official releases
- Government schemes and policy announcements

### Key Design Goals

1. **Academic Excellence**: Demonstrate SOLID principles and design patterns
2. **Production Readiness**: Maintain existing deployment infrastructure
3. **Extensibility**: Enable easy addition of new sources and exam categories
4. **Maintainability**: Clear separation of concerns with layered architecture
5. **Type Safety**: Comprehensive type hints and validation

### Transformation Scope

**Retained Components**:
- Google Gemini 1.5 Flash API integration
- PostgreSQL database with SQLAlchemy ORM
- Docker containerization
- Render deployment configuration
- CLI-based pipeline execution

**New Components**:
- Exam-specific content scrapers (YouTube, PIB, Government Schemes)
- Exam category taxonomy (8 categories)
- Enhanced AI agents for exam-focused processing
- Ranking strategies for different exam types
- Repository pattern for data access
- Service layer for business logic


## Architecture

### High-Level Architecture

The system follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                           │
│                  (CLI Interface, Logging)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      Service Layer                               │
│  (ScrapingService, CategorizationService, SummarizationService,  │
│   RankingService, DigestGenerationService)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     Business Logic Layer                         │
│  (Scrapers: YouTube, PIB, GovSchemes)                           │
│  (Agents: Categorization, Summarization, Ranking, Digest)       │
│  (Strategies: UPSC, SSC, Banking Ranking)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Data Access Layer                             │
│  (Repositories: Article, Summary, Ranking, Category, Source)    │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     Data Storage Layer                           │
│              (PostgreSQL Database via SQLAlchemy)                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     External Services                             │
│  (Google Gemini API, YouTube RSS, PIB Website, Gov Portals)     │
└──────────────────────────────────────────────────────────────────┘
```

### Pipeline Architecture

The system implements a sequential processing pipeline:

```
┌──────────┐    ┌────────────┐    ┌────────────┐    ┌──────┐    ┌───────┐    ┌────────┐
│  Scrape  │───▶│ Categorize │───▶│ Summarize  │───▶│ Rank │───▶│ Store │───▶│ Digest │
└──────────┘    └────────────┘    └────────────┘    └──────┘    └───────┘    └────────┘
     │                │                  │              │            │             │
     ▼                ▼                  ▼              ▼            ▼             ▼
  YouTube          Gemini            Gemini         Strategy    PostgreSQL    Email/CLI
  PIB API          API               API            Pattern     via ORM       Output
  Gov Sites
```

**Pipeline Stages**:

1. **Scrape**: Fetch content from multiple sources (YouTube transcripts, PIB releases, government schemes)
2. **Categorize**: Classify content into exam-relevant categories using Gemini API
3. **Summarize**: Generate exam-focused summaries with prelims/mains relevance
4. **Rank**: Score articles by exam relevance using strategy pattern
5. **Store**: Persist processed data to PostgreSQL via repositories
6. **Digest**: Compile top-ranked articles into formatted output

### Component Interaction Diagram

```mermaid
graph TB
    CLI[CLI Pipeline Runner]
    
    subgraph Services
        SS[ScrapingService]
        CS[CategorizationService]
        SumS[SummarizationService]
        RS[RankingService]
        DS[DigestGenerationService]
    end
    
    subgraph Scrapers
        YS[YouTubeScraper]
        PS[PIBScraper]
        GS[GovSchemesScraper]
        SF[ScraperFactory]
    end
    
    subgraph Agents
        CA[CategorizationAgent]
        SA[SummarizationAgent]
        RA[RankingAgent]
        DA[DigestAgent]
    end
    
    subgraph Strategies
        URS[UPSCRankingStrategy]
        SRS[SSCRankingStrategy]
        BRS[BankingRankingStrategy]
    end
    
    subgraph Repositories
        AR[ArticleRepository]
        SR[SummaryRepository]
        RR[RankingRepository]
        CR[CategoryRepository]
        SoR[SourceRepository]
    end
    
    subgraph External
        Gemini[Gemini API]
        YT[YouTube RSS]
        PIB[PIB Website]
        DB[(PostgreSQL)]
    end
    
    CLI --> SS
    CLI --> CS
    CLI --> SumS
    CLI --> RS
    CLI --> DS
    
    SS --> SF
    SF --> YS
    SF --> PS
    SF --> GS
    
    YS --> YT
    PS --> PIB
    
    CS --> CA
    SumS --> SA
    RS --> RA
    DS --> DA
    
    CA --> Gemini
    SA --> Gemini
    RA --> URS
    RA --> SRS
    RA --> BRS
    DA --> Gemini
    
    SS --> AR
    CS --> AR
    CS --> CR
    SumS --> SR
    RS --> RR
    
    AR --> DB
    SR --> DB
    RR --> DB
    CR --> DB
    SoR --> DB
```


### Design Principles Applied

**SOLID Principles**:

1. **Single Responsibility Principle (SRP)**: Each class has one reason to change
   - Scrapers only fetch data
   - Agents only process with AI
   - Repositories only handle data access
   - Services only orchestrate workflows

2. **Open/Closed Principle (OCP)**: Open for extension, closed for modification
   - Abstract base classes allow new scrapers without modifying existing code
   - Strategy pattern allows new ranking algorithms without changing RankingAgent
   - Factory pattern allows new scraper types without modifying factory logic

3. **Liskov Substitution Principle (LSP)**: Subclasses are substitutable for base classes
   - Any AbstractScraper subclass can be used wherever AbstractScraper is expected
   - Any AbstractRankingStrategy can be injected into RankingAgent
   - All agents implement the same execute() interface

4. **Interface Segregation Principle (ISP)**: No client depends on unused methods
   - AbstractScraper defines only scraping interface
   - AbstractAgent defines only execution interface
   - Repositories define only data access methods they need

5. **Dependency Inversion Principle (DIP)**: Depend on abstractions, not concretions
   - Services depend on abstract repositories, not concrete implementations
   - RankingAgent depends on AbstractRankingStrategy, not concrete strategies
   - Pipeline depends on service interfaces, not implementations


## Components and Interfaces

### Abstract Base Classes

#### AbstractScraper

**Purpose**: Defines the interface for all content scrapers, ensuring consistent behavior across different sources.

**Design Pattern**: Template Method Pattern (defines algorithm structure, subclasses implement steps)

**Class Definition**:

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class ScrapedContent(BaseModel):
    """Data model for scraped content."""
    title: str
    content: str
    url: str
    published_at: datetime
    source_type: str
    metadata: dict = {}


class AbstractScraper(ABC):
    """
    Abstract base class for all content scrapers.
    
    Implements the Template Method pattern where the scraping algorithm
    structure is defined, but specific steps are implemented by subclasses.
    
    Attributes:
        _source_name (str): Name of the content source (private)
        _base_url (str): Base URL for the source (private)
        _timeout (int): Request timeout in seconds (private)
    """
    
    def __init__(self, source_name: str, base_url: str, timeout: int = 30):
        """
        Initialize the scraper with common configuration.
        
        Args:
            source_name: Human-readable name of the source
            base_url: Base URL for API or website
            timeout: Request timeout in seconds
        """
        self._source_name = source_name
        self._base_url = base_url
        self._timeout = timeout
    
    @property
    def source_name(self) -> str:
        """Get the source name (encapsulation)."""
        return self._source_name
    
    @abstractmethod
    def scrape(self, hours: int = 24) -> List[ScrapedContent]:
        """
        Scrape content from the source.
        
        This method must be implemented by all concrete scrapers.
        
        Args:
            hours: Number of hours to look back for content
            
        Returns:
            List of scraped content items
            
        Raises:
            ScraperException: If scraping fails
        """
        pass
    
    def _handle_network_error(self, error: Exception) -> None:
        """
        Common error handling for network failures.
        
        Args:
            error: The exception that occurred
        """
        # Log error with context
        print(f"Network error in {self._source_name}: {str(error)}")
    
    def validate_content(self, content: ScrapedContent) -> bool:
        """
        Validate scraped content meets minimum requirements.
        
        Args:
            content: Content to validate
            
        Returns:
            True if valid, False otherwise
        """
        return (
            len(content.title) > 0 and
            len(content.content) > 50 and
            content.url.startswith('http')
        )
```

**Key Design Decisions**:
- Private attributes (prefixed with `_`) enforce encapsulation
- Property decorator provides controlled read access
- Abstract method forces subclasses to implement scrape()
- Common validation logic prevents code duplication
- Pydantic models ensure type safety and validation


#### AbstractAgent

**Purpose**: Defines the interface for all AI-powered agents that process content using Gemini API.

**Design Pattern**: Strategy Pattern (agents are interchangeable strategies for content processing)

**Class Definition**:

```python
from abc import ABC, abstractmethod
from typing import Any, Optional
import google.generativeai as genai
from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Configuration for AI agents."""
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int = 2048
    api_key: str


class AbstractAgent(ABC):
    """
    Abstract base class for all AI-powered agents.
    
    Provides common Gemini API client initialization and error handling.
    Subclasses implement specific processing logic.
    
    Attributes:
        _config (AgentConfig): Agent configuration (private)
        _client (genai.GenerativeModel): Gemini API client (private)
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the agent with Gemini API configuration.
        
        Args:
            config: Agent configuration including API key
        """
        self._config = config
        genai.configure(api_key=config.api_key)
        self._client = genai.GenerativeModel(config.model_name)
    
    @property
    def model_name(self) -> str:
        """Get the model name being used."""
        return self._config.model_name
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """
        Execute the agent's processing logic.
        
        This method must be implemented by all concrete agents.
        
        Args:
            input_data: Input data to process (type varies by agent)
            
        Returns:
            Processed output (type varies by agent)
            
        Raises:
            AgentException: If processing fails
        """
        pass
    
    def _call_gemini_api(self, prompt: str) -> str:
        """
        Common method to call Gemini API with error handling.
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            API response text
            
        Raises:
            AgentException: If API call fails
        """
        try:
            response = self._client.generate_content(
                prompt,
                generation_config={
                    "temperature": self._config.temperature,
                    "max_output_tokens": self._config.max_tokens,
                }
            )
            return response.text
        except Exception as e:
            raise AgentException(f"Gemini API call failed: {str(e)}")
    
    def _parse_json_response(self, response: str) -> dict:
        """
        Parse JSON response from Gemini API.
        
        Args:
            response: JSON string from API
            
        Returns:
            Parsed dictionary
        """
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            raise


class AgentException(Exception):
    """Exception raised by agents during processing."""
    pass
```

**Key Design Decisions**:
- Encapsulates Gemini API client initialization
- Provides common error handling for API calls
- Abstract execute() method allows polymorphic agent usage
- JSON parsing handles both raw and markdown-wrapped responses
- Configuration object pattern for flexible initialization


#### AbstractRankingStrategy

**Purpose**: Defines the interface for ranking algorithms, enabling different scoring strategies for different exam types.

**Design Pattern**: Strategy Pattern (interchangeable ranking algorithms)

**Class Definition**:

```python
from abc import ABC, abstractmethod
from typing import Dict
from pydantic import BaseModel


class ArticleMetadata(BaseModel):
    """Metadata for ranking calculation."""
    category: str
    source_type: str
    published_at: datetime
    content_length: int
    keywords: List[str] = []


class RankingResult(BaseModel):
    """Result of ranking calculation."""
    score: float  # 0.0 to 10.0
    reasoning: str
    factors: Dict[str, float]  # Individual factor scores


class AbstractRankingStrategy(ABC):
    """
    Abstract base class for ranking strategies.
    
    Implements the Strategy pattern to allow different ranking algorithms
    for different exam types (UPSC, SSC, Banking, etc.).
    
    Attributes:
        _exam_type (str): Type of exam this strategy is for (private)
        _weights (Dict[str, float]): Scoring weights for factors (private)
    """
    
    def __init__(self, exam_type: str, weights: Dict[str, float]):
        """
        Initialize the ranking strategy.
        
        Args:
            exam_type: Type of exam (UPSC, SSC, Banking, etc.)
            weights: Dictionary of factor weights
        """
        self._exam_type = exam_type
        self._weights = weights
        self._validate_weights()
    
    @property
    def exam_type(self) -> str:
        """Get the exam type for this strategy."""
        return self._exam_type
    
    @abstractmethod
    def calculate_score(
        self, 
        content: str, 
        metadata: ArticleMetadata
    ) -> RankingResult:
        """
        Calculate relevance score for an article.
        
        This method must be implemented by all concrete strategies.
        
        Args:
            content: Article content text
            metadata: Article metadata for scoring
            
        Returns:
            RankingResult with score and reasoning
        """
        pass
    
    def _validate_weights(self) -> None:
        """Validate that weights sum to 1.0."""
        total = sum(self._weights.values())
        if not (0.99 <= total <= 1.01):  # Allow small floating point error
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def _calculate_freshness_score(self, published_at: datetime) -> float:
        """
        Calculate freshness score based on publication date.
        
        Args:
            published_at: Publication timestamp
            
        Returns:
            Score from 0.0 to 1.0 (newer = higher)
        """
        from datetime import datetime, timezone
        
        age_hours = (datetime.now(timezone.utc) - published_at).total_seconds() / 3600
        
        # Exponential decay: 1.0 at 0 hours, 0.5 at 24 hours, 0.25 at 48 hours
        return max(0.0, min(1.0, 2 ** (-age_hours / 24)))
    
    def _calculate_category_relevance(
        self, 
        category: str, 
        priority_categories: List[str]
    ) -> float:
        """
        Calculate category relevance score.
        
        Args:
            category: Article category
            priority_categories: List of high-priority categories for this exam
            
        Returns:
            Score from 0.0 to 1.0
        """
        if category in priority_categories:
            # Higher score for priority categories
            index = priority_categories.index(category)
            return 1.0 - (index * 0.1)  # First priority = 1.0, second = 0.9, etc.
        return 0.5  # Default score for non-priority categories
```

**Key Design Decisions**:
- Strategy pattern allows runtime selection of ranking algorithm
- Weight validation ensures scoring consistency
- Common helper methods reduce code duplication
- Encapsulated weights prevent external modification
- Pydantic models ensure type safety for inputs/outputs


### Concrete Scraper Implementations

#### YouTubeScraper

**Purpose**: Scrapes video transcripts from exam preparation YouTube channels.

**Inheritance**: Extends AbstractScraper

**Class Definition**:

```python
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


class YouTubeScraper(AbstractScraper):
    """
    Concrete scraper for YouTube exam preparation channels.
    
    Inherits from AbstractScraper and implements YouTube-specific
    scraping logic using RSS feeds and transcript API.
    
    Attributes:
        _channel_ids (List[str]): YouTube channel IDs to scrape (private)
        _transcript_api (YouTubeTranscriptApi): API client (private)
    """
    
    # Class constant: Exam preparation channels
    EXAM_CHANNELS = [
        "UCYRBFLkuZ8ZAfwz7ayGGvZQ",  # StudyIQ IAS
        "UCnvC2wLZOiKdFkM8Ml4EzQg",  # Drishti IAS
        "UCZ8QY-RF48rE3LJRgdD0kVQ",  # Vision IAS
        "UCawZsQWqfGSbCI5yjkdVkTA",  # OnlyIAS
        "UCOEVlIHEsILuTV_Ix8dDW5A",  # Insights IAS
        "UCawZsQWqfGSbCI5yjkdVkTB",  # PIB India Official
        "UCawZsQWqfGSbCI5yjkdVkTC",  # Sansad TV
        "UCawZsQWqfGSbCI5yjkdVkTD",  # Vajiram & Ravi
        "UCawZsQWqfGSbCI5yjkdVkTE",  # Adda247
        "UCawZsQWqfGSbCI5yjkdVkTF",  # BYJU'S Exam Prep
        "UCawZsQWqfGSbCI5yjkdVkTG",  # Unacademy UPSC
    ]
    
    def __init__(self, channel_ids: Optional[List[str]] = None):
        """
        Initialize YouTube scraper.
        
        Args:
            channel_ids: Optional list of channel IDs (uses default if None)
        """
        super().__init__(
            source_name="YouTube Exam Channels",
            base_url="https://www.youtube.com",
            timeout=30
        )
        self._channel_ids = channel_ids or self.EXAM_CHANNELS
        self._transcript_api = YouTubeTranscriptApi()
    
    def scrape(self, hours: int = 24) -> List[ScrapedContent]:
        """
        Scrape transcripts from all configured channels.
        
        Implements the abstract scrape() method from AbstractScraper.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of scraped video transcripts
        """
        all_content = []
        
        for channel_id in self._channel_ids:
            try:
                videos = self._get_recent_videos(channel_id, hours)
                for video in videos:
                    transcript = self._get_transcript(video['video_id'])
                    if transcript:
                        content = ScrapedContent(
                            title=video['title'],
                            content=transcript,
                            url=video['url'],
                            published_at=video['published_at'],
                            source_type='youtube',
                            metadata={
                                'channel_id': channel_id,
                                'video_id': video['video_id'],
                                'description': video['description']
                            }
                        )
                        if self.validate_content(content):
                            all_content.append(content)
            except Exception as e:
                self._handle_network_error(e)
                continue
        
        return all_content
    
    def _get_recent_videos(
        self, 
        channel_id: str, 
        hours: int
    ) -> List[dict]:
        """
        Get recent videos from a channel using RSS feed.
        
        Args:
            channel_id: YouTube channel ID
            hours: Hours to look back
            
        Returns:
            List of video metadata dictionaries
        """
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        feed = feedparser.parse(rss_url)
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        videos = []
        
        for entry in feed.entries:
            # Skip YouTube Shorts
            if "/shorts/" in entry.link:
                continue
            
            published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            if published_time >= cutoff_time:
                videos.append({
                    'title': entry.title,
                    'url': entry.link,
                    'video_id': self._extract_video_id(entry.link),
                    'published_at': published_time,
                    'description': entry.get('summary', '')
                })
        
        return videos
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        if "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        if "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        return url
    
    def _get_transcript(self, video_id: str) -> Optional[str]:
        """
        Get transcript for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Transcript text or None if unavailable
        """
        try:
            transcript = self._transcript_api.fetch(video_id)
            return " ".join([snippet.text for snippet in transcript.snippets])
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except Exception:
            return None
```

**Key Design Decisions**:
- Inherits common scraper behavior from AbstractScraper
- Overrides scrape() method with YouTube-specific logic
- Uses class constant for default channel list
- Private helper methods encapsulate implementation details
- Graceful handling of missing transcripts
- Filters out YouTube Shorts (typically not exam content)


#### PIBScraper

**Purpose**: Scrapes official press releases from Press Information Bureau (PIB).

**Inheritance**: Extends AbstractScraper

**Class Definition**:

```python
from typing import List
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup


class PIBScraper(AbstractScraper):
    """
    Concrete scraper for PIB (Press Information Bureau) press releases.
    
    Inherits from AbstractScraper and implements PIB-specific
    scraping logic for government press releases.
    
    Attributes:
        _categories (List[str]): PIB categories to scrape (private)
    """
    
    # PIB categories relevant to competitive exams
    EXAM_RELEVANT_CATEGORIES = [
        "Government Policies",
        "Economy",
        "Defence",
        "International Relations",
        "Science & Technology",
        "Environment",
        "Social Welfare"
    ]
    
    def __init__(self, categories: Optional[List[str]] = None):
        """
        Initialize PIB scraper.
        
        Args:
            categories: Optional list of categories (uses default if None)
        """
        super().__init__(
            source_name="Press Information Bureau",
            base_url="https://pib.gov.in",
            timeout=30
        )
        self._categories = categories or self.EXAM_RELEVANT_CATEGORIES
    
    def scrape(self, hours: int = 24) -> List[ScrapedContent]:
        """
        Scrape press releases from PIB.
        
        Implements the abstract scrape() method from AbstractScraper.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of scraped press releases
        """
        all_content = []
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        for category in self._categories:
            try:
                releases = self._scrape_category(category, cutoff_time)
                all_content.extend(releases)
            except Exception as e:
                self._handle_network_error(e)
                continue
        
        return all_content
    
    def _scrape_category(
        self, 
        category: str, 
        cutoff_time: datetime
    ) -> List[ScrapedContent]:
        """
        Scrape press releases for a specific category.
        
        Args:
            category: PIB category name
            cutoff_time: Only include releases after this time
            
        Returns:
            List of scraped content
        """
        # PIB category URL format
        category_url = f"{self._base_url}/PressReleaseIframePage.aspx?PRID={category}"
        
        response = requests.get(category_url, timeout=self._timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        releases = []
        
        # Find all press release entries
        for item in soup.find_all('div', class_='content-area'):
            try:
                release = self._parse_release(item, category)
                if release and release.published_at >= cutoff_time:
                    if self.validate_content(release):
                        releases.append(release)
            except Exception:
                continue
        
        return releases
    
    def _parse_release(
        self, 
        item: BeautifulSoup, 
        category: str
    ) -> Optional[ScrapedContent]:
        """
        Parse a single press release item.
        
        Args:
            item: BeautifulSoup element containing release
            category: Category name
            
        Returns:
            ScrapedContent or None if parsing fails
        """
        try:
            title_elem = item.find('h3')
            content_elem = item.find('div', class_='press-content')
            date_elem = item.find('span', class_='date')
            link_elem = item.find('a', href=True)
            
            if not all([title_elem, content_elem, date_elem, link_elem]):
                return None
            
            title = title_elem.get_text(strip=True)
            content = content_elem.get_text(strip=True)
            date_str = date_elem.get_text(strip=True)
            url = self._base_url + link_elem['href']
            
            # Parse PIB date format: "DD-MMM-YYYY HH:MM"
            published_at = datetime.strptime(date_str, "%d-%b-%Y %H:%M")
            published_at = published_at.replace(tzinfo=timezone.utc)
            
            return ScrapedContent(
                title=title,
                content=content,
                url=url,
                published_at=published_at,
                source_type='pib',
                metadata={
                    'category': category,
                    'ministry': self._extract_ministry(content)
                }
            )
        except Exception:
            return None
    
    def _extract_ministry(self, content: str) -> str:
        """
        Extract ministry name from press release content.
        
        Args:
            content: Press release text
            
        Returns:
            Ministry name or "Unknown"
        """
        # Common pattern: "Ministry of XYZ" in first paragraph
        import re
        match = re.search(r'Ministry of ([A-Za-z\s&]+)', content[:500])
        return match.group(1).strip() if match else "Unknown"
```

**Key Design Decisions**:
- Inherits from AbstractScraper for consistent interface
- Uses BeautifulSoup for HTML parsing
- Category-based scraping for targeted content
- Extracts ministry information for better categorization
- Robust error handling for malformed HTML
- Date parsing handles PIB-specific format


#### GovernmentSchemesScraper

**Purpose**: Scrapes information about government schemes and welfare programs.

**Inheritance**: Extends AbstractScraper

**Class Definition**:

```python
from typing import List, Dict
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup


class GovernmentSchemesScraper(AbstractScraper):
    """
    Concrete scraper for government schemes and welfare programs.
    
    Inherits from AbstractScraper and implements scraping logic
    for official government scheme portals.
    
    Attributes:
        _scheme_portals (List[str]): URLs of scheme portals (private)
    """
    
    # Official government scheme portals
    SCHEME_PORTALS = [
        "https://www.india.gov.in/spotlight/schemes",
        "https://www.myscheme.gov.in/",
    ]
    
    def __init__(self, portals: Optional[List[str]] = None):
        """
        Initialize government schemes scraper.
        
        Args:
            portals: Optional list of portal URLs (uses default if None)
        """
        super().__init__(
            source_name="Government Schemes",
            base_url="https://www.india.gov.in",
            timeout=30
        )
        self._scheme_portals = portals or self.SCHEME_PORTALS
    
    def scrape(self, hours: int = 24) -> List[ScrapedContent]:
        """
        Scrape government schemes from official portals.
        
        Implements the abstract scrape() method from AbstractScraper.
        Note: Schemes are typically updated less frequently than news,
        so the hours parameter filters by last_updated field.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of scraped scheme information
        """
        all_content = []
        
        for portal_url in self._scheme_portals:
            try:
                schemes = self._scrape_portal(portal_url, hours)
                all_content.extend(schemes)
            except Exception as e:
                self._handle_network_error(e)
                continue
        
        return all_content
    
    def _scrape_portal(self, portal_url: str, hours: int) -> List[ScrapedContent]:
        """
        Scrape schemes from a specific portal.
        
        Args:
            portal_url: URL of the scheme portal
            hours: Hours to look back
            
        Returns:
            List of scraped schemes
        """
        response = requests.get(portal_url, timeout=self._timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        schemes = []
        
        # Find scheme cards/entries (structure varies by portal)
        for item in soup.find_all(['div', 'article'], class_=['scheme-card', 'scheme-item']):
            try:
                scheme = self._parse_scheme(item, portal_url)
                if scheme and self.validate_content(scheme):
                    schemes.append(scheme)
            except Exception:
                continue
        
        return schemes
    
    def _parse_scheme(
        self, 
        item: BeautifulSoup, 
        portal_url: str
    ) -> Optional[ScrapedContent]:
        """
        Parse a single scheme entry.
        
        Args:
            item: BeautifulSoup element containing scheme
            portal_url: Source portal URL
            
        Returns:
            ScrapedContent or None if parsing fails
        """
        try:
            # Extract scheme details
            title = item.find(['h2', 'h3', 'h4']).get_text(strip=True)
            description = item.find(['p', 'div'], class_=['description', 'summary'])
            description_text = description.get_text(strip=True) if description else ""
            
            link = item.find('a', href=True)
            scheme_url = link['href'] if link else portal_url
            if not scheme_url.startswith('http'):
                scheme_url = self._base_url + scheme_url
            
            # Extract structured information
            metadata = self._extract_scheme_metadata(item)
            
            # Format content with structured information
            content = self._format_scheme_content(
                description_text, 
                metadata
            )
            
            return ScrapedContent(
                title=title,
                content=content,
                url=scheme_url,
                published_at=datetime.now(timezone.utc),  # Use current time for schemes
                source_type='government_scheme',
                metadata=metadata
            )
        except Exception:
            return None
    
    def _extract_scheme_metadata(self, item: BeautifulSoup) -> Dict[str, str]:
        """
        Extract structured metadata from scheme entry.
        
        Args:
            item: BeautifulSoup element
            
        Returns:
            Dictionary of metadata fields
        """
        metadata = {
            'ministry': 'Unknown',
            'beneficiaries': 'Unknown',
            'launch_date': 'Unknown',
            'objectives': 'Unknown'
        }
        
        # Try to find ministry
        ministry_elem = item.find(text=lambda t: 'Ministry' in str(t))
        if ministry_elem:
            metadata['ministry'] = ministry_elem.strip()
        
        # Try to find beneficiaries
        beneficiary_elem = item.find(class_=['beneficiaries', 'target-group'])
        if beneficiary_elem:
            metadata['beneficiaries'] = beneficiary_elem.get_text(strip=True)
        
        return metadata
    
    def _format_scheme_content(
        self, 
        description: str, 
        metadata: Dict[str, str]
    ) -> str:
        """
        Format scheme information into structured content.
        
        Args:
            description: Scheme description
            metadata: Extracted metadata
            
        Returns:
            Formatted content string
        """
        content_parts = [description]
        
        if metadata['ministry'] != 'Unknown':
            content_parts.append(f"\nMinistry: {metadata['ministry']}")
        
        if metadata['beneficiaries'] != 'Unknown':
            content_parts.append(f"\nBeneficiaries: {metadata['beneficiaries']}")
        
        return "\n".join(content_parts)
```

**Key Design Decisions**:
- Inherits from AbstractScraper for consistency
- Handles multiple portal formats with flexible parsing
- Extracts structured metadata (ministry, beneficiaries, etc.)
- Formats content for better AI processing
- Uses current timestamp since schemes update infrequently
- Robust error handling for varying HTML structures


#### ScraperFactory

**Purpose**: Creates scraper instances using the Factory Pattern, centralizing scraper instantiation logic.

**Design Pattern**: Factory Pattern

**Class Definition**:

```python
from typing import Dict, Type, Optional
from enum import Enum


class SourceType(Enum):
    """Enumeration of available source types."""
    YOUTUBE = "youtube"
    PIB = "pib"
    GOVERNMENT_SCHEMES = "government_schemes"


class ScraperFactory:
    """
    Factory for creating scraper instances.
    
    Implements the Factory Pattern to centralize scraper creation
    and enable easy addition of new scraper types.
    
    Attributes:
        _registry (Dict): Maps source types to scraper classes (private, class-level)
    """
    
    # Class-level registry of available scrapers
    _registry: Dict[SourceType, Type[AbstractScraper]] = {}
    
    @classmethod
    def register_scraper(
        cls, 
        source_type: SourceType, 
        scraper_class: Type[AbstractScraper]
    ) -> None:
        """
        Register a scraper class for a source type.
        
        This method allows new scrapers to be added without modifying
        the factory code (Open/Closed Principle).
        
        Args:
            source_type: The source type enum value
            scraper_class: The scraper class to register
        """
        cls._registry[source_type] = scraper_class
    
    @classmethod
    def create_scraper(
        cls, 
        source_type: SourceType,
        **kwargs
    ) -> AbstractScraper:
        """
        Create a scraper instance for the given source type.
        
        Args:
            source_type: Type of scraper to create
            **kwargs: Additional arguments to pass to scraper constructor
            
        Returns:
            Scraper instance
            
        Raises:
            ValueError: If source type is not registered
        """
        if source_type not in cls._registry:
            raise ValueError(
                f"Unknown source type: {source_type}. "
                f"Available types: {list(cls._registry.keys())}"
            )
        
        scraper_class = cls._registry[source_type]
        return scraper_class(**kwargs)
    
    @classmethod
    def get_available_sources(cls) -> List[SourceType]:
        """
        Get list of available source types.
        
        Returns:
            List of registered source types
        """
        return list(cls._registry.keys())
    
    @classmethod
    def create_all_scrapers(cls) -> List[AbstractScraper]:
        """
        Create instances of all registered scrapers.
        
        Useful for pipeline execution that needs all sources.
        
        Returns:
            List of all scraper instances
        """
        return [
            cls.create_scraper(source_type)
            for source_type in cls._registry.keys()
        ]


# Register default scrapers
ScraperFactory.register_scraper(SourceType.YOUTUBE, YouTubeScraper)
ScraperFactory.register_scraper(SourceType.PIB, PIBScraper)
ScraperFactory.register_scraper(SourceType.GOVERNMENT_SCHEMES, GovernmentSchemesScraper)
```

**Usage Example**:

```python
# Create a specific scraper
youtube_scraper = ScraperFactory.create_scraper(SourceType.YOUTUBE)

# Create all scrapers for pipeline
all_scrapers = ScraperFactory.create_all_scrapers()

# Add a new scraper type (extensibility)
class NewsScraper(AbstractScraper):
    # Implementation...
    pass

ScraperFactory.register_scraper(SourceType.NEWS, NewsScraper)
```

**Key Design Decisions**:
- Factory Pattern centralizes object creation
- Registry pattern allows runtime registration of new scrapers
- Enum for source types provides type safety
- Class methods enable usage without instantiation
- Open/Closed Principle: new scrapers can be added without modifying factory
- Returns AbstractScraper type for polymorphic usage


### Concrete Agent Implementations

#### CategorizationAgent

**Purpose**: Categorizes content into exam-relevant topics using Gemini API.

**Inheritance**: Extends AbstractAgent

**Class Definition**:

```python
from typing import List
from pydantic import BaseModel


class CategoryResult(BaseModel):
    """Result of categorization."""
    primary_category: str
    secondary_categories: List[str] = []
    confidence: float  # 0.0 to 1.0
    reasoning: str


class CategorizationAgent(AbstractAgent):
    """
    Agent for categorizing content into exam-relevant topics.
    
    Inherits from AbstractAgent and implements categorization
    logic using Gemini API.
    
    Attributes:
        _categories (List[str]): Valid category names (private)
    """
    
    # Exam-relevant categories
    EXAM_CATEGORIES = [
        "Polity",
        "Economy",
        "International Relations",
        "Science & Tech",
        "Environment & Ecology",
        "Defence & Security",
        "Government Schemes",
        "Social Issues"
    ]
    
    def __init__(self, config: AgentConfig):
        """
        Initialize categorization agent.
        
        Args:
            config: Agent configuration
        """
        super().__init__(config)
        self._categories = self.EXAM_CATEGORIES
    
    def execute(self, content: ScrapedContent) -> CategoryResult:
        """
        Categorize content into exam-relevant topics.
        
        Implements the abstract execute() method from AbstractAgent.
        
        Args:
            content: Scraped content to categorize
            
        Returns:
            CategoryResult with primary and secondary categories
        """
        prompt = self._build_categorization_prompt(content)
        response = self._call_gemini_api(prompt)
        result_dict = self._parse_json_response(response)
        
        # Validate categories
        result = CategoryResult(**result_dict)
        self._validate_categories(result)
        
        return result
    
    def _build_categorization_prompt(self, content: ScrapedContent) -> str:
        """
        Build prompt for Gemini API.
        
        Args:
            content: Content to categorize
            
        Returns:
            Formatted prompt string
        """
        categories_str = ", ".join(self._categories)
        
        return f"""You are an expert in competitive exam preparation for UPSC, SSC, and Banking exams.

Categorize the following content into exam-relevant topics.

CONTENT:
Title: {content.title}
Text: {content.content[:2000]}  # Limit for API

AVAILABLE CATEGORIES:
{categories_str}

INSTRUCTIONS:
1. Select ONE primary category that best fits the content
2. Select up to TWO secondary categories if relevant
3. Provide confidence score (0.0 to 1.0)
4. Explain your reasoning

OUTPUT FORMAT (JSON):
{{
    "primary_category": "category name",
    "secondary_categories": ["category1", "category2"],
    "confidence": 0.95,
    "reasoning": "explanation of categorization"
}}"""
    
    def _validate_categories(self, result: CategoryResult) -> None:
        """
        Validate that assigned categories are valid.
        
        Args:
            result: Categorization result to validate
            
        Raises:
            ValueError: If invalid category found
        """
        if result.primary_category not in self._categories:
            raise ValueError(
                f"Invalid primary category: {result.primary_category}"
            )
        
        for cat in result.secondary_categories:
            if cat not in self._categories:
                raise ValueError(f"Invalid secondary category: {cat}")
        
        if len(result.secondary_categories) > 2:
            raise ValueError("Maximum 2 secondary categories allowed")
```

**Key Design Decisions**:
- Inherits from AbstractAgent for consistent interface
- Uses Pydantic models for type-safe results
- Validates categories against predefined list
- Limits content length to stay within API limits
- Structured JSON output for reliable parsing
- Confidence scoring for quality assessment


#### SummarizationAgent

**Purpose**: Generates exam-focused summaries with prelims/mains relevance using Gemini API.

**Inheritance**: Extends AbstractAgent

**Class Definition**:

```python
from pydantic import BaseModel


class SummaryResult(BaseModel):
    """Result of summarization."""
    summary: str
    why_important: str
    prelims_relevance: str
    mains_relevance: str
    possible_questions: List[str]
    key_facts: List[str]


class SummarizationAgent(AbstractAgent):
    """
    Agent for generating exam-focused summaries.
    
    Inherits from AbstractAgent and implements summarization
    logic tailored for competitive exam preparation.
    
    Attributes:
        _max_summary_words (int): Maximum words in summary (private)
    """
    
    def __init__(self, config: AgentConfig, max_summary_words: int = 250):
        """
        Initialize summarization agent.
        
        Args:
            config: Agent configuration
            max_summary_words: Maximum words in summary
        """
        super().__init__(config)
        self._max_summary_words = max_summary_words
    
    def execute(
        self, 
        content: ScrapedContent, 
        category: str
    ) -> SummaryResult:
        """
        Generate exam-focused summary for content.
        
        Implements the abstract execute() method from AbstractAgent.
        
        Args:
            content: Content to summarize
            category: Primary category of content
            
        Returns:
            SummaryResult with exam-focused analysis
        """
        prompt = self._build_summarization_prompt(content, category)
        response = self._call_gemini_api(prompt)
        result_dict = self._parse_json_response(response)
        
        return SummaryResult(**result_dict)
    
    def _build_summarization_prompt(
        self, 
        content: ScrapedContent, 
        category: str
    ) -> str:
        """
        Build prompt for Gemini API.
        
        Args:
            content: Content to summarize
            category: Content category
            
        Returns:
            Formatted prompt string
        """
        return f"""You are an expert educator for competitive exams (UPSC, SSC, Banking).

Analyze the following content and create an exam-focused summary.

CONTENT:
Title: {content.title}
Category: {category}
Text: {content.content[:3000]}  # Limit for API

INSTRUCTIONS:
Create a comprehensive exam-focused analysis with:

1. SUMMARY: Concise summary in {self._max_summary_words} words
2. WHY IMPORTANT: Why this matters for exam preparation
3. PRELIMS RELEVANCE: How this relates to objective questions
4. MAINS RELEVANCE: How this relates to descriptive answers
5. POSSIBLE QUESTIONS: 3-5 potential exam questions
6. KEY FACTS: Important facts, dates, names to remember

OUTPUT FORMAT (JSON):
{{
    "summary": "concise summary text",
    "why_important": "explanation of exam relevance",
    "prelims_relevance": "connection to objective questions",
    "mains_relevance": "connection to descriptive answers",
    "possible_questions": [
        "Question 1?",
        "Question 2?",
        "Question 3?"
    ],
    "key_facts": [
        "Fact 1",
        "Fact 2",
        "Fact 3"
    ]
}}"""
    
    def get_formatted_summary(self, result: SummaryResult) -> str:
        """
        Format summary result as readable text.
        
        Args:
            result: Summary result to format
            
        Returns:
            Formatted string for display
        """
        lines = [
            "SUMMARY:",
            result.summary,
            "",
            "WHY IMPORTANT FOR EXAMS:",
            result.why_important,
            "",
            "PRELIMS RELEVANCE:",
            result.prelims_relevance,
            "",
            "MAINS RELEVANCE:",
            result.mains_relevance,
            "",
            "POSSIBLE QUESTIONS:",
        ]
        
        for i, question in enumerate(result.possible_questions, 1):
            lines.append(f"{i}. {question}")
        
        lines.append("")
        lines.append("KEY FACTS TO REMEMBER:")
        
        for fact in result.key_facts:
            lines.append(f"• {fact}")
        
        return "\n".join(lines)
```

**Key Design Decisions**:
- Inherits from AbstractAgent for consistency
- Structured output with multiple exam-relevant sections
- Configurable summary length
- Includes both prelims (objective) and mains (descriptive) analysis
- Generates potential exam questions for practice
- Extracts key facts for quick revision
- Provides formatted output method for display


#### RankingAgent

**Purpose**: Ranks articles by exam relevance using injected ranking strategies.

**Inheritance**: Extends AbstractAgent

**Class Definition**:

```python
from typing import Optional


class RankingAgent(AbstractAgent):
    """
    Agent for ranking articles by exam relevance.
    
    Inherits from AbstractAgent and uses Strategy Pattern
    to support different ranking algorithms for different exam types.
    
    Attributes:
        _strategy (AbstractRankingStrategy): Ranking strategy (private)
    """
    
    def __init__(
        self, 
        config: AgentConfig,
        strategy: AbstractRankingStrategy
    ):
        """
        Initialize ranking agent with a strategy.
        
        Demonstrates Dependency Injection and Strategy Pattern.
        
        Args:
            config: Agent configuration
            strategy: Ranking strategy to use
        """
        super().__init__(config)
        self._strategy = strategy
    
    @property
    def strategy(self) -> AbstractRankingStrategy:
        """Get the current ranking strategy."""
        return self._strategy
    
    def set_strategy(self, strategy: AbstractRankingStrategy) -> None:
        """
        Change the ranking strategy at runtime.
        
        Demonstrates Strategy Pattern's runtime flexibility.
        
        Args:
            strategy: New ranking strategy
        """
        self._strategy = strategy
    
    def execute(
        self, 
        content: ScrapedContent,
        metadata: ArticleMetadata
    ) -> RankingResult:
        """
        Rank an article using the configured strategy.
        
        Implements the abstract execute() method from AbstractAgent.
        
        Args:
            content: Article content
            metadata: Article metadata for ranking
            
        Returns:
            RankingResult with score and reasoning
        """
        # Delegate to strategy
        result = self._strategy.calculate_score(
            content.content,
            metadata
        )
        
        # Optionally enhance with AI insights
        if self._should_use_ai_enhancement(result):
            result = self._enhance_with_ai(content, result)
        
        return result
    
    def _should_use_ai_enhancement(self, result: RankingResult) -> bool:
        """
        Determine if AI enhancement is needed.
        
        Args:
            result: Initial ranking result
            
        Returns:
            True if AI enhancement should be applied
        """
        # Use AI for borderline cases (scores near threshold)
        return 4.0 <= result.score <= 6.0
    
    def _enhance_with_ai(
        self, 
        content: ScrapedContent,
        initial_result: RankingResult
    ) -> RankingResult:
        """
        Enhance ranking with AI analysis for borderline cases.
        
        Args:
            content: Article content
            initial_result: Initial ranking from strategy
            
        Returns:
            Enhanced ranking result
        """
        prompt = f"""You are an expert in competitive exam preparation.

Analyze this article's relevance for exam preparation.

ARTICLE:
Title: {content.title}
Content: {content.content[:2000]}

INITIAL SCORE: {initial_result.score}/10
INITIAL REASONING: {initial_result.reasoning}

Provide:
1. Adjusted score (0.0 to 10.0)
2. Detailed reasoning for the score
3. Specific exam topics this relates to

OUTPUT FORMAT (JSON):
{{
    "score": 7.5,
    "reasoning": "detailed explanation",
    "exam_topics": ["topic1", "topic2"]
}}"""
        
        response = self._call_gemini_api(prompt)
        ai_result = self._parse_json_response(response)
        
        # Combine strategy and AI results
        final_score = (initial_result.score + ai_result['score']) / 2
        
        return RankingResult(
            score=final_score,
            reasoning=f"{initial_result.reasoning}\n\nAI Enhancement: {ai_result['reasoning']}",
            factors={
                **initial_result.factors,
                'ai_adjustment': ai_result['score'] - initial_result.score
            }
        )
```

**Key Design Decisions**:
- Inherits from AbstractAgent for consistency
- Strategy Pattern: ranking algorithm is injected dependency
- Runtime strategy switching for flexibility
- Hybrid approach: strategy-based + AI enhancement for borderline cases
- Encapsulated strategy prevents external modification
- Demonstrates Dependency Injection principle


#### DigestAgent

**Purpose**: Compiles ranked articles into a formatted digest for output.

**Inheritance**: Extends AbstractAgent

**Class Definition**:

```python
from typing import List, Tuple
from datetime import datetime


class DigestArticle(BaseModel):
    """Article data for digest generation."""
    title: str
    summary: SummaryResult
    category: str
    score: float
    url: str
    published_at: datetime


class DigestResult(BaseModel):
    """Generated digest output."""
    introduction: str
    articles_by_category: Dict[str, List[DigestArticle]]
    conclusion: str
    generated_at: datetime


class DigestAgent(AbstractAgent):
    """
    Agent for generating formatted digests from ranked articles.
    
    Inherits from AbstractAgent and implements digest generation
    with AI-powered introduction and conclusion.
    
    Attributes:
        _digest_title (str): Title for the digest (private)
    """
    
    def __init__(
        self, 
        config: AgentConfig,
        digest_title: str = "Daily Exam Intelligence Digest"
    ):
        """
        Initialize digest agent.
        
        Args:
            config: Agent configuration
            digest_title: Title for generated digests
        """
        super().__init__(config)
        self._digest_title = digest_title
    
    def execute(
        self, 
        articles: List[DigestArticle]
    ) -> DigestResult:
        """
        Generate a formatted digest from ranked articles.
        
        Implements the abstract execute() method from AbstractAgent.
        
        Args:
            articles: List of articles to include in digest
            
        Returns:
            DigestResult with formatted content
        """
        # Group articles by category
        by_category = self._group_by_category(articles)
        
        # Generate AI-powered introduction
        introduction = self._generate_introduction(articles)
        
        # Generate AI-powered conclusion
        conclusion = self._generate_conclusion(articles)
        
        return DigestResult(
            introduction=introduction,
            articles_by_category=by_category,
            conclusion=conclusion,
            generated_at=datetime.now(timezone.utc)
        )
    
    def _group_by_category(
        self, 
        articles: List[DigestArticle]
    ) -> Dict[str, List[DigestArticle]]:
        """
        Group articles by category.
        
        Args:
            articles: Articles to group
            
        Returns:
            Dictionary mapping categories to article lists
        """
        grouped = {}
        for article in articles:
            if article.category not in grouped:
                grouped[article.category] = []
            grouped[article.category].append(article)
        
        # Sort articles within each category by score
        for category in grouped:
            grouped[category].sort(key=lambda a: a.score, reverse=True)
        
        return grouped
    
    def _generate_introduction(self, articles: List[DigestArticle]) -> str:
        """
        Generate AI-powered introduction.
        
        Args:
            articles: Articles in the digest
            
        Returns:
            Introduction text
        """
        categories = set(a.category for a in articles)
        avg_score = sum(a.score for a in articles) / len(articles)
        
        prompt = f"""You are an expert educator for competitive exams.

Write a brief introduction (2-3 sentences) for today's exam intelligence digest.

DIGEST STATS:
- Total articles: {len(articles)}
- Categories covered: {', '.join(categories)}
- Average relevance score: {avg_score:.1f}/10

The introduction should:
1. Welcome the reader
2. Highlight key themes or important topics
3. Encourage focused study

Keep it motivating and concise."""
        
        return self._call_gemini_api(prompt)
    
    def _generate_conclusion(self, articles: List[DigestArticle]) -> str:
        """
        Generate AI-powered conclusion.
        
        Args:
            articles: Articles in the digest
            
        Returns:
            Conclusion text
        """
        top_categories = self._get_top_categories(articles, n=3)
        
        prompt = f"""You are an expert educator for competitive exams.

Write a brief conclusion (2-3 sentences) for today's exam intelligence digest.

TOP FOCUS AREAS:
{', '.join(top_categories)}

The conclusion should:
1. Summarize key takeaways
2. Suggest study priorities
3. Provide encouragement

Keep it actionable and motivating."""
        
        return self._call_gemini_api(prompt)
    
    def _get_top_categories(
        self, 
        articles: List[DigestArticle], 
        n: int
    ) -> List[str]:
        """
        Get top N categories by article count.
        
        Args:
            articles: Articles to analyze
            n: Number of top categories to return
            
        Returns:
            List of category names
        """
        from collections import Counter
        category_counts = Counter(a.category for a in articles)
        return [cat for cat, _ in category_counts.most_common(n)]
    
    def format_as_text(self, digest: DigestResult) -> str:
        """
        Format digest as plain text.
        
        Args:
            digest: Digest to format
            
        Returns:
            Formatted text string
        """
        lines = [
            "=" * 80,
            self._digest_title.center(80),
            f"Generated: {digest.generated_at.strftime('%Y-%m-%d %H:%M UTC')}".center(80),
            "=" * 80,
            "",
            digest.introduction,
            "",
        ]
        
        for category, articles in digest.articles_by_category.items():
            lines.append("")
            lines.append(f"{'─' * 80}")
            lines.append(f"📚 {category.upper()}")
            lines.append(f"{'─' * 80}")
            
            for i, article in enumerate(articles, 1):
                lines.append(f"\n{i}. {article.title} (Score: {article.score:.1f}/10)")
                lines.append(f"   URL: {article.url}")
                lines.append(f"\n   {article.summary.summary}")
                lines.append(f"\n   💡 Why Important: {article.summary.why_important}")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("CONCLUSION")
        lines.append("=" * 80)
        lines.append(digest.conclusion)
        lines.append("")
        
        return "\n".join(lines)
```

**Key Design Decisions**:
- Inherits from AbstractAgent for consistency
- AI-generated introduction and conclusion for personalization
- Groups articles by category for organized presentation
- Provides both structured (DigestResult) and formatted (text) output
- Sorts articles by score within categories
- Includes metadata (generation time, scores) for transparency


### Concrete Ranking Strategy Implementations

#### UPSCRankingStrategy

**Purpose**: Implements UPSC-specific ranking algorithm.

**Inheritance**: Extends AbstractRankingStrategy

**Class Definition**:

```python
class UPSCRankingStrategy(AbstractRankingStrategy):
    """
    Ranking strategy optimized for UPSC Civil Services Examination.
    
    Inherits from AbstractRankingStrategy and implements
    UPSC-specific scoring logic.
    
    UPSC Focus Areas:
    - Polity & Governance (high priority)
    - International Relations (high priority)
    - Economy (high priority)
    - Current Affairs (essential)
    """
    
    # UPSC priority categories (ordered by importance)
    PRIORITY_CATEGORIES = [
        "Polity",
        "International Relations",
        "Economy",
        "Government Schemes",
        "Environment & Ecology",
        "Science & Tech",
        "Defence & Security",
        "Social Issues"
    ]
    
    # Scoring weights for UPSC
    DEFAULT_WEIGHTS = {
        'category_relevance': 0.35,  # Category match is crucial
        'freshness': 0.20,           # Recent events matter
        'content_depth': 0.25,       # Detailed analysis preferred
        'source_credibility': 0.20   # Official sources valued
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize UPSC ranking strategy.
        
        Args:
            weights: Optional custom weights (uses defaults if None)
        """
        super().__init__(
            exam_type="UPSC",
            weights=weights or self.DEFAULT_WEIGHTS
        )
    
    def calculate_score(
        self, 
        content: str, 
        metadata: ArticleMetadata
    ) -> RankingResult:
        """
        Calculate UPSC relevance score.
        
        Implements the abstract calculate_score() method.
        
        Args:
            content: Article content
            metadata: Article metadata
            
        Returns:
            RankingResult with score and breakdown
        """
        factors = {}
        
        # 1. Category relevance (35%)
        factors['category_relevance'] = self._calculate_category_relevance(
            metadata.category,
            self.PRIORITY_CATEGORIES
        )
        
        # 2. Freshness (20%)
        factors['freshness'] = self._calculate_freshness_score(
            metadata.published_at
        )
        
        # 3. Content depth (25%)
        factors['content_depth'] = self._calculate_content_depth(
            content,
            metadata.content_length
        )
        
        # 4. Source credibility (20%)
        factors['source_credibility'] = self._calculate_source_credibility(
            metadata.source_type
        )
        
        # Calculate weighted score
        score = sum(
            factors[factor] * self._weights[factor]
            for factor in factors
        )
        
        # Scale to 0-10
        final_score = score * 10.0
        
        # Generate reasoning
        reasoning = self._generate_reasoning(factors, final_score)
        
        return RankingResult(
            score=final_score,
            reasoning=reasoning,
            factors=factors
        )
    
    def _calculate_content_depth(
        self, 
        content: str, 
        length: int
    ) -> float:
        """
        Calculate content depth score.
        
        UPSC prefers detailed, analytical content.
        
        Args:
            content: Article text
            metadata: Article metadata
            
        Returns:
            Score from 0.0 to 1.0
        """
        # Length score (longer = more detailed)
        if length < 500:
            length_score = 0.3
        elif length < 1000:
            length_score = 0.6
        elif length < 2000:
            length_score = 0.8
        else:
            length_score = 1.0
        
        # Keyword density (analytical terms)
        analytical_keywords = [
            'analysis', 'impact', 'implications', 'significance',
            'perspective', 'challenges', 'opportunities', 'policy',
            'governance', 'framework', 'mechanism', 'strategy'
        ]
        
        content_lower = content.lower()
        keyword_count = sum(
            1 for keyword in analytical_keywords
            if keyword in content_lower
        )
        keyword_score = min(1.0, keyword_count / 5)  # 5+ keywords = max score
        
        # Combine scores
        return (length_score * 0.6) + (keyword_score * 0.4)
    
    def _calculate_source_credibility(self, source_type: str) -> float:
        """
        Calculate source credibility score.
        
        UPSC values official government sources.
        
        Args:
            source_type: Type of source
            
        Returns:
            Score from 0.0 to 1.0
        """
        credibility_map = {
            'pib': 1.0,              # Official government source
            'government_scheme': 1.0, # Official scheme info
            'youtube': 0.7,          # Educational channels (varies)
            'news': 0.8,             # News sources
            'editorial': 0.9         # Expert analysis
        }
        
        return credibility_map.get(source_type, 0.5)
    
    def _generate_reasoning(
        self, 
        factors: Dict[str, float], 
        final_score: float
    ) -> str:
        """
        Generate human-readable reasoning for the score.
        
        Args:
            factors: Individual factor scores
            final_score: Final calculated score
            
        Returns:
            Reasoning text
        """
        lines = [
            f"UPSC Relevance Score: {final_score:.1f}/10",
            "",
            "Factor Breakdown:"
        ]
        
        for factor, score in factors.items():
            percentage = score * 100
            lines.append(f"  • {factor.replace('_', ' ').title()}: {percentage:.0f}%")
        
        # Add interpretation
        if final_score >= 8.0:
            lines.append("\n✓ Highly relevant for UPSC preparation")
        elif final_score >= 6.0:
            lines.append("\n✓ Moderately relevant for UPSC preparation")
        else:
            lines.append("\n⚠ Lower priority for UPSC preparation")
        
        return "\n".join(lines)
```

**Key Design Decisions**:
- Inherits from AbstractRankingStrategy
- UPSC-specific priority categories and weights
- Multi-factor scoring: category, freshness, depth, credibility
- Configurable weights for experimentation
- Detailed reasoning generation for transparency
- Analytical keyword detection for content quality


#### SSCRankingStrategy

**Purpose**: Implements SSC-specific ranking algorithm.

**Inheritance**: Extends AbstractRankingStrategy

**Class Definition**:

```python
class SSCRankingStrategy(AbstractRankingStrategy):
    """
    Ranking strategy optimized for SSC (Staff Selection Commission) exams.
    
    Inherits from AbstractRankingStrategy and implements
    SSC-specific scoring logic.
    
    SSC Focus Areas:
    - General Awareness (current affairs heavy)
    - Quantitative data (statistics, numbers)
    - Government schemes (welfare focus)
    - Recent events (last 6 months priority)
    """
    
    PRIORITY_CATEGORIES = [
        "Government Schemes",
        "Economy",
        "Science & Tech",
        "Social Issues",
        "Polity",
        "Environment & Ecology",
        "Defence & Security",
        "International Relations"
    ]
    
    DEFAULT_WEIGHTS = {
        'category_relevance': 0.30,
        'freshness': 0.35,           # SSC emphasizes recent events
        'factual_density': 0.25,     # Facts, figures, dates important
        'source_credibility': 0.10
    }
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize SSC ranking strategy."""
        super().__init__(
            exam_type="SSC",
            weights=weights or self.DEFAULT_WEIGHTS
        )
    
    def calculate_score(
        self, 
        content: str, 
        metadata: ArticleMetadata
    ) -> RankingResult:
        """Calculate SSC relevance score."""
        factors = {}
        
        factors['category_relevance'] = self._calculate_category_relevance(
            metadata.category,
            self.PRIORITY_CATEGORIES
        )
        
        factors['freshness'] = self._calculate_freshness_score(
            metadata.published_at
        )
        
        factors['factual_density'] = self._calculate_factual_density(content)
        
        factors['source_credibility'] = self._calculate_source_credibility(
            metadata.source_type
        )
        
        score = sum(
            factors[factor] * self._weights[factor]
            for factor in factors
        )
        
        final_score = score * 10.0
        reasoning = self._generate_reasoning(factors, final_score)
        
        return RankingResult(
            score=final_score,
            reasoning=reasoning,
            factors=factors
        )
    
    def _calculate_factual_density(self, content: str) -> float:
        """
        Calculate density of factual information.
        
        SSC questions often test specific facts, dates, and numbers.
        
        Args:
            content: Article text
            
        Returns:
            Score from 0.0 to 1.0
        """
        import re
        
        # Count numbers (dates, statistics, etc.)
        numbers = re.findall(r'\b\d+\b', content)
        number_score = min(1.0, len(numbers) / 10)  # 10+ numbers = max score
        
        # Count proper nouns (names, places, organizations)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        noun_score = min(1.0, len(proper_nouns) / 15)  # 15+ nouns = max score
        
        # Count dates
        dates = re.findall(
            r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4})\b',
            content
        )
        date_score = min(1.0, len(dates) / 5)  # 5+ dates = max score
        
        # Weighted combination
        return (number_score * 0.4) + (noun_score * 0.4) + (date_score * 0.2)
    
    def _calculate_source_credibility(self, source_type: str) -> float:
        """Calculate source credibility for SSC context."""
        credibility_map = {
            'pib': 1.0,
            'government_scheme': 1.0,
            'youtube': 0.8,  # SSC channels often good
            'news': 0.9,
            'editorial': 0.7
        }
        return credibility_map.get(source_type, 0.5)
    
    def _generate_reasoning(
        self, 
        factors: Dict[str, float], 
        final_score: float
    ) -> str:
        """Generate reasoning for SSC score."""
        lines = [
            f"SSC Relevance Score: {final_score:.1f}/10",
            "",
            "Factor Breakdown:"
        ]
        
        for factor, score in factors.items():
            percentage = score * 100
            lines.append(f"  • {factor.replace('_', ' ').title()}: {percentage:.0f}%")
        
        if final_score >= 8.0:
            lines.append("\n✓ Highly relevant for SSC preparation")
        elif final_score >= 6.0:
            lines.append("\n✓ Moderately relevant for SSC preparation")
        else:
            lines.append("\n⚠ Lower priority for SSC preparation")
        
        return "\n".join(lines)
```

#### BankingRankingStrategy

**Purpose**: Implements Banking exam-specific ranking algorithm.

**Inheritance**: Extends AbstractRankingStrategy

**Class Definition**:

```python
class BankingRankingStrategy(AbstractRankingStrategy):
    """
    Ranking strategy optimized for Banking exams (IBPS, SBI, RBI).
    
    Banking Focus Areas:
    - Economy & Banking sector
    - Financial policies & regulations
    - Government schemes (financial inclusion)
    - RBI policies and announcements
    """
    
    PRIORITY_CATEGORIES = [
        "Economy",
        "Government Schemes",
        "Polity",
        "Science & Tech",
        "International Relations",
        "Social Issues",
        "Environment & Ecology",
        "Defence & Security"
    ]
    
    DEFAULT_WEIGHTS = {
        'category_relevance': 0.40,  # Banking heavily focused on economy
        'freshness': 0.25,
        'banking_keywords': 0.25,    # Banking-specific terms
        'source_credibility': 0.10
    }
    
    # Banking-specific keywords
    BANKING_KEYWORDS = [
        'bank', 'rbi', 'reserve bank', 'monetary policy', 'fiscal',
        'inflation', 'gdp', 'credit', 'loan', 'interest rate',
        'npa', 'financial inclusion', 'digital payment', 'fintech',
        'basel', 'repo rate', 'crr', 'slr', 'msme', 'nbfc'
    ]
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize Banking ranking strategy."""
        super().__init__(
            exam_type="Banking",
            weights=weights or self.DEFAULT_WEIGHTS
        )
    
    def calculate_score(
        self, 
        content: str, 
        metadata: ArticleMetadata
    ) -> RankingResult:
        """Calculate Banking exam relevance score."""
        factors = {}
        
        factors['category_relevance'] = self._calculate_category_relevance(
            metadata.category,
            self.PRIORITY_CATEGORIES
        )
        
        factors['freshness'] = self._calculate_freshness_score(
            metadata.published_at
        )
        
        factors['banking_keywords'] = self._calculate_banking_keyword_score(
            content
        )
        
        factors['source_credibility'] = self._calculate_source_credibility(
            metadata.source_type
        )
        
        score = sum(
            factors[factor] * self._weights[factor]
            for factor in factors
        )
        
        final_score = score * 10.0
        reasoning = self._generate_reasoning(factors, final_score)
        
        return RankingResult(
            score=final_score,
            reasoning=reasoning,
            factors=factors
        )
    
    def _calculate_banking_keyword_score(self, content: str) -> float:
        """
        Calculate score based on banking-specific keywords.
        
        Args:
            content: Article text
            
        Returns:
            Score from 0.0 to 1.0
        """
        content_lower = content.lower()
        
        keyword_count = sum(
            1 for keyword in self.BANKING_KEYWORDS
            if keyword in content_lower
        )
        
        # 5+ banking keywords = max score
        return min(1.0, keyword_count / 5)
    
    def _calculate_source_credibility(self, source_type: str) -> float:
        """Calculate source credibility for Banking context."""
        credibility_map = {
            'pib': 1.0,
            'government_scheme': 0.9,
            'youtube': 0.7,
            'news': 0.9,
            'editorial': 0.8
        }
        return credibility_map.get(source_type, 0.5)
    
    def _generate_reasoning(
        self, 
        factors: Dict[str, float], 
        final_score: float
    ) -> str:
        """Generate reasoning for Banking score."""
        lines = [
            f"Banking Exam Relevance Score: {final_score:.1f}/10",
            "",
            "Factor Breakdown:"
        ]
        
        for factor, score in factors.items():
            percentage = score * 100
            lines.append(f"  • {factor.replace('_', ' ').title()}: {percentage:.0f}%")
        
        if final_score >= 8.0:
            lines.append("\n✓ Highly relevant for Banking exam preparation")
        elif final_score >= 6.0:
            lines.append("\n✓ Moderately relevant for Banking exam preparation")
        else:
            lines.append("\n⚠ Lower priority for Banking exam preparation")
        
        return "\n".join(lines)
```

**Key Design Decisions**:
- All strategies inherit from AbstractRankingStrategy
- Each strategy has exam-specific priorities and weights
- SSC emphasizes freshness and factual density
- Banking emphasizes economy category and banking keywords
- Strategies are interchangeable (Liskov Substitution Principle)
- Can be injected into RankingAgent at runtime


## Data Models

### Database Schema Design

The system uses PostgreSQL with SQLAlchemy ORM for data persistence. The schema is designed for efficient querying and maintains referential integrity.

#### Entity Relationship Diagram

```mermaid
erDiagram
    SOURCES ||--o{ ARTICLES : provides
    CATEGORIES ||--o{ ARTICLES : classifies
    ARTICLES ||--|| SUMMARIES : has
    ARTICLES ||--|| RANKINGS : has
    USER_PROFILES ||--o{ RANKINGS : influences
    
    SOURCES {
        int id PK
        string name
        string source_type
        string base_url
        boolean is_active
        timestamp created_at
    }
    
    CATEGORIES {
        int id PK
        string name
        string description
        int priority_order
        timestamp created_at
    }
    
    ARTICLES {
        int id PK
        int source_id FK
        int category_id FK
        string title
        text content
        string url
        timestamp published_at
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }
    
    SUMMARIES {
        int id PK
        int article_id FK
        text summary
        text why_important
        text prelims_relevance
        text mains_relevance
        jsonb possible_questions
        jsonb key_facts
        timestamp created_at
    }
    
    RANKINGS {
        int id PK
        int article_id FK
        int user_profile_id FK
        float score
        string exam_type
        text reasoning
        jsonb factors
        timestamp created_at
    }
    
    USER_PROFILES {
        int id PK
        string name
        string email
        jsonb interests
        string exam_type
        string expertise_level
        timestamp created_at
        timestamp updated_at
    }
```


#### SQLAlchemy ORM Models

**Base Model**:

```python
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
```

**Source Model**:

```python
class Source(Base, TimestampMixin):
    """
    Represents a content source (YouTube, PIB, etc.).
    
    Attributes:
        id: Primary key
        name: Human-readable source name
        source_type: Type of source (youtube, pib, government_scheme)
        base_url: Base URL for the source
        is_active: Whether source is currently active
        articles: Relationship to articles from this source
    """
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    source_type = Column(String(50), nullable=False)
    base_url = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    articles = relationship('Article', back_populates='source', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', type='{self.source_type}')>"
```

**Category Model**:

```python
class Category(Base, TimestampMixin):
    """
    Represents an exam-relevant category.
    
    Attributes:
        id: Primary key
        name: Category name (Polity, Economy, etc.)
        description: Detailed description
        priority_order: Display/sorting priority
        articles: Relationship to articles in this category
    """
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    priority_order = Column(Integer, default=0)
    
    # Relationships
    articles = relationship('Article', back_populates='category')
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
```

**Article Model**:

```python
class Article(Base, TimestampMixin):
    """
    Represents a scraped article.
    
    Attributes:
        id: Primary key
        source_id: Foreign key to sources table
        category_id: Foreign key to categories table
        title: Article title
        content: Full article content
        url: Source URL
        published_at: Publication timestamp
        metadata: Additional metadata (JSON)
        source: Relationship to source
        category: Relationship to category
        summary: Relationship to summary (one-to-one)
        ranking: Relationship to ranking (one-to-one)
    """
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False)
    metadata = Column(JSON, default={})
    
    # Relationships
    source = relationship('Source', back_populates='articles')
    category = relationship('Category', back_populates='articles')
    summary = relationship('Summary', back_populates='article', uselist=False, cascade='all, delete-orphan')
    ranking = relationship('Ranking', back_populates='article', uselist=False, cascade='all, delete-orphan')
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_articles_published_at', 'published_at'),
        Index('idx_articles_category_id', 'category_id'),
        Index('idx_articles_source_id', 'source_id'),
    )
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...')>"
```

**Summary Model**:

```python
class Summary(Base, TimestampMixin):
    """
    Represents an AI-generated summary of an article.
    
    Attributes:
        id: Primary key
        article_id: Foreign key to articles table
        summary: Main summary text
        why_important: Exam relevance explanation
        prelims_relevance: Prelims exam relevance
        mains_relevance: Mains exam relevance
        possible_questions: List of potential questions (JSON)
        key_facts: List of key facts (JSON)
        article: Relationship to article
    """
    __tablename__ = 'summaries'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False, unique=True)
    summary = Column(Text, nullable=False)
    why_important = Column(Text)
    prelims_relevance = Column(Text)
    mains_relevance = Column(Text)
    possible_questions = Column(JSON, default=[])
    key_facts = Column(JSON, default=[])
    
    # Relationships
    article = relationship('Article', back_populates='summary')
    
    def __repr__(self):
        return f"<Summary(id={self.id}, article_id={self.article_id})>"
```

**Ranking Model**:

```python
class Ranking(Base, TimestampMixin):
    """
    Represents a relevance ranking for an article.
    
    Attributes:
        id: Primary key
        article_id: Foreign key to articles table
        user_profile_id: Foreign key to user_profiles table (optional)
        score: Relevance score (0.0 to 10.0)
        exam_type: Exam type this ranking is for
        reasoning: Explanation of the score
        factors: Individual factor scores (JSON)
        article: Relationship to article
        user_profile: Relationship to user profile
    """
    __tablename__ = 'rankings'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False, unique=True)
    user_profile_id = Column(Integer, ForeignKey('user_profiles.id'))
    score = Column(Float, nullable=False)
    exam_type = Column(String(50), nullable=False)
    reasoning = Column(Text)
    factors = Column(JSON, default={})
    
    # Relationships
    article = relationship('Article', back_populates='ranking')
    user_profile = relationship('UserProfile', back_populates='rankings')
    
    # Indexes for ranking queries
    __table_args__ = (
        Index('idx_rankings_score', 'score'),
        Index('idx_rankings_exam_type', 'exam_type'),
    )
    
    def __repr__(self):
        return f"<Ranking(id={self.id}, article_id={self.article_id}, score={self.score})>"
```

**UserProfile Model**:

```python
class UserProfile(Base, TimestampMixin):
    """
    Represents a user profile for personalized rankings.
    
    Attributes:
        id: Primary key
        name: User name
        email: User email
        interests: List of interests (JSON)
        exam_type: Target exam type
        expertise_level: User's expertise level
        rankings: Relationship to rankings
    """
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    interests = Column(JSON, default=[])
    exam_type = Column(String(50), nullable=False)
    expertise_level = Column(String(50), default='intermediate')
    
    # Relationships
    rankings = relationship('Ranking', back_populates='user_profile')
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, name='{self.name}', exam_type='{self.exam_type}')>"
```

**Key Design Decisions**:
- TimestampMixin provides automatic timestamp management
- Foreign key constraints ensure referential integrity
- Indexes on frequently queried columns (published_at, score, category_id)
- JSON columns for flexible metadata storage
- Cascade deletes maintain data consistency
- One-to-one relationships for summary and ranking
- Relationships use back_populates for bidirectional access


### Repository Pattern Implementation

The Repository Pattern abstracts data access logic, providing a clean interface between business logic and data storage.

#### Base Repository

```python
from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session
from contextlib import contextmanager

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository providing common CRUD operations.
    
    Implements the Repository Pattern to abstract database access.
    Uses Generic type for type safety.
    
    Attributes:
        _model_class (Type[T]): SQLAlchemy model class (private)
        _session_factory: SQLAlchemy session factory (private)
    """
    
    def __init__(self, model_class: Type[T], session_factory):
        """
        Initialize repository.
        
        Args:
            model_class: SQLAlchemy model class
            session_factory: Session factory for database connections
        """
        self._model_class = model_class
        self._session_factory = session_factory
    
    @contextmanager
    def _get_session(self):
        """
        Context manager for database sessions.
        
        Ensures proper session handling (commit, rollback, close).
        
        Yields:
            SQLAlchemy session
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create(self, entity: T) -> T:
        """
        Create a new entity.
        
        Args:
            entity: Entity to create
            
        Returns:
            Created entity with ID populated
        """
        with self._get_session() as session:
            session.add(entity)
            session.flush()  # Get ID without committing
            session.refresh(entity)
            return entity
    
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """
        Find entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity or None if not found
        """
        with self._get_session() as session:
            return session.query(self._model_class).filter_by(id=entity_id).first()
    
    def find_all(self) -> List[T]:
        """
        Find all entities.
        
        Returns:
            List of all entities
        """
        with self._get_session() as session:
            return session.query(self._model_class).all()
    
    def update(self, entity: T) -> T:
        """
        Update an existing entity.
        
        Args:
            entity: Entity to update
            
        Returns:
            Updated entity
        """
        with self._get_session() as session:
            session.merge(entity)
            return entity
    
    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if deleted, False if not found
        """
        with self._get_session() as session:
            entity = session.query(self._model_class).filter_by(id=entity_id).first()
            if entity:
                session.delete(entity)
                return True
            return False
```

#### ArticleRepository

```python
from datetime import datetime
from typing import List, Optional


class ArticleRepository(BaseRepository[Article]):
    """
    Repository for Article entities.
    
    Extends BaseRepository with article-specific queries.
    """
    
    def __init__(self, session_factory):
        """Initialize article repository."""
        super().__init__(Article, session_factory)
    
    def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Article]:
        """
        Find articles published within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of articles in date range
        """
        with self._get_session() as session:
            return session.query(Article).filter(
                Article.published_at >= start_date,
                Article.published_at <= end_date
            ).order_by(Article.published_at.desc()).all()
    
    def find_by_category(self, category_id: int) -> List[Article]:
        """
        Find articles by category.
        
        Args:
            category_id: Category ID
            
        Returns:
            List of articles in category
        """
        with self._get_session() as session:
            return session.query(Article).filter_by(
                category_id=category_id
            ).order_by(Article.published_at.desc()).all()
    
    def find_by_source(self, source_id: int) -> List[Article]:
        """
        Find articles by source.
        
        Args:
            source_id: Source ID
            
        Returns:
            List of articles from source
        """
        with self._get_session() as session:
            return session.query(Article).filter_by(
                source_id=source_id
            ).order_by(Article.published_at.desc()).all()
    
    def find_by_url(self, url: str) -> Optional[Article]:
        """
        Find article by URL (for duplicate detection).
        
        Args:
            url: Article URL
            
        Returns:
            Article or None if not found
        """
        with self._get_session() as session:
            return session.query(Article).filter_by(url=url).first()
    
    def bulk_create(self, articles: List[Article]) -> List[Article]:
        """
        Create multiple articles in a single transaction.
        
        Args:
            articles: List of articles to create
            
        Returns:
            List of created articles
        """
        with self._get_session() as session:
            session.bulk_save_objects(articles, return_defaults=True)
            return articles
```

#### SummaryRepository

```python
class SummaryRepository(BaseRepository[Summary]):
    """Repository for Summary entities."""
    
    def __init__(self, session_factory):
        """Initialize summary repository."""
        super().__init__(Summary, session_factory)
    
    def find_by_article_id(self, article_id: int) -> Optional[Summary]:
        """
        Find summary for an article.
        
        Args:
            article_id: Article ID
            
        Returns:
            Summary or None if not found
        """
        with self._get_session() as session:
            return session.query(Summary).filter_by(
                article_id=article_id
            ).first()
```

#### RankingRepository

```python
class RankingRepository(BaseRepository[Ranking]):
    """Repository for Ranking entities."""
    
    def __init__(self, session_factory):
        """Initialize ranking repository."""
        super().__init__(Ranking, session_factory)
    
    def find_by_article_id(self, article_id: int) -> Optional[Ranking]:
        """
        Find ranking for an article.
        
        Args:
            article_id: Article ID
            
        Returns:
            Ranking or None if not found
        """
        with self._get_session() as session:
            return session.query(Ranking).filter_by(
                article_id=article_id
            ).first()
    
    def find_top_n(
        self, 
        n: int, 
        exam_type: Optional[str] = None
    ) -> List[Ranking]:
        """
        Find top N ranked articles.
        
        Args:
            n: Number of articles to return
            exam_type: Optional exam type filter
            
        Returns:
            List of top N rankings
        """
        with self._get_session() as session:
            query = session.query(Ranking)
            
            if exam_type:
                query = query.filter_by(exam_type=exam_type)
            
            return query.order_by(Ranking.score.desc()).limit(n).all()
    
    def find_by_score_range(
        self, 
        min_score: float, 
        max_score: float
    ) -> List[Ranking]:
        """
        Find rankings within a score range.
        
        Args:
            min_score: Minimum score
            max_score: Maximum score
            
        Returns:
            List of rankings in range
        """
        with self._get_session() as session:
            return session.query(Ranking).filter(
                Ranking.score >= min_score,
                Ranking.score <= max_score
            ).order_by(Ranking.score.desc()).all()
```

#### CategoryRepository

```python
class CategoryRepository(BaseRepository[Category]):
    """Repository for Category entities."""
    
    def __init__(self, session_factory):
        """Initialize category repository."""
        super().__init__(Category, session_factory)
    
    def find_by_name(self, name: str) -> Optional[Category]:
        """
        Find category by name.
        
        Args:
            name: Category name
            
        Returns:
            Category or None if not found
        """
        with self._get_session() as session:
            return session.query(Category).filter_by(name=name).first()
    
    def find_all_ordered(self) -> List[Category]:
        """
        Find all categories ordered by priority.
        
        Returns:
            List of categories ordered by priority_order
        """
        with self._get_session() as session:
            return session.query(Category).order_by(
                Category.priority_order
            ).all()
```

#### SourceRepository

```python
class SourceRepository(BaseRepository[Source]):
    """Repository for Source entities."""
    
    def __init__(self, session_factory):
        """Initialize source repository."""
        super().__init__(Source, session_factory)
    
    def find_by_type(self, source_type: str) -> List[Source]:
        """
        Find sources by type.
        
        Args:
            source_type: Source type (youtube, pib, etc.)
            
        Returns:
            List of sources of that type
        """
        with self._get_session() as session:
            return session.query(Source).filter_by(
                source_type=source_type
            ).all()
    
    def find_active_sources(self) -> List[Source]:
        """
        Find all active sources.
        
        Returns:
            List of active sources
        """
        with self._get_session() as session:
            return session.query(Source).filter_by(
                is_active=True
            ).all()
```

**Key Design Decisions**:
- BaseRepository provides common CRUD operations (DRY principle)
- Generic type parameter ensures type safety
- Context manager ensures proper session handling
- Specific repositories add domain-specific queries
- Bulk operations for performance
- Dependency Inversion: services depend on repository interfaces


### Service Layer Implementation

The Service Layer orchestrates business logic, coordinating between scrapers, agents, and repositories. Services depend on abstractions (interfaces) rather than concrete implementations (Dependency Inversion Principle).

#### ScrapingService

```python
from typing import List, Dict
from datetime import datetime, timedelta, timezone


class ScrapingService:
    """
    Service for orchestrating content scraping.
    
    Coordinates scrapers and persists results via repositories.
    
    Attributes:
        _scraper_factory (ScraperFactory): Factory for creating scrapers (private)
        _article_repo (ArticleRepository): Article repository (private)
        _source_repo (SourceRepository): Source repository (private)
    """
    
    def __init__(
        self,
        scraper_factory: ScraperFactory,
        article_repo: ArticleRepository,
        source_repo: SourceRepository
    ):
        """
        Initialize scraping service.
        
        Demonstrates Dependency Injection pattern.
        
        Args:
            scraper_factory: Factory for creating scrapers
            article_repo: Repository for articles
            source_repo: Repository for sources
        """
        self._scraper_factory = scraper_factory
        self._article_repo = article_repo
        self._source_repo = source_repo
    
    def scrape_all_sources(self, hours: int = 24) -> Dict[str, int]:
        """
        Scrape content from all active sources.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary mapping source names to article counts
        """
        results = {}
        active_sources = self._source_repo.find_active_sources()
        
        for source in active_sources:
            try:
                count = self._scrape_source(source, hours)
                results[source.name] = count
            except Exception as e:
                print(f"Error scraping {source.name}: {str(e)}")
                results[source.name] = 0
        
        return results
    
    def _scrape_source(self, source: Source, hours: int) -> int:
        """
        Scrape content from a single source.
        
        Args:
            source: Source entity
            hours: Hours to look back
            
        Returns:
            Number of articles scraped
        """
        # Create appropriate scraper
        source_type = SourceType(source.source_type)
        scraper = self._scraper_factory.create_scraper(source_type)
        
        # Scrape content
        scraped_content = scraper.scrape(hours)
        
        # Filter out duplicates
        new_content = self._filter_duplicates(scraped_content)
        
        # Convert to Article entities
        articles = [
            self._create_article_entity(content, source)
            for content in new_content
        ]
        
        # Bulk insert
        if articles:
            self._article_repo.bulk_create(articles)
        
        return len(articles)
    
    def _filter_duplicates(
        self, 
        content_list: List[ScrapedContent]
    ) -> List[ScrapedContent]:
        """
        Filter out content that already exists in database.
        
        Args:
            content_list: List of scraped content
            
        Returns:
            List of new content (not in database)
        """
        new_content = []
        
        for content in content_list:
            existing = self._article_repo.find_by_url(content.url)
            if not existing:
                new_content.append(content)
        
        return new_content
    
    def _create_article_entity(
        self, 
        content: ScrapedContent, 
        source: Source
    ) -> Article:
        """
        Convert ScrapedContent to Article entity.
        
        Args:
            content: Scraped content
            source: Source entity
            
        Returns:
            Article entity
        """
        return Article(
            source_id=source.id,
            title=content.title,
            content=content.content,
            url=content.url,
            published_at=content.published_at,
            metadata=content.metadata
        )
```

#### CategorizationService

```python
class CategorizationService:
    """
    Service for categorizing articles.
    
    Coordinates categorization agent and repositories.
    
    Attributes:
        _agent (CategorizationAgent): Categorization agent (private)
        _article_repo (ArticleRepository): Article repository (private)
        _category_repo (CategoryRepository): Category repository (private)
    """
    
    def __init__(
        self,
        agent: CategorizationAgent,
        article_repo: ArticleRepository,
        category_repo: CategoryRepository
    ):
        """
        Initialize categorization service.
        
        Args:
            agent: Categorization agent
            article_repo: Article repository
            category_repo: Category repository
        """
        self._agent = agent
        self._article_repo = article_repo
        self._category_repo = category_repo
    
    def categorize_articles(
        self, 
        article_ids: List[int]
    ) -> Dict[int, str]:
        """
        Categorize multiple articles.
        
        Args:
            article_ids: List of article IDs to categorize
            
        Returns:
            Dictionary mapping article IDs to category names
        """
        results = {}
        
        for article_id in article_ids:
            try:
                category_name = self._categorize_article(article_id)
                results[article_id] = category_name
            except Exception as e:
                print(f"Error categorizing article {article_id}: {str(e)}")
                results[article_id] = "Uncategorized"
        
        return results
    
    def _categorize_article(self, article_id: int) -> str:
        """
        Categorize a single article.
        
        Args:
            article_id: Article ID
            
        Returns:
            Category name
        """
        # Fetch article
        article = self._article_repo.find_by_id(article_id)
        if not article:
            raise ValueError(f"Article {article_id} not found")
        
        # Convert to ScrapedContent for agent
        content = ScrapedContent(
            title=article.title,
            content=article.content,
            url=article.url,
            published_at=article.published_at,
            source_type=article.source.source_type,
            metadata=article.metadata
        )
        
        # Categorize using agent
        result = self._agent.execute(content)
        
        # Find category entity
        category = self._category_repo.find_by_name(result.primary_category)
        if not category:
            raise ValueError(f"Category '{result.primary_category}' not found")
        
        # Update article
        article.category_id = category.id
        self._article_repo.update(article)
        
        return result.primary_category
```

#### SummarizationService

```python
class SummarizationService:
    """
    Service for generating article summaries.
    
    Coordinates summarization agent and repositories.
    
    Attributes:
        _agent (SummarizationAgent): Summarization agent (private)
        _article_repo (ArticleRepository): Article repository (private)
        _summary_repo (SummaryRepository): Summary repository (private)
    """
    
    def __init__(
        self,
        agent: SummarizationAgent,
        article_repo: ArticleRepository,
        summary_repo: SummaryRepository
    ):
        """Initialize summarization service."""
        self._agent = agent
        self._article_repo = article_repo
        self._summary_repo = summary_repo
    
    def summarize_articles(
        self, 
        article_ids: List[int]
    ) -> Dict[int, bool]:
        """
        Generate summaries for multiple articles.
        
        Args:
            article_ids: List of article IDs
            
        Returns:
            Dictionary mapping article IDs to success status
        """
        results = {}
        
        for article_id in article_ids:
            try:
                self._summarize_article(article_id)
                results[article_id] = True
            except Exception as e:
                print(f"Error summarizing article {article_id}: {str(e)}")
                results[article_id] = False
        
        return results
    
    def _summarize_article(self, article_id: int) -> None:
        """
        Generate summary for a single article.
        
        Args:
            article_id: Article ID
        """
        # Fetch article
        article = self._article_repo.find_by_id(article_id)
        if not article:
            raise ValueError(f"Article {article_id} not found")
        
        # Convert to ScrapedContent
        content = ScrapedContent(
            title=article.title,
            content=article.content,
            url=article.url,
            published_at=article.published_at,
            source_type=article.source.source_type,
            metadata=article.metadata
        )
        
        # Generate summary using agent
        category_name = article.category.name if article.category else "General"
        result = self._agent.execute(content, category_name)
        
        # Create summary entity
        summary = Summary(
            article_id=article.id,
            summary=result.summary,
            why_important=result.why_important,
            prelims_relevance=result.prelims_relevance,
            mains_relevance=result.mains_relevance,
            possible_questions=result.possible_questions,
            key_facts=result.key_facts
        )
        
        # Save summary
        self._summary_repo.create(summary)
```

#### RankingService

```python
class RankingService:
    """
    Service for ranking articles.
    
    Coordinates ranking agent and repositories.
    
    Attributes:
        _agent (RankingAgent): Ranking agent (private)
        _article_repo (ArticleRepository): Article repository (private)
        _ranking_repo (RankingRepository): Ranking repository (private)
    """
    
    def __init__(
        self,
        agent: RankingAgent,
        article_repo: ArticleRepository,
        ranking_repo: RankingRepository
    ):
        """Initialize ranking service."""
        self._agent = agent
        self._article_repo = article_repo
        self._ranking_repo = ranking_repo
    
    def rank_articles(
        self, 
        article_ids: List[int]
    ) -> Dict[int, float]:
        """
        Rank multiple articles.
        
        Args:
            article_ids: List of article IDs
            
        Returns:
            Dictionary mapping article IDs to scores
        """
        results = {}
        
        for article_id in article_ids:
            try:
                score = self._rank_article(article_id)
                results[article_id] = score
            except Exception as e:
                print(f"Error ranking article {article_id}: {str(e)}")
                results[article_id] = 0.0
        
        return results
    
    def _rank_article(self, article_id: int) -> float:
        """
        Rank a single article.
        
        Args:
            article_id: Article ID
            
        Returns:
            Relevance score
        """
        # Fetch article
        article = self._article_repo.find_by_id(article_id)
        if not article:
            raise ValueError(f"Article {article_id} not found")
        
        # Prepare metadata
        metadata = ArticleMetadata(
            category=article.category.name if article.category else "General",
            source_type=article.source.source_type,
            published_at=article.published_at,
            content_length=len(article.content),
            keywords=article.metadata.get('keywords', [])
        )
        
        # Convert to ScrapedContent
        content = ScrapedContent(
            title=article.title,
            content=article.content,
            url=article.url,
            published_at=article.published_at,
            source_type=article.source.source_type,
            metadata=article.metadata
        )
        
        # Rank using agent
        result = self._agent.execute(content, metadata)
        
        # Create ranking entity
        ranking = Ranking(
            article_id=article.id,
            score=result.score,
            exam_type=self._agent.strategy.exam_type,
            reasoning=result.reasoning,
            factors=result.factors
        )
        
        # Save ranking
        self._ranking_repo.create(ranking)
        
        return result.score
    
    def get_top_articles(
        self, 
        n: int, 
        exam_type: Optional[str] = None
    ) -> List[Article]:
        """
        Get top N ranked articles.
        
        Args:
            n: Number of articles to return
            exam_type: Optional exam type filter
            
        Returns:
            List of top articles
        """
        rankings = self._ranking_repo.find_top_n(n, exam_type)
        
        return [
            self._article_repo.find_by_id(ranking.article_id)
            for ranking in rankings
        ]
```

**Key Design Decisions**:
- Services orchestrate workflows, don't implement business logic directly
- Dependency Injection: services receive dependencies via constructor
- Services depend on abstractions (repository interfaces), not concrete classes
- Error handling at service level with logging
- Bulk operations for performance
- Clear separation: services coordinate, agents process, repositories persist


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following testable properties. Many criteria are examples (testing specific configurations or implementations) rather than universal properties. The properties below represent universal behaviors that should hold across all inputs.

**Redundancy Analysis**:
- Properties 2.4, 3.3, and 4.3 all test that scraped content contains required fields - these can be combined into a single property about scraper output validation
- Properties 7.2, 7.4, and 7.6 all relate to categorization constraints - these can be combined
- Properties 8.2 and 8.4 both relate to summary structure - these can be combined
- Properties 13.7, 21.4, and 21.6 all relate to error handling - these represent different aspects and should remain separate
- Properties 25.1, 25.2, 25.3, 25.4, and 25.5 all relate to logging - these can be combined into comprehensive logging properties


### Property 1: Scraper Output Completeness

*For any* content scraped by any scraper (YouTube, PIB, Government Schemes), the resulting ScrapedContent object SHALL contain all required fields: title (non-empty), content (non-empty), url (valid HTTP/HTTPS), published_at (valid datetime), source_type (non-empty), and metadata (dictionary).

**Validates: Requirements 2.4, 3.3, 4.3**

**Rationale**: This property ensures data quality and consistency across all scrapers. It prevents incomplete data from entering the pipeline, which could cause failures in downstream processing (categorization, summarization, ranking).

### Property 2: Time Window Filtering

*For any* scraper and any specified time window (hours parameter), all returned content SHALL have a published_at timestamp within the specified time range (now - hours <= published_at <= now).

**Validates: Requirements 3.4**

**Rationale**: This property ensures that scrapers correctly filter content by time, preventing old or future-dated content from being processed. This is critical for maintaining relevance in exam preparation.

### Property 3: Liskov Substitution for Scrapers

*For any* concrete scraper class (YouTubeScraper, PIBScraper, GovernmentSchemesScraper), instances SHALL be substitutable for AbstractScraper in all contexts, meaning they can be used wherever AbstractScraper is expected without breaking functionality.

**Validates: Requirements 5.4, 16.7**

**Rationale**: This property validates the Liskov Substitution Principle, ensuring that the inheritance hierarchy is correctly designed. It enables polymorphic usage of scrapers in the pipeline.

### Property 4: Factory Pattern Correctness

*For any* valid SourceType enum value, the ScraperFactory SHALL return a scraper instance of the correct type that inherits from AbstractScraper.

**Validates: Requirements 6.2**

**Rationale**: This property ensures the Factory Pattern is correctly implemented, enabling dynamic scraper creation based on configuration.

### Property 5: Categorization Constraints

*For any* article categorized by CategorizationAgent, the result SHALL contain exactly one primary category from the predefined list of eight categories (Polity, Economy, International Relations, Science & Tech, Environment & Ecology, Defence & Security, Government Schemes, Social Issues), and at most two secondary categories from the same list, with all categories being distinct.

**Validates: Requirements 7.2, 7.4, 7.6**

**Rationale**: This property ensures categorization output is well-formed and valid, preventing invalid categories from entering the system and ensuring consistent categorization structure.

### Property 6: Summary Structure Completeness

*For any* article summarized by SummarizationAgent, the resulting SummaryResult SHALL contain all required sections (summary, why_important, prelims_relevance, mains_relevance, possible_questions, key_facts), with the summary section containing between 200-300 words, and possible_questions containing at least 3 questions.

**Validates: Requirements 8.2, 8.4**

**Rationale**: This property ensures summaries are comprehensive and useful for exam preparation, with consistent structure across all articles.

### Property 7: Summary Content Fidelity

*For any* article summarized, the generated summary SHALL include at least one specific fact, name, date, or statistic that appears in the original article content, ensuring the summary is grounded in the source material.

**Validates: Requirements 8.6**

**Rationale**: This property prevents hallucination and ensures summaries are factually grounded in the source content, which is critical for exam preparation accuracy.

### Property 8: Ranking Score Bounds

*For any* article ranked by RankingAgent (regardless of strategy), the resulting score SHALL be a float value between 0.0 and 10.0 (inclusive).

**Validates: Requirements 10.4**

**Rationale**: This property ensures ranking scores are normalized and comparable across different strategies and articles.

### Property 9: Database Referential Integrity

*For any* delete operation on an article, all related entities (summary, ranking) SHALL either be deleted (cascade) or the operation SHALL fail, maintaining referential integrity.

**Validates: Requirements 12.7**

**Rationale**: This property ensures database consistency, preventing orphaned records that could cause application errors.

### Property 10: Repository Session Management

*For any* repository operation (create, update, delete, query), the database session SHALL be properly managed: opened before the operation, committed on success, rolled back on error, and closed in all cases.

**Validates: Requirements 13.7**

**Rationale**: This property prevents database connection leaks and ensures transaction consistency, which is critical for production reliability.

### Property 11: Pipeline Execution Order

*For any* pipeline execution, the stages SHALL execute in the exact order: Scrape → Categorize → Summarize → Rank → Store → Generate Digest, with each stage completing before the next begins.

**Validates: Requirements 15.2**

**Rationale**: This property ensures the pipeline maintains correct data dependencies, as each stage depends on the output of the previous stage.

### Property 12: Pipeline Progress Logging

*For any* pipeline execution, progress logs SHALL be generated at the start and end of each stage (Scrape, Categorize, Summarize, Rank, Store, Digest), with each log entry containing a timestamp and the stage name.

**Validates: Requirements 15.3, 25.1, 25.2**

**Rationale**: This property ensures observability of pipeline execution, enabling debugging and performance monitoring.

### Property 13: Pipeline Summary Report

*For any* completed pipeline execution, a summary report SHALL be generated containing: total articles scraped, articles categorized, articles summarized, articles ranked, top N articles selected, and total execution time.

**Validates: Requirements 15.5, 25.5**

**Rationale**: This property ensures pipeline execution is measurable and auditable, providing visibility into system performance.

### Property 14: External API Error Handling

*For any* external API call (Gemini API, YouTube API, PIB website), if an error occurs, the error SHALL be caught, logged with context (API name, operation, error message), and SHALL NOT crash the calling component.

**Validates: Requirements 21.4, 21.6**

**Rationale**: This property ensures system resilience to external failures, which is critical for production reliability given the dependency on external services.

### Property 15: API Call Latency Logging

*For any* Gemini API call, the latency (time from request to response) SHALL be measured and logged if it exceeds 1 second.

**Validates: Requirements 25.3**

**Rationale**: This property enables performance monitoring and identification of slow API calls that could impact user experience.

### Property 16: Slow Query Logging

*For any* database query that takes longer than 1 second to execute, the query execution time and query details SHALL be logged.

**Validates: Requirements 25.4**

**Rationale**: This property enables identification of performance bottlenecks in database access, supporting optimization efforts.


## Error Handling

### Error Handling Strategy

The system implements a layered error handling approach:

1. **Component Level**: Each component (scraper, agent, repository) handles its own errors
2. **Service Level**: Services catch component errors and decide whether to continue or fail
3. **Pipeline Level**: Pipeline catches service errors and continues with remaining items

### Error Categories

**Transient Errors** (retry-able):
- Network timeouts
- API rate limits
- Temporary database connection failures

**Permanent Errors** (non-retry-able):
- Invalid configuration
- Missing required data
- Authentication failures

### Error Handling Patterns

#### Scraper Error Handling

```python
class AbstractScraper(ABC):
    def scrape_with_retry(self, hours: int, max_retries: int = 3) -> List[ScrapedContent]:
        """
        Scrape with automatic retry for transient failures.
        
        Args:
            hours: Hours to look back
            max_retries: Maximum retry attempts
            
        Returns:
            List of scraped content
        """
        for attempt in range(max_retries):
            try:
                return self.scrape(hours)
            except TransientError as e:
                if attempt == max_retries - 1:
                    self._handle_network_error(e)
                    return []
                time.sleep(2 ** attempt)  # Exponential backoff
            except PermanentError as e:
                self._handle_network_error(e)
                return []
```

#### Agent Error Handling

```python
class AbstractAgent(ABC):
    def execute_with_fallback(self, input_data: Any, fallback_value: Any = None) -> Any:
        """
        Execute with fallback value on failure.
        
        Args:
            input_data: Input to process
            fallback_value: Value to return on failure
            
        Returns:
            Processed result or fallback value
        """
        try:
            return self.execute(input_data)
        except AgentException as e:
            print(f"Agent execution failed: {str(e)}")
            return fallback_value
```

#### Repository Error Handling

```python
class BaseRepository(Generic[T]):
    @contextmanager
    def _get_session(self):
        """Context manager with automatic rollback."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise RepositoryException(f"Database integrity error: {str(e)}")
        except OperationalError as e:
            session.rollback()
            raise RepositoryException(f"Database operational error: {str(e)}")
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
```

### Logging Strategy

**Log Levels**:
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages (pipeline progress)
- **WARNING**: Warning messages (non-critical errors)
- **ERROR**: Error messages (component failures)
- **CRITICAL**: Critical errors (system failures)

**Log Format**:
```
[TIMESTAMP] [LEVEL] [COMPONENT] [MESSAGE] [CONTEXT]
```

**Example**:
```
[2024-01-15 10:30:45] [ERROR] [YouTubeScraper] Failed to fetch transcript for video abc123 [channel_id=UCxxx, error=TranscriptsDisabled]
```


## Testing Strategy

### Dual Testing Approach

The system requires both unit testing and property-based testing for comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and error conditions
**Property Tests**: Verify universal properties across all inputs

Together, these approaches provide comprehensive coverage: unit tests catch concrete bugs, property tests verify general correctness.

### Property-Based Testing

**Library Selection**: Use `hypothesis` for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: competitive-exam-intelligence-system, Property {number}: {property_text}`

**Example Property Test**:

```python
from hypothesis import given, strategies as st
import pytest

# Feature: competitive-exam-intelligence-system, Property 1: Scraper Output Completeness
@given(
    scraper_type=st.sampled_from([SourceType.YOUTUBE, SourceType.PIB, SourceType.GOVERNMENT_SCHEMES]),
    hours=st.integers(min_value=1, max_value=168)
)
@pytest.mark.property_test
def test_scraper_output_completeness(scraper_type, hours):
    """
    Property 1: For any scraper and time window, output contains all required fields.
    """
    # Arrange
    scraper = ScraperFactory.create_scraper(scraper_type)
    
    # Act
    results = scraper.scrape(hours)
    
    # Assert
    for content in results:
        assert len(content.title) > 0, "Title must be non-empty"
        assert len(content.content) > 0, "Content must be non-empty"
        assert content.url.startswith('http'), "URL must be valid HTTP/HTTPS"
        assert isinstance(content.published_at, datetime), "Published date must be datetime"
        assert len(content.source_type) > 0, "Source type must be non-empty"
        assert isinstance(content.metadata, dict), "Metadata must be dictionary"


# Feature: competitive-exam-intelligence-system, Property 5: Categorization Constraints
@given(
    article_content=st.text(min_size=100, max_size=5000),
    article_title=st.text(min_size=10, max_size=200)
)
@pytest.mark.property_test
def test_categorization_constraints(article_content, article_title):
    """
    Property 5: For any article, categorization produces valid category structure.
    """
    # Arrange
    agent = CategorizationAgent(config=test_config)
    content = ScrapedContent(
        title=article_title,
        content=article_content,
        url="https://example.com/test",
        published_at=datetime.now(timezone.utc),
        source_type="test"
    )
    
    # Act
    result = agent.execute(content)
    
    # Assert
    valid_categories = CategorizationAgent.EXAM_CATEGORIES
    assert result.primary_category in valid_categories, "Primary category must be valid"
    assert len(result.secondary_categories) <= 2, "At most 2 secondary categories"
    for cat in result.secondary_categories:
        assert cat in valid_categories, "Secondary categories must be valid"
    
    all_categories = [result.primary_category] + result.secondary_categories
    assert len(all_categories) == len(set(all_categories)), "Categories must be distinct"


# Feature: competitive-exam-intelligence-system, Property 8: Ranking Score Bounds
@given(
    strategy=st.sampled_from([
        UPSCRankingStrategy(),
        SSCRankingStrategy(),
        BankingRankingStrategy()
    ]),
    content_length=st.integers(min_value=100, max_value=10000),
    published_hours_ago=st.integers(min_value=0, max_value=168)
)
@pytest.mark.property_test
def test_ranking_score_bounds(strategy, content_length, published_hours_ago):
    """
    Property 8: For any article and strategy, ranking score is between 0.0 and 10.0.
    """
    # Arrange
    published_at = datetime.now(timezone.utc) - timedelta(hours=published_hours_ago)
    metadata = ArticleMetadata(
        category="Economy",
        source_type="pib",
        published_at=published_at,
        content_length=content_length,
        keywords=[]
    )
    content = "Test content " * (content_length // 13)
    
    # Act
    result = strategy.calculate_score(content, metadata)
    
    # Assert
    assert 0.0 <= result.score <= 10.0, f"Score must be between 0.0 and 10.0, got {result.score}"
    assert isinstance(result.score, float), "Score must be float"
```

### Unit Testing Strategy

**Test Organization**:
```
tests/
├── unit/
│   ├── test_scrapers.py
│   ├── test_agents.py
│   ├── test_strategies.py
│   ├── test_repositories.py
│   └── test_services.py
├── integration/
│   ├── test_pipeline.py
│   └── test_database.py
├── property/
│   ├── test_scraper_properties.py
│   ├── test_agent_properties.py
│   └── test_pipeline_properties.py
└── conftest.py
```

**Unit Test Examples**:

```python
# Unit test for specific example
def test_youtube_scraper_with_specific_channel():
    """Test YouTubeScraper with a known channel."""
    scraper = YouTubeScraper(channel_ids=["UCYRBFLkuZ8ZAfwz7ayGGvZQ"])
    results = scraper.scrape(hours=24)
    
    assert isinstance(results, list)
    for content in results:
        assert content.source_type == "youtube"


# Unit test for edge case
def test_youtube_scraper_with_no_transcript():
    """Test YouTubeScraper handles missing transcripts gracefully."""
    scraper = YouTubeScraper()
    # Mock video with no transcript
    video_id = "test_no_transcript"
    
    transcript = scraper._get_transcript(video_id)
    
    assert transcript is None  # Should return None, not crash


# Unit test for error condition
def test_pib_scraper_network_error():
    """Test PIBScraper handles network errors gracefully."""
    scraper = PIBScraper()
    
    with patch('requests.get', side_effect=requests.ConnectionError):
        results = scraper.scrape(hours=24)
    
    assert results == []  # Should return empty list, not crash
```

### Integration Testing

**Database Integration Tests**:

```python
@pytest.fixture
def test_db():
    """Create test database."""
    engine = create_engine("postgresql://test:test@localhost/test_db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


def test_article_repository_integration(test_db):
    """Test ArticleRepository with real database."""
    session_factory = sessionmaker(bind=test_db)
    repo = ArticleRepository(session_factory)
    
    # Create article
    article = Article(
        source_id=1,
        title="Test Article",
        content="Test content",
        url="https://example.com/test",
        published_at=datetime.now(timezone.utc)
    )
    
    created = repo.create(article)
    assert created.id is not None
    
    # Find by ID
    found = repo.find_by_id(created.id)
    assert found.title == "Test Article"
```

**Pipeline Integration Tests**:

```python
def test_full_pipeline_execution():
    """Test complete pipeline execution."""
    # Arrange
    pipeline = Pipeline(
        scraping_service=scraping_service,
        categorization_service=categorization_service,
        summarization_service=summarization_service,
        ranking_service=ranking_service,
        digest_service=digest_service
    )
    
    # Act
    result = pipeline.execute(hours=24, top_n=10)
    
    # Assert
    assert result.articles_scraped > 0
    assert result.articles_categorized > 0
    assert result.articles_summarized > 0
    assert result.articles_ranked > 0
    assert len(result.top_articles) <= 10
```

### Test Coverage Goals

- **Unit Test Coverage**: Minimum 80% code coverage
- **Property Test Coverage**: All 16 correctness properties must have corresponding property tests
- **Integration Test Coverage**: All service interactions and database operations
- **Edge Case Coverage**: All error conditions and boundary cases

### Continuous Integration

**CI Pipeline**:
1. Run unit tests
2. Run property tests (100 iterations each)
3. Run integration tests
4. Check code coverage (minimum 80%)
5. Run linting (flake8, mypy)
6. Run security checks (bandit)


## UML Diagrams

### Class Diagram

```mermaid
classDiagram
    %% Abstract Base Classes
    class AbstractScraper {
        <<abstract>>
        -_source_name: str
        -_base_url: str
        -_timeout: int
        +source_name: str
        +scrape(hours: int)* List~ScrapedContent~
        +validate_content(content: ScrapedContent) bool
        #_handle_network_error(error: Exception) void
    }
    
    class AbstractAgent {
        <<abstract>>
        -_config: AgentConfig
        -_client: GenerativeModel
        +model_name: str
        +execute(input_data: Any)* Any
        #_call_gemini_api(prompt: str) str
        #_parse_json_response(response: str) dict
    }
    
    class AbstractRankingStrategy {
        <<abstract>>
        -_exam_type: str
        -_weights: Dict~str, float~
        +exam_type: str
        +calculate_score(content: str, metadata: ArticleMetadata)* RankingResult
        #_validate_weights() void
        #_calculate_freshness_score(published_at: datetime) float
        #_calculate_category_relevance(category: str, priorities: List~str~) float
    }
    
    %% Concrete Scrapers
    class YouTubeScraper {
        -_channel_ids: List~str~
        -_transcript_api: YouTubeTranscriptApi
        +EXAM_CHANNELS: List~str~
        +scrape(hours: int) List~ScrapedContent~
        -_get_recent_videos(channel_id: str, hours: int) List~dict~
        -_extract_video_id(url: str) str
        -_get_transcript(video_id: str) Optional~str~
    }
    
    class PIBScraper {
        -_categories: List~str~
        +EXAM_RELEVANT_CATEGORIES: List~str~
        +scrape(hours: int) List~ScrapedContent~
        -_scrape_category(category: str, cutoff_time: datetime) List~ScrapedContent~
        -_parse_release(item: BeautifulSoup, category: str) Optional~ScrapedContent~
        -_extract_ministry(content: str) str
    }
    
    class GovernmentSchemesScraper {
        -_scheme_portals: List~str~
        +SCHEME_PORTALS: List~str~
        +scrape(hours: int) List~ScrapedContent~
        -_scrape_portal(portal_url: str, hours: int) List~ScrapedContent~
        -_parse_scheme(item: BeautifulSoup, portal_url: str) Optional~ScrapedContent~
        -_extract_scheme_metadata(item: BeautifulSoup) Dict~str, str~
        -_format_scheme_content(description: str, metadata: Dict) str
    }
    
    %% Factory
    class ScraperFactory {
        <<factory>>
        -_registry: Dict~SourceType, Type~AbstractScraper~~
        +register_scraper(source_type: SourceType, scraper_class: Type) void
        +create_scraper(source_type: SourceType, **kwargs) AbstractScraper
        +get_available_sources() List~SourceType~
        +create_all_scrapers() List~AbstractScraper~
    }
    
    %% Concrete Agents
    class CategorizationAgent {
        -_categories: List~str~
        +EXAM_CATEGORIES: List~str~
        +execute(content: ScrapedContent) CategoryResult
        -_build_categorization_prompt(content: ScrapedContent) str
        -_validate_categories(result: CategoryResult) void
    }
    
    class SummarizationAgent {
        -_max_summary_words: int
        +execute(content: ScrapedContent, category: str) SummaryResult
        -_build_summarization_prompt(content: ScrapedContent, category: str) str
        +get_formatted_summary(result: SummaryResult) str
    }
    
    class RankingAgent {
        -_strategy: AbstractRankingStrategy
        +strategy: AbstractRankingStrategy
        +execute(content: ScrapedContent, metadata: ArticleMetadata) RankingResult
        +set_strategy(strategy: AbstractRankingStrategy) void
        -_should_use_ai_enhancement(result: RankingResult) bool
        -_enhance_with_ai(content: ScrapedContent, initial_result: RankingResult) RankingResult
    }
    
    class DigestAgent {
        -_digest_title: str
        +execute(articles: List~DigestArticle~) DigestResult
        -_group_by_category(articles: List~DigestArticle~) Dict~str, List~DigestArticle~~
        -_generate_introduction(articles: List~DigestArticle~) str
        -_generate_conclusion(articles: List~DigestArticle~) str
        -_get_top_categories(articles: List~DigestArticle~, n: int) List~str~
        +format_as_text(digest: DigestResult) str
    }
    
    %% Concrete Strategies
    class UPSCRankingStrategy {
        +PRIORITY_CATEGORIES: List~str~
        +DEFAULT_WEIGHTS: Dict~str, float~
        +calculate_score(content: str, metadata: ArticleMetadata) RankingResult
        -_calculate_content_depth(content: str, length: int) float
        -_calculate_source_credibility(source_type: str) float
        -_generate_reasoning(factors: Dict, final_score: float) str
    }
    
    class SSCRankingStrategy {
        +PRIORITY_CATEGORIES: List~str~
        +DEFAULT_WEIGHTS: Dict~str, float~
        +calculate_score(content: str, metadata: ArticleMetadata) RankingResult
        -_calculate_factual_density(content: str) float
        -_calculate_source_credibility(source_type: str) float
        -_generate_reasoning(factors: Dict, final_score: float) str
    }
    
    class BankingRankingStrategy {
        +PRIORITY_CATEGORIES: List~str~
        +DEFAULT_WEIGHTS: Dict~str, float~
        +BANKING_KEYWORDS: List~str~
        +calculate_score(content: str, metadata: ArticleMetadata) RankingResult
        -_calculate_banking_keyword_score(content: str) float
        -_calculate_source_credibility(source_type: str) float
        -_generate_reasoning(factors: Dict, final_score: float) str
    }
    
    %% Repositories
    class BaseRepository~T~ {
        <<generic>>
        -_model_class: Type~T~
        -_session_factory: sessionmaker
        +create(entity: T) T
        +find_by_id(entity_id: int) Optional~T~
        +find_all() List~T~
        +update(entity: T) T
        +delete(entity_id: int) bool
        #_get_session() Session
    }
    
    class ArticleRepository {
        +find_by_date_range(start_date: datetime, end_date: datetime) List~Article~
        +find_by_category(category_id: int) List~Article~
        +find_by_source(source_id: int) List~Article~
        +find_by_url(url: str) Optional~Article~
        +bulk_create(articles: List~Article~) List~Article~
    }
    
    class SummaryRepository {
        +find_by_article_id(article_id: int) Optional~Summary~
    }
    
    class RankingRepository {
        +find_by_article_id(article_id: int) Optional~Ranking~
        +find_top_n(n: int, exam_type: Optional~str~) List~Ranking~
        +find_by_score_range(min_score: float, max_score: float) List~Ranking~
    }
    
    class CategoryRepository {
        +find_by_name(name: str) Optional~Category~
        +find_all_ordered() List~Category~
    }
    
    class SourceRepository {
        +find_by_type(source_type: str) List~Source~
        +find_active_sources() List~Source~
    }
    
    %% Services
    class ScrapingService {
        -_scraper_factory: ScraperFactory
        -_article_repo: ArticleRepository
        -_source_repo: SourceRepository
        +scrape_all_sources(hours: int) Dict~str, int~
        -_scrape_source(source: Source, hours: int) int
        -_filter_duplicates(content_list: List~ScrapedContent~) List~ScrapedContent~
        -_create_article_entity(content: ScrapedContent, source: Source) Article
    }
    
    class CategorizationService {
        -_agent: CategorizationAgent
        -_article_repo: ArticleRepository
        -_category_repo: CategoryRepository
        +categorize_articles(article_ids: List~int~) Dict~int, str~
        -_categorize_article(article_id: int) str
    }
    
    class SummarizationService {
        -_agent: SummarizationAgent
        -_article_repo: ArticleRepository
        -_summary_repo: SummaryRepository
        +summarize_articles(article_ids: List~int~) Dict~int, bool~
        -_summarize_article(article_id: int) void
    }
    
    class RankingService {
        -_agent: RankingAgent
        -_article_repo: ArticleRepository
        -_ranking_repo: RankingRepository
        +rank_articles(article_ids: List~int~) Dict~int, float~
        -_rank_article(article_id: int) float
        +get_top_articles(n: int, exam_type: Optional~str~) List~Article~
    }
    
    %% Relationships - Inheritance
    AbstractScraper <|-- YouTubeScraper
    AbstractScraper <|-- PIBScraper
    AbstractScraper <|-- GovernmentSchemesScraper
    
    AbstractAgent <|-- CategorizationAgent
    AbstractAgent <|-- SummarizationAgent
    AbstractAgent <|-- RankingAgent
    AbstractAgent <|-- DigestAgent
    
    AbstractRankingStrategy <|-- UPSCRankingStrategy
    AbstractRankingStrategy <|-- SSCRankingStrategy
    AbstractRankingStrategy <|-- BankingRankingStrategy
    
    BaseRepository <|-- ArticleRepository
    BaseRepository <|-- SummaryRepository
    BaseRepository <|-- RankingRepository
    BaseRepository <|-- CategoryRepository
    BaseRepository <|-- SourceRepository
    
    %% Relationships - Composition
    RankingAgent *-- AbstractRankingStrategy : contains
    ScraperFactory ..> AbstractScraper : creates
    
    %% Relationships - Dependency
    ScrapingService ..> ScraperFactory : uses
    ScrapingService ..> ArticleRepository : uses
    ScrapingService ..> SourceRepository : uses
    
    CategorizationService ..> CategorizationAgent : uses
    CategorizationService ..> ArticleRepository : uses
    CategorizationService ..> CategoryRepository : uses
    
    SummarizationService ..> SummarizationAgent : uses
    SummarizationService ..> ArticleRepository : uses
    SummarizationService ..> SummaryRepository : uses
    
    RankingService ..> RankingAgent : uses
    RankingService ..> ArticleRepository : uses
    RankingService ..> RankingRepository : uses
```


## Configuration Management

### Configuration Structure

The system uses environment variables for configuration, with a centralized Config class for access.

#### Config Class

```python
import os
from typing import List, Dict, Optional
from pydantic import BaseSettings, Field, validator


class Config(BaseSettings):
    """
    Centralized configuration management.
    
    Uses Pydantic BaseSettings for automatic environment variable loading
    and validation.
    """
    
    # Database Configuration
    DATABASE_URL: str = Field(..., env='DATABASE_URL')
    DB_POOL_SIZE: int = Field(5, env='DB_POOL_SIZE')
    DB_MAX_OVERFLOW: int = Field(10, env='DB_MAX_OVERFLOW')
    
    # Gemini API Configuration
    GEMINI_API_KEY: str = Field(..., env='GEMINI_API_KEY')
    GEMINI_MODEL: str = Field('gemini-1.5-flash', env='GEMINI_MODEL')
    GEMINI_TEMPERATURE: float = Field(0.7, env='GEMINI_TEMPERATURE')
    GEMINI_MAX_TOKENS: int = Field(2048, env='GEMINI_MAX_TOKENS')
    
    # YouTube Configuration
    YOUTUBE_CHANNELS: List[str] = Field(
        default=[
            "UCYRBFLkuZ8ZAfwz7ayGGvZQ",  # StudyIQ IAS
            "UCnvC2wLZOiKdFkM8Ml4EzQg",  # Drishti IAS
            "UCZ8QY-RF48rE3LJRgdD0kVQ",  # Vision IAS
            "UCawZsQWqfGSbCI5yjkdVkTA",  # OnlyIAS
            "UCOEVlIHEsILuTV_Ix8dDW5A",  # Insights IAS
            "UCawZsQWqfGSbCI5yjkdVkTB",  # PIB India Official
            "UCawZsQWqfGSbCI5yjkdVkTC",  # Sansad TV
            "UCawZsQWqfGSbCI5yjkdVkTD",  # Vajiram & Ravi
            "UCawZsQWqfGSbCI5yjkdVkTE",  # Adda247
            "UCawZsQWqfGSbCI5yjkdVkTF",  # BYJU'S Exam Prep
            "UCawZsQWqfGSbCI5yjkdVkTG",  # Unacademy UPSC
        ],
        env='YOUTUBE_CHANNELS'
    )
    PROXY_USERNAME: Optional[str] = Field(None, env='PROXY_USERNAME')
    PROXY_PASSWORD: Optional[str] = Field(None, env='PROXY_PASSWORD')
    
    # PIB Configuration
    PIB_BASE_URL: str = Field('https://pib.gov.in', env='PIB_BASE_URL')
    PIB_CATEGORIES: List[str] = Field(
        default=[
            "Government Policies",
            "Economy",
            "Defence",
            "International Relations",
            "Science & Technology",
            "Environment",
            "Social Welfare"
        ],
        env='PIB_CATEGORIES'
    )
    
    # Government Schemes Configuration
    SCHEME_PORTALS: List[str] = Field(
        default=[
            "https://www.india.gov.in/spotlight/schemes",
            "https://www.myscheme.gov.in/",
        ],
        env='SCHEME_PORTALS'
    )
    
    # Scraping Configuration
    SCRAPING_TIMEOUT: int = Field(30, env='SCRAPING_TIMEOUT')
    DEFAULT_LOOKBACK_HOURS: int = Field(24, env='DEFAULT_LOOKBACK_HOURS')
    
    # Ranking Configuration
    DEFAULT_EXAM_TYPE: str = Field('UPSC', env='DEFAULT_EXAM_TYPE')
    UPSC_WEIGHTS: Dict[str, float] = Field(
        default={
            'category_relevance': 0.35,
            'freshness': 0.20,
            'content_depth': 0.25,
            'source_credibility': 0.20
        },
        env='UPSC_WEIGHTS'
    )
    SSC_WEIGHTS: Dict[str, float] = Field(
        default={
            'category_relevance': 0.30,
            'freshness': 0.35,
            'factual_density': 0.25,
            'source_credibility': 0.10
        },
        env='SSC_WEIGHTS'
    )
    BANKING_WEIGHTS: Dict[str, float] = Field(
        default={
            'category_relevance': 0.40,
            'freshness': 0.25,
            'banking_keywords': 0.25,
            'source_credibility': 0.10
        },
        env='BANKING_WEIGHTS'
    )
    
    # Summarization Configuration
    MAX_SUMMARY_WORDS: int = Field(250, env='MAX_SUMMARY_WORDS')
    
    # Pipeline Configuration
    ENABLE_PARALLEL_SCRAPING: bool = Field(True, env='ENABLE_PARALLEL_SCRAPING')
    MAX_WORKERS: int = Field(4, env='MAX_WORKERS')
    
    # Logging Configuration
    LOG_LEVEL: str = Field('INFO', env='LOG_LEVEL')
    LOG_FORMAT: str = Field(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        env='LOG_FORMAT'
    )
    
    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith('postgresql://'):
            raise ValueError('DATABASE_URL must be a PostgreSQL connection string')
        return v
    
    @validator('GEMINI_API_KEY')
    def validate_gemini_api_key(cls, v):
        """Validate Gemini API key is not empty."""
        if not v or len(v) < 10:
            raise ValueError('GEMINI_API_KEY must be a valid API key')
        return v
    
    @validator('DEFAULT_EXAM_TYPE')
    def validate_exam_type(cls, v):
        """Validate exam type is supported."""
        valid_types = ['UPSC', 'SSC', 'Banking']
        if v not in valid_types:
            raise ValueError(f'DEFAULT_EXAM_TYPE must be one of {valid_types}')
        return v
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True


# Singleton instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get configuration singleton.
    
    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config
```

### Environment Variables

**.env.example**:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/exam_intelligence
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048

# YouTube Configuration (comma-separated channel IDs)
YOUTUBE_CHANNELS=UCYRBFLkuZ8ZAfwz7ayGGvZQ,UCnvC2wLZOiKdFkM8Ml4EzQg
PROXY_USERNAME=  # Optional: for YouTube transcript proxy
PROXY_PASSWORD=  # Optional: for YouTube transcript proxy

# PIB Configuration
PIB_BASE_URL=https://pib.gov.in
PIB_CATEGORIES=Government Policies,Economy,Defence

# Scraping Configuration
SCRAPING_TIMEOUT=30
DEFAULT_LOOKBACK_HOURS=24

# Ranking Configuration
DEFAULT_EXAM_TYPE=UPSC

# Summarization Configuration
MAX_SUMMARY_WORDS=250

# Pipeline Configuration
ENABLE_PARALLEL_SCRAPING=true
MAX_WORKERS=4

# Logging Configuration
LOG_LEVEL=INFO
```

### Configuration Validation

The system validates configuration on startup:

```python
def validate_configuration():
    """
    Validate configuration on startup.
    
    Raises:
        ConfigurationError: If configuration is invalid
    """
    try:
        config = get_config()
        
        # Test database connection
        engine = create_engine(config.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        # Test Gemini API
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        model.generate_content("Test")
        
        print("✓ Configuration validated successfully")
        
    except Exception as e:
        raise ConfigurationError(f"Configuration validation failed: {str(e)}")
```


## CLI Pipeline Design

### Pipeline Orchestration

The CLI pipeline orchestrates the complete workflow from scraping to digest generation.

#### Pipeline Class

```python
from typing import Dict, List
from datetime import datetime, timezone
import argparse
import logging


class PipelineResult(BaseModel):
    """Result of pipeline execution."""
    articles_scraped: int
    articles_categorized: int
    articles_summarized: int
    articles_ranked: int
    top_articles_selected: int
    execution_time_seconds: float
    errors: List[str] = []


class Pipeline:
    """
    Main pipeline orchestrator.
    
    Coordinates all services to execute the complete workflow.
    
    Attributes:
        _scraping_service: Service for scraping (private)
        _categorization_service: Service for categorization (private)
        _summarization_service: Service for summarization (private)
        _ranking_service: Service for ranking (private)
        _digest_service: Service for digest generation (private)
        _logger: Logger instance (private)
    """
    
    def __init__(
        self,
        scraping_service: ScrapingService,
        categorization_service: CategorizationService,
        summarization_service: SummarizationService,
        ranking_service: RankingService,
        digest_service: DigestAgent
    ):
        """
        Initialize pipeline with services.
        
        Demonstrates Dependency Injection pattern.
        
        Args:
            scraping_service: Service for scraping
            categorization_service: Service for categorization
            summarization_service: Service for summarization
            ranking_service: Service for ranking
            digest_service: Agent for digest generation
        """
        self._scraping_service = scraping_service
        self._categorization_service = categorization_service
        self._summarization_service = summarization_service
        self._ranking_service = ranking_service
        self._digest_service = digest_service
        self._logger = logging.getLogger(__name__)
    
    def execute(
        self, 
        hours: int = 24, 
        top_n: int = 10,
        dry_run: bool = False
    ) -> PipelineResult:
        """
        Execute the complete pipeline.
        
        Args:
            hours: Number of hours to look back
            top_n: Number of top articles to select
            dry_run: If True, skip database writes
            
        Returns:
            PipelineResult with execution statistics
        """
        start_time = datetime.now(timezone.utc)
        result = PipelineResult(
            articles_scraped=0,
            articles_categorized=0,
            articles_summarized=0,
            articles_ranked=0,
            top_articles_selected=0,
            execution_time_seconds=0.0
        )
        
        try:
            # Stage 1: Scrape
            self._logger.info(f"[{datetime.now()}] Starting Stage 1: Scraping")
            scrape_results = self._scraping_service.scrape_all_sources(hours)
            result.articles_scraped = sum(scrape_results.values())
            self._logger.info(f"[{datetime.now()}] Scraped {result.articles_scraped} articles")
            
            if result.articles_scraped == 0:
                self._logger.warning("No articles scraped, ending pipeline")
                return result
            
            # Get article IDs for processing
            article_ids = self._get_recent_article_ids(hours)
            
            # Stage 2: Categorize
            self._logger.info(f"[{datetime.now()}] Starting Stage 2: Categorization")
            categorize_results = self._categorization_service.categorize_articles(article_ids)
            result.articles_categorized = sum(1 for success in categorize_results.values() if success)
            self._logger.info(f"[{datetime.now()}] Categorized {result.articles_categorized} articles")
            
            # Stage 3: Summarize
            self._logger.info(f"[{datetime.now()}] Starting Stage 3: Summarization")
            summarize_results = self._summarization_service.summarize_articles(article_ids)
            result.articles_summarized = sum(1 for success in summarize_results.values() if success)
            self._logger.info(f"[{datetime.now()}] Summarized {result.articles_summarized} articles")
            
            # Stage 4: Rank
            self._logger.info(f"[{datetime.now()}] Starting Stage 4: Ranking")
            rank_results = self._ranking_service.rank_articles(article_ids)
            result.articles_ranked = len(rank_results)
            self._logger.info(f"[{datetime.now()}] Ranked {result.articles_ranked} articles")
            
            # Stage 5: Select Top N
            self._logger.info(f"[{datetime.now()}] Starting Stage 5: Selecting Top {top_n}")
            top_articles = self._ranking_service.get_top_articles(top_n)
            result.top_articles_selected = len(top_articles)
            self._logger.info(f"[{datetime.now()}] Selected {result.top_articles_selected} top articles")
            
            # Stage 6: Generate Digest
            self._logger.info(f"[{datetime.now()}] Starting Stage 6: Digest Generation")
            digest_articles = self._prepare_digest_articles(top_articles)
            digest = self._digest_service.execute(digest_articles)
            
            # Output digest
            print("\n" + "=" * 80)
            print(self._digest_service.format_as_text(digest))
            print("=" * 80 + "\n")
            
        except Exception as e:
            self._logger.error(f"Pipeline execution failed: {str(e)}")
            result.errors.append(str(e))
        
        finally:
            end_time = datetime.now(timezone.utc)
            result.execution_time_seconds = (end_time - start_time).total_seconds()
            self._logger.info(f"Pipeline completed in {result.execution_time_seconds:.2f} seconds")
        
        return result
    
    def _get_recent_article_ids(self, hours: int) -> List[int]:
        """Get IDs of recently scraped articles."""
        # Implementation depends on repository
        pass
    
    def _prepare_digest_articles(self, articles: List[Article]) -> List[DigestArticle]:
        """Convert Article entities to DigestArticle format."""
        # Implementation depends on data models
        pass


def main():
    """
    CLI entrypoint for pipeline execution.
    """
    parser = argparse.ArgumentParser(
        description='Run the Competitive Exam Intelligence System pipeline'
    )
    parser.add_argument(
        'hours',
        type=int,
        nargs='?',
        default=24,
        help='Number of hours to look back (default: 24)'
    )
    parser.add_argument(
        'top_n',
        type=int,
        nargs='?',
        default=10,
        help='Number of top articles to select (default: 10)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without writing to database'
    )
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Skip email sending'
    )
    parser.add_argument(
        '--exam-type',
        type=str,
        choices=['UPSC', 'SSC', 'Banking'],
        help='Exam type for ranking (default: from config)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
    )
    
    # Validate configuration
    try:
        validate_configuration()
    except ConfigurationError as e:
        print(f"Configuration error: {str(e)}")
        return 1
    
    # Initialize services (dependency injection)
    config = get_config()
    
    # Create database session factory
    engine = create_engine(config.DATABASE_URL)
    session_factory = sessionmaker(bind=engine)
    
    # Create repositories
    article_repo = ArticleRepository(session_factory)
    summary_repo = SummaryRepository(session_factory)
    ranking_repo = RankingRepository(session_factory)
    category_repo = CategoryRepository(session_factory)
    source_repo = SourceRepository(session_factory)
    
    # Create agents
    agent_config = AgentConfig(
        model_name=config.GEMINI_MODEL,
        temperature=config.GEMINI_TEMPERATURE,
        max_tokens=config.GEMINI_MAX_TOKENS,
        api_key=config.GEMINI_API_KEY
    )
    
    categorization_agent = CategorizationAgent(agent_config)
    summarization_agent = SummarizationAgent(agent_config, config.MAX_SUMMARY_WORDS)
    
    # Create ranking strategy based on exam type
    exam_type = args.exam_type or config.DEFAULT_EXAM_TYPE
    if exam_type == 'UPSC':
        strategy = UPSCRankingStrategy(config.UPSC_WEIGHTS)
    elif exam_type == 'SSC':
        strategy = SSCRankingStrategy(config.SSC_WEIGHTS)
    else:
        strategy = BankingRankingStrategy(config.BANKING_WEIGHTS)
    
    ranking_agent = RankingAgent(agent_config, strategy)
    digest_agent = DigestAgent(agent_config)
    
    # Create services
    scraping_service = ScrapingService(
        ScraperFactory,
        article_repo,
        source_repo
    )
    categorization_service = CategorizationService(
        categorization_agent,
        article_repo,
        category_repo
    )
    summarization_service = SummarizationService(
        summarization_agent,
        article_repo,
        summary_repo
    )
    ranking_service = RankingService(
        ranking_agent,
        article_repo,
        ranking_repo
    )
    
    # Create and execute pipeline
    pipeline = Pipeline(
        scraping_service,
        categorization_service,
        summarization_service,
        ranking_service,
        digest_agent
    )
    
    result = pipeline.execute(
        hours=args.hours,
        top_n=args.top_n,
        dry_run=args.dry_run
    )
    
    # Print summary
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Articles Scraped:      {result.articles_scraped}")
    print(f"Articles Categorized:  {result.articles_categorized}")
    print(f"Articles Summarized:   {result.articles_summarized}")
    print(f"Articles Ranked:       {result.articles_ranked}")
    print(f"Top Articles Selected: {result.top_articles_selected}")
    print(f"Execution Time:        {result.execution_time_seconds:.2f} seconds")
    
    if result.errors:
        print(f"\nErrors: {len(result.errors)}")
        for error in result.errors:
            print(f"  - {error}")
    
    print("=" * 80 + "\n")
    
    return 0 if not result.errors else 1


if __name__ == '__main__':
    exit(main())
```

### CLI Usage Examples

```bash
# Run pipeline for last 24 hours, select top 10 articles
python scripts/run_pipeline.py 24 10

# Run pipeline for last 48 hours, select top 15 articles
python scripts/run_pipeline.py 48 15

# Run pipeline with dry-run (no database writes)
python scripts/run_pipeline.py 24 10 --dry-run

# Run pipeline without email
python scripts/run_pipeline.py 24 10 --no-email

# Run pipeline for SSC exam type
python scripts/run_pipeline.py 24 10 --exam-type SSC

# Run pipeline for Banking exam type
python scripts/run_pipeline.py 24 10 --exam-type Banking
```


## Deployment and Production Readiness

### Docker Configuration

**Dockerfile** (maintained from existing system):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run pipeline
CMD ["python", "scripts/run_pipeline.py", "24", "10"]
```

### Render Deployment

**render.yaml** (maintained from existing system):

```yaml
services:
  # PostgreSQL Database
  - type: pserv
    name: exam-intelligence-db
    env: docker
    plan: free
    region: oregon
    databases:
      - name: exam_intelligence
        user: exam_user

  # Background Worker (Pipeline)
  - type: worker
    name: exam-intelligence-worker
    env: docker
    plan: free
    region: oregon
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: exam-intelligence-db
          property: connectionString
      - key: GEMINI_API_KEY
        sync: false  # Set manually in Render dashboard
      - key: DEFAULT_EXAM_TYPE
        value: UPSC
      - key: LOG_LEVEL
        value: INFO

  # Cron Job (Daily Execution)
  - type: cron
    name: exam-intelligence-daily
    env: docker
    schedule: "0 6 * * *"  # Run at 6 AM UTC daily
    dockerfilePath: ./Dockerfile
    dockerCommand: python scripts/run_pipeline.py 24 10
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: exam-intelligence-db
          property: connectionString
      - key: GEMINI_API_KEY
        sync: false
```

### Database Migration

**Migration Script** (app/database/migrations/001_transform_to_exam_system.py):

```python
"""
Migration: Transform AI News Aggregator to Exam Intelligence System

This migration:
1. Adds new tables (categories, rankings, user_profiles)
2. Modifies existing tables (articles, summaries)
3. Migrates existing data
4. Creates indexes
"""

from sqlalchemy import create_engine, text
from app.database.models import Base
from app.config import get_config


def upgrade():
    """Apply migration."""
    config = get_config()
    engine = create_engine(config.DATABASE_URL)
    
    with engine.begin() as conn:
        # 1. Create new tables
        print("Creating new tables...")
        Base.metadata.create_all(engine)
        
        # 2. Add new columns to existing tables
        print("Adding new columns...")
        conn.execute(text("""
            ALTER TABLE articles 
            ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES categories(id);
        """))
        
        conn.execute(text("""
            ALTER TABLE summaries
            ADD COLUMN IF NOT EXISTS prelims_relevance TEXT,
            ADD COLUMN IF NOT EXISTS mains_relevance TEXT,
            ADD COLUMN IF NOT EXISTS possible_questions JSONB DEFAULT '[]',
            ADD COLUMN IF NOT EXISTS key_facts JSONB DEFAULT '[]';
        """))
        
        # 3. Create indexes
        print("Creating indexes...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_articles_published_at 
            ON articles(published_at);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_articles_category_id 
            ON articles(category_id);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_rankings_score 
            ON rankings(score);
        """))
        
        # 4. Insert default categories
        print("Inserting default categories...")
        categories = [
            ("Polity", "Indian Polity and Governance", 1),
            ("Economy", "Indian Economy and Economic Development", 2),
            ("International Relations", "International Relations and Organizations", 3),
            ("Science & Tech", "Science and Technology", 4),
            ("Environment & Ecology", "Environment and Ecology", 5),
            ("Defence & Security", "Defence and Security", 6),
            ("Government Schemes", "Government Schemes and Policies", 7),
            ("Social Issues", "Social Issues and Development", 8),
        ]
        
        for name, description, priority in categories:
            conn.execute(text("""
                INSERT INTO categories (name, description, priority_order, created_at, updated_at)
                VALUES (:name, :description, :priority, NOW(), NOW())
                ON CONFLICT (name) DO NOTHING;
            """), {"name": name, "description": description, "priority": priority})
        
        # 5. Insert default sources
        print("Inserting default sources...")
        sources = [
            ("YouTube Exam Channels", "youtube", "https://www.youtube.com"),
            ("Press Information Bureau", "pib", "https://pib.gov.in"),
            ("Government Schemes", "government_scheme", "https://www.india.gov.in"),
        ]
        
        for name, source_type, base_url in sources:
            conn.execute(text("""
                INSERT INTO sources (name, source_type, base_url, is_active, created_at, updated_at)
                VALUES (:name, :type, :url, TRUE, NOW(), NOW())
                ON CONFLICT (name) DO NOTHING;
            """), {"name": name, "type": source_type, "url": base_url})
        
        print("Migration completed successfully!")


def downgrade():
    """Rollback migration."""
    config = get_config()
    engine = create_engine(config.DATABASE_URL)
    
    with engine.begin() as conn:
        print("Rolling back migration...")
        
        # Drop new columns
        conn.execute(text("""
            ALTER TABLE articles DROP COLUMN IF EXISTS category_id;
        """))
        
        conn.execute(text("""
            ALTER TABLE summaries
            DROP COLUMN IF EXISTS prelims_relevance,
            DROP COLUMN IF EXISTS mains_relevance,
            DROP COLUMN IF EXISTS possible_questions,
            DROP COLUMN IF EXISTS key_facts;
        """))
        
        # Drop new tables
        conn.execute(text("DROP TABLE IF EXISTS rankings CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS user_profiles CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS categories CASCADE;"))
        
        print("Rollback completed!")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python 001_transform_to_exam_system.py [upgrade|downgrade]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'upgrade':
        upgrade()
    elif command == 'downgrade':
        downgrade()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
```

### Monitoring and Observability

**Logging Configuration**:

```python
import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = 'INFO'):
    """
    Setup structured logging for production.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Console handler with JSON formatting
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        timestamp=True
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

**Performance Monitoring**:

```python
import time
from functools import wraps
from typing import Callable


def monitor_performance(func: Callable) -> Callable:
    """
    Decorator to monitor function performance.
    
    Logs execution time and any errors.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(func.__module__)
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function {func.__name__} completed",
                extra={
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'status': 'success'
                }
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(
                f"Function {func.__name__} failed",
                extra={
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'status': 'error',
                    'error': str(e)
                }
            )
            
            raise
    
    return wrapper
```

### Health Checks

```python
from typing import Dict, Any


def health_check() -> Dict[str, Any]:
    """
    Perform system health check.
    
    Returns:
        Dictionary with health status
    """
    health = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Check database connection
    try:
        config = get_config()
        engine = create_engine(config.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health['checks']['database'] = 'ok'
    except Exception as e:
        health['checks']['database'] = f'error: {str(e)}'
        health['status'] = 'unhealthy'
    
    # Check Gemini API
    try:
        config = get_config()
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        model.generate_content("Test")
        health['checks']['gemini_api'] = 'ok'
    except Exception as e:
        health['checks']['gemini_api'] = f'error: {str(e)}'
        health['status'] = 'unhealthy'
    
    # Check disk space
    import shutil
    total, used, free = shutil.disk_usage("/")
    free_percent = (free / total) * 100
    
    if free_percent < 10:
        health['checks']['disk_space'] = f'warning: {free_percent:.1f}% free'
        health['status'] = 'degraded'
    else:
        health['checks']['disk_space'] = f'ok: {free_percent:.1f}% free'
    
    return health
```


## Implementation Roadmap

### Phase 1: Foundation (Week 1)

**Objective**: Establish core abstractions and infrastructure

**Tasks**:
1. Create abstract base classes (AbstractScraper, AbstractAgent, AbstractRankingStrategy)
2. Implement database models with SQLAlchemy
3. Set up configuration management with Pydantic
4. Create base repository with session management
5. Write unit tests for base classes

**Deliverables**:
- Abstract base classes with docstrings
- Database schema with migrations
- Configuration validation
- Base repository implementation
- Test suite for foundation

### Phase 2: Scrapers (Week 2)

**Objective**: Implement content scrapers

**Tasks**:
1. Implement YouTubeScraper with 11 exam channels
2. Implement PIBScraper with category filtering
3. Implement GovernmentSchemesScraper
4. Implement ScraperFactory with registry pattern
5. Write property tests for scraper output validation

**Deliverables**:
- Three concrete scraper implementations
- Factory pattern implementation
- Property tests for scrapers
- Integration tests with real sources (mocked)

### Phase 3: Agents (Week 3)

**Objective**: Implement AI-powered agents

**Tasks**:
1. Implement CategorizationAgent with 8 categories
2. Implement SummarizationAgent with exam focus
3. Implement RankingAgent with strategy injection
4. Implement DigestAgent for output formatting
5. Write property tests for agent outputs

**Deliverables**:
- Four concrete agent implementations
- Gemini API integration
- Property tests for agents
- Unit tests for edge cases

### Phase 4: Ranking Strategies (Week 4)

**Objective**: Implement exam-specific ranking

**Tasks**:
1. Implement UPSCRankingStrategy
2. Implement SSCRankingStrategy
3. Implement BankingRankingStrategy
4. Write property tests for score bounds
5. Tune ranking weights based on testing

**Deliverables**:
- Three ranking strategy implementations
- Property tests for strategies
- Weight tuning documentation

### Phase 5: Repositories and Services (Week 5)

**Objective**: Implement data access and business logic

**Tasks**:
1. Implement all repository classes (Article, Summary, Ranking, Category, Source)
2. Implement all service classes (Scraping, Categorization, Summarization, Ranking)
3. Write property tests for session management
4. Write integration tests for services
5. Implement bulk operations for performance

**Deliverables**:
- Five repository implementations
- Four service implementations
- Property tests for repositories
- Integration tests for services

### Phase 6: Pipeline and CLI (Week 6)

**Objective**: Implement pipeline orchestration

**Tasks**:
1. Implement Pipeline class with stage execution
2. Implement CLI with argument parsing
3. Implement logging and monitoring
4. Write property tests for pipeline execution
5. Write integration tests for full pipeline

**Deliverables**:
- Pipeline orchestrator
- CLI interface
- Logging infrastructure
- Property tests for pipeline
- End-to-end integration tests

### Phase 7: Testing and Documentation (Week 7)

**Objective**: Comprehensive testing and documentation

**Tasks**:
1. Achieve 80% code coverage with unit tests
2. Implement all 16 property tests
3. Write integration tests for all components
4. Generate UML diagrams
5. Write project report

**Deliverables**:
- Complete test suite (unit + property + integration)
- UML class diagram
- UML component diagram
- Project report (2-3 pages)
- README with usage examples

### Phase 8: Deployment and Production (Week 8)

**Objective**: Deploy to production

**Tasks**:
1. Run database migration on production
2. Deploy to Render with Docker
3. Set up cron job for daily execution
4. Configure monitoring and alerts
5. Perform load testing

**Deliverables**:
- Production deployment on Render
- Daily cron job configured
- Monitoring dashboard
- Load test results
- Deployment documentation


## Academic Project Report Template

### Title Page

```
AI-Powered Competitive Exam News Intelligence System
A Transformation Project Demonstrating OOP Principles and Design Patterns

Student Name: [Your Name]
Course: [Course Name]
Institution: [Institution Name]
Date: [Date]
```

### 1. Introduction (1/2 page)

**Project Overview**:
This project transforms an existing AI News Aggregator into a Competitive Exam News Intelligence System for Indian competitive exam aspirants (UPSC, SSC, Banking). The system aggregates content from exam-relevant sources (YouTube channels, PIB, government schemes), processes it using Google Gemini AI, and generates personalized exam-focused digests.

**Objectives**:
- Demonstrate strong Object-Oriented Programming (OOP) principles
- Implement industry-standard design patterns
- Build a production-ready system with proper architecture
- Maintain existing infrastructure (PostgreSQL, Docker, Render)

**Technologies Used**:
- Python 3.11 with type hints
- Google Gemini 1.5 Flash API for AI processing
- PostgreSQL with SQLAlchemy ORM
- Docker for containerization
- Render for cloud deployment

### 2. System Architecture (1/2 page)

**Layered Architecture**:

The system follows a 5-layer architecture:

1. **Presentation Layer**: CLI interface for pipeline execution
2. **Service Layer**: Business logic orchestration (ScrapingService, CategorizationService, etc.)
3. **Business Logic Layer**: Core components (Scrapers, Agents, Strategies)
4. **Data Access Layer**: Repository pattern for database operations
5. **Data Storage Layer**: PostgreSQL database

**Pipeline Flow**:
```
Scrape → Categorize → Summarize → Rank → Store → Generate Digest
```

Each stage processes articles sequentially, with error handling ensuring pipeline resilience.

**Component Diagram**: [Include Mermaid diagram from design document]

### 3. OOP Principles Implementation (1 page)

#### 3.1 Encapsulation

**Definition**: Hiding internal state and requiring interaction through methods.

**Implementation**:
```python
class AbstractScraper(ABC):
    def __init__(self, source_name: str, base_url: str, timeout: int = 30):
        self._source_name = source_name  # Private attribute
        self._base_url = base_url        # Private attribute
        self._timeout = timeout          # Private attribute
    
    @property
    def source_name(self) -> str:
        """Controlled read access to private attribute."""
        return self._source_name
```

**Benefits**: Prevents external code from directly modifying internal state, ensuring data integrity.

#### 3.2 Abstraction

**Definition**: Hiding complex implementation details behind simple interfaces.

**Implementation**:
```python
class AbstractAgent(ABC):
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Abstract method that all agents must implement."""
        pass
```

**Benefits**: Allows different agent implementations (Categorization, Summarization, Ranking) to be used interchangeably.

#### 3.3 Inheritance

**Definition**: Creating new classes based on existing classes.

**Implementation**:
```python
class YouTubeScraper(AbstractScraper):
    """Inherits common scraper behavior from AbstractScraper."""
    
    def scrape(self, hours: int) -> List[ScrapedContent]:
        """Implements abstract scrape() method."""
        # YouTube-specific implementation
```

**Benefits**: Code reuse (common error handling, validation) and consistent interface across all scrapers.

#### 3.4 Polymorphism

**Definition**: Objects of different types can be accessed through the same interface.

**Implementation**:
```python
def process_with_scraper(scraper: AbstractScraper, hours: int):
    """Works with any scraper type (YouTube, PIB, GovSchemes)."""
    results = scraper.scrape(hours)  # Polymorphic call
    return results
```

**Benefits**: Enables flexible, extensible code where new scraper types can be added without modifying existing code.

#### 3.5 SOLID Principles

**Single Responsibility Principle**: Each class has one reason to change
- Example: YouTubeScraper only handles YouTube scraping, not categorization or storage

**Open/Closed Principle**: Open for extension, closed for modification
- Example: New ranking strategies can be added without modifying RankingAgent

**Liskov Substitution Principle**: Subclasses are substitutable for base classes
- Example: Any AbstractScraper subclass can be used wherever AbstractScraper is expected

**Interface Segregation Principle**: No client depends on unused methods
- Example: AbstractScraper only defines scraping interface, not unrelated methods

**Dependency Inversion Principle**: Depend on abstractions, not concretions
- Example: Services depend on repository interfaces, not concrete implementations

### 4. Design Patterns Implementation (1 page)

#### 4.1 Factory Pattern

**Purpose**: Centralize object creation logic.

**Implementation**:
```python
class ScraperFactory:
    _registry: Dict[SourceType, Type[AbstractScraper]] = {}
    
    @classmethod
    def create_scraper(cls, source_type: SourceType) -> AbstractScraper:
        """Create scraper instance based on type."""
        scraper_class = cls._registry[source_type]
        return scraper_class()
```

**Benefits**: 
- Decouples scraper creation from usage
- Enables runtime scraper selection
- Simplifies adding new scraper types

#### 4.2 Strategy Pattern

**Purpose**: Enable interchangeable algorithms.

**Implementation**:
```python
class RankingAgent(AbstractAgent):
    def __init__(self, config: AgentConfig, strategy: AbstractRankingStrategy):
        self._strategy = strategy  # Strategy injection
    
    def execute(self, content: ScrapedContent, metadata: ArticleMetadata):
        return self._strategy.calculate_score(content.content, metadata)
```

**Benefits**:
- Different ranking algorithms for different exam types (UPSC, SSC, Banking)
- Runtime strategy switching
- Easy to add new ranking algorithms

#### 4.3 Repository Pattern

**Purpose**: Abstract data access logic.

**Implementation**:
```python
class ArticleRepository(BaseRepository[Article]):
    def find_by_date_range(self, start: datetime, end: datetime) -> List[Article]:
        """Query articles by date range."""
        with self._get_session() as session:
            return session.query(Article).filter(
                Article.published_at >= start,
                Article.published_at <= end
            ).all()
```

**Benefits**:
- Decouples business logic from database details
- Enables easy database switching
- Centralizes query logic

#### 4.4 Service Layer Pattern

**Purpose**: Orchestrate business logic.

**Implementation**:
```python
class ScrapingService:
    def __init__(self, scraper_factory, article_repo, source_repo):
        self._scraper_factory = scraper_factory
        self._article_repo = article_repo
        self._source_repo = source_repo
    
    def scrape_all_sources(self, hours: int) -> Dict[str, int]:
        """Orchestrate scraping across all sources."""
        # Coordinates scrapers and repositories
```

**Benefits**:
- Clear separation of concerns
- Testable business logic
- Reusable workflows

#### 4.5 Singleton Pattern

**Purpose**: Ensure single instance of configuration.

**Implementation**:
```python
_config: Optional[Config] = None

def get_config() -> Config:
    """Get configuration singleton."""
    global _config
    if _config is None:
        _config = Config()
    return _config
```

**Benefits**:
- Single source of truth for configuration
- Prevents multiple config loads
- Thread-safe access

### 5. Database Design (1/2 page)

**Entity Relationship Diagram**: [Include ERD from design document]

**Key Tables**:
- **articles**: Stores scraped content
- **summaries**: AI-generated exam-focused summaries
- **rankings**: Relevance scores for articles
- **categories**: Exam-relevant categories (8 categories)
- **sources**: Content sources (YouTube, PIB, etc.)
- **user_profiles**: User preferences for personalization

**Relationships**:
- One-to-one: Article ↔ Summary, Article ↔ Ranking
- Many-to-one: Article → Category, Article → Source
- Foreign key constraints ensure referential integrity

**Indexes**:
- `idx_articles_published_at`: Fast date range queries
- `idx_rankings_score`: Fast top-N queries
- `idx_articles_category_id`: Fast category filtering

### 6. Challenges and Solutions (1/2 page)

**Challenge 1: Handling Missing YouTube Transcripts**
- **Problem**: Not all videos have transcripts available
- **Solution**: Graceful error handling returns None, pipeline continues with available content

**Challenge 2: Gemini API Rate Limits**
- **Problem**: Free tier has 15 requests/minute limit
- **Solution**: Batch processing with delays, exponential backoff on rate limit errors

**Challenge 3: Database Session Management**
- **Problem**: Connection leaks can exhaust database pool
- **Solution**: Context manager pattern ensures sessions are always closed

**Challenge 4: Maintaining Production Infrastructure**
- **Problem**: Must not break existing Docker/Render deployment
- **Solution**: Incremental migration with backward compatibility, database migration scripts

### 7. Conclusion (1/4 page)

This project successfully demonstrates strong OOP principles and design patterns in a production-ready system. The transformation from AI News Aggregator to Competitive Exam Intelligence System showcases:

- **Solid Architecture**: Layered design with clear separation of concerns
- **OOP Excellence**: Proper use of encapsulation, abstraction, inheritance, and polymorphism
- **Design Patterns**: Factory, Strategy, Repository, Service Layer, and Singleton patterns
- **Production Readiness**: Docker deployment, database migrations, error handling, logging
- **Testability**: Property-based testing ensures correctness across all inputs

The system is deployed on Render's free tier, processing exam-relevant content daily for competitive exam aspirants. Future enhancements could include web UI, multi-user support, and additional exam types.

### 8. References

1. Martin, R. C. (2017). Clean Architecture: A Craftsman's Guide to Software Structure and Design
2. Gamma, E., et al. (1994). Design Patterns: Elements of Reusable Object-Oriented Software
3. Fowler, M. (2002). Patterns of Enterprise Application Architecture
4. Google Gemini API Documentation: https://ai.google.dev/docs
5. SQLAlchemy Documentation: https://docs.sqlalchemy.org/


## Conclusion

This design document provides a comprehensive blueprint for transforming the AI News Aggregator into a Competitive Exam Intelligence System. The design emphasizes:

**Academic Excellence**:
- Clear demonstration of all OOP principles (Encapsulation, Abstraction, Inheritance, Polymorphism)
- Implementation of SOLID principles throughout the architecture
- Five design patterns (Factory, Strategy, Repository, Service Layer, Singleton) with clear rationale
- Comprehensive type hints and Google-style docstrings
- UML diagrams for visual documentation

**Production Readiness**:
- Maintains existing infrastructure (Gemini API, PostgreSQL, Docker, Render)
- Robust error handling at all layers
- Comprehensive logging and monitoring
- Database migrations for safe transformation
- Health checks and performance monitoring

**Correctness and Testing**:
- 16 correctness properties derived from requirements
- Property-based testing with hypothesis library (100 iterations minimum)
- Unit tests for specific examples and edge cases
- Integration tests for end-to-end workflows
- Target: 80% code coverage

**Extensibility**:
- Abstract base classes enable easy addition of new scrapers, agents, and strategies
- Factory pattern allows runtime component selection
- Strategy pattern enables exam-specific customization
- Repository pattern abstracts database details
- Configuration-driven behavior

**Key Design Decisions**:

1. **Layered Architecture**: Clear separation between presentation, service, business logic, data access, and storage layers
2. **Dependency Injection**: Services receive dependencies via constructor, enabling testability and flexibility
3. **Pydantic Models**: Type-safe data validation throughout the system
4. **Context Managers**: Automatic resource management for database sessions
5. **Structured Logging**: JSON-formatted logs for production observability

**Implementation Path**:

The 8-week implementation roadmap provides a clear path from foundation to production deployment:
- Weeks 1-2: Foundation and scrapers
- Weeks 3-4: Agents and strategies
- Weeks 5-6: Repositories, services, and pipeline
- Weeks 7-8: Testing, documentation, and deployment

**Academic Value**:

This project serves as an excellent demonstration of:
- Software architecture principles
- Object-oriented design
- Design pattern application
- Production system development
- Testing strategies (unit + property-based)

The included project report template provides a structure for documenting the work for academic submission, with clear explanations of how each OOP principle and design pattern is implemented.

**Next Steps**:

1. Review and approve this design document
2. Begin Phase 1 implementation (Foundation)
3. Iterate on design based on implementation learnings
4. Maintain documentation as code evolves
5. Deploy to production and monitor performance

This design provides a solid foundation for building a production-ready, academically rigorous system that demonstrates strong software engineering principles while solving a real-world problem for competitive exam aspirants.

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**Status**: Ready for Review

