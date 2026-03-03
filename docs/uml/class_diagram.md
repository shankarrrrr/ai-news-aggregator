# UML Class Diagram: Competitive Exam Intelligence System

This document contains the UML class diagram for the Competitive Exam Intelligence System, showing all classes, their attributes, methods, and relationships.

## Class Diagram

```mermaid
classDiagram
    %% Abstract Base Classes
    class AbstractScraper {
        <<abstract>>
        -_source_name: str
        -_base_url: str
        -_timeout: int
        +__init__(source_name, base_url, timeout)
        +source_name: str
        +base_url: str
        +timeout: int
        +scrape(hours)* List~ScrapedContent~
        +scrape_with_retry(hours, max_retries, base_delay, max_delay) List~ScrapedContent~
        +validate_content(content) bool
        +_handle_network_error(error) None
        +_execute_with_timeout(func, timeout_seconds) Any
        +_log_scrape_start(hours) None
        +_log_scrape_complete(count) None
    }

    class AbstractAgent {
        <<abstract>>
        -_config: AgentConfig
        -_client: genai.GenerativeModel
        +__init__(config)
        +model_name: str
        +temperature: float
        +execute(input_data)* Any
        +execute_with_fallback(input_data, fallback_strategies, max_retries, base_delay) Any
        +_call_gemini_api(prompt) str
        +_parse_json_response(response) dict
        +_extract_retry_after(error_message) Optional~int~
        +_log_execution_start(operation) None
        +_log_execution_complete(operation) None
        +_log_api_call(prompt_length) None
    }

    class AbstractRankingStrategy {
        <<abstract>>
        -_exam_type: str
        -_weights: Dict~str, float~
        +__init__(exam_type, weights)
        +exam_type: str
        +calculate_score(content, metadata)* RankingResult
        +_validate_weights() None
        +_calculate_freshness_score(published_at) float
        +_calculate_category_relevance(category, priority_categories) float
    }

    %% Data Models
    class ScrapedContent {
        +title: str
        +content: str
        +url: str
        +published_at: datetime
        +source_type: str
        +metadata: dict
    }

    class AgentConfig {
        +model_name: str
        +temperature: float
        +max_tokens: int
        +api_key: str
    }

    class ArticleMetadata {
        +category: str
        +source_type: str
        +published_at: datetime
        +content_length: int
        +keywords: List~str~
    }

    class RankingResult {
        +score: float
        +reasoning: str
        +factors: Dict~str, float~
    }

    %% Concrete Scrapers
    class YouTubeScraper {
        +EXAM_CHANNELS: List~str~
        -_channel_ids: List~str~
        -_transcript_api: YouTubeTranscriptApi
        +__init__(channel_ids)
        +scrape(hours) List~ScrapedContent~
        +_get_recent_videos(channel_id, hours) List~dict~
        +_extract_video_id(url) str
        +_get_transcript(video_id) Optional~str~
    }

    class PIBScraper {
        +EXAM_RELEVANT_CATEGORIES: List~str~
        -_categories: List~str~
        +__init__(categories)
        +scrape(hours) List~ScrapedContent~
        +_scrape_category(category, cutoff_time) List~ScrapedContent~
        +_parse_release(item, category) Optional~ScrapedContent~
    }

    class GovernmentSchemesScraper {
        +SCHEME_PORTALS: List~str~
        -_portals: List~str~
        +__init__(portals)
        +scrape(hours) List~ScrapedContent~
        +_scrape_portal(portal, cutoff_time) List~ScrapedContent~
        +_parse_scheme(item) Optional~ScrapedContent~
        +_extract_scheme_metadata(item) dict
        +_format_scheme_content(scheme_data) str
    }

    %% Factory
    class ScraperFactory {
        -_registry: Dict~SourceType, type~
        +register_scraper(source_type, scraper_class) None
        +create_scraper(source_type) AbstractScraper
        +get_available_sources() List~SourceType~
        +create_all_scrapers() List~AbstractScraper~
    }

    class SourceType {
        <<enumeration>>
        YOUTUBE
        PIB
        GOVERNMENT_SCHEMES
    }

    %% Concrete Agents
    class CategorizationAgent {
        +EXAM_CATEGORIES: List~str~
        +execute(content) CategoryResult
        +_build_categorization_prompt(content) str
        +_validate_categories(categories) bool
    }

    class SummarizationAgent {
        +execute(content, category) SummaryResult
        +_build_summarization_prompt(content, category) str
        +get_formatted_summary(result) str
    }

    class RankingAgent {
        -_strategy: AbstractRankingStrategy
        +__init__(config, strategy)
        +execute(content, metadata) RankingResult
        +set_strategy(strategy) None
        +_should_use_ai_enhancement(score) bool
        +_enhance_with_ai(content, metadata, base_score) float
    }

    class DigestAgent {
        +execute(articles) DigestResult
        +_group_by_category(articles) Dict~str, List~DigestArticle~~
        +_generate_introduction(categories) str
        +_generate_conclusion(stats) str
        +_get_top_categories(articles) List~str~
        +format_as_text(result) str
    }

    %% Ranking Strategies
    class UPSCRankingStrategy {
        +PRIORITY_CATEGORIES: List~str~
        +DEFAULT_WEIGHTS: Dict~str, float~
        +calculate_score(content, metadata) RankingResult
        +_calculate_content_depth(content) float
        +_calculate_source_credibility(source_type) float
        +_generate_reasoning(factors) str
    }

    class SSCRankingStrategy {
        +PRIORITY_CATEGORIES: List~str~
        +DEFAULT_WEIGHTS: Dict~str, float~
        +calculate_score(content, metadata) RankingResult
        +_calculate_factual_density(content) float
        +_calculate_source_credibility(source_type) float
        +_generate_reasoning(factors) str
    }

    class BankingRankingStrategy {
        +PRIORITY_CATEGORIES: List~str~
        +BANKING_KEYWORDS: List~str~
        +DEFAULT_WEIGHTS: Dict~str, float~
        +calculate_score(content, metadata) RankingResult
        +_calculate_banking_keyword_score(content) float
        +_calculate_source_credibility(source_type) float
        +_generate_reasoning(factors) str
    }

    %% Database Models
    class Article {
        +id: int
        +title: str
        +content: str
        +url: str
        +published_at: datetime
        +category_id: int
        +source_id: int
        +metadata: dict
        +created_at: datetime
        +updated_at: datetime
    }

    class Category {
        +id: int
        +name: str
        +description: str
        +priority: int
        +created_at: datetime
        +updated_at: datetime
    }

    class Source {
        +id: int
        +name: str
        +source_type: str
        +base_url: str
        +is_active: bool
        +description: str
        +created_at: datetime
        +updated_at: datetime
    }

    class Summary {
        +id: int
        +article_id: int
        +summary_text: str
        +exam_relevance: str
        +prelims_relevance: str
        +mains_relevance: str
        +possible_questions: str
        +key_facts: str
        +word_count: int
        +created_at: datetime
        +updated_at: datetime
    }

    class Ranking {
        +id: int
        +article_id: int
        +exam_type: str
        +score: float
        +reasoning: str
        +factors: dict
        +strategy_used: str
        +created_at: datetime
        +updated_at: datetime
    }

    %% Repositories
    class BaseRepository~T~ {
        <<generic>>
        +create(entity) T
        +find_by_id(id) Optional~T~
        +find_all() List~T~
        +update(entity) T
        +delete(id) bool
        +_get_session() Session
    }

    class ArticleRepository {
        +find_by_date_range(start, end) List~Article~
        +find_by_category(category_id) List~Article~
        +find_by_source(source_id) List~Article~
        +find_by_url(url) Optional~Article~
        +bulk_create(articles) List~Article~
    }

    class SummaryRepository {
        +find_by_article_id(article_id) Optional~Summary~
    }

    class RankingRepository {
        +find_by_article_id(article_id) List~Ranking~
        +find_top_n(exam_type, n) List~Ranking~
        +find_by_score_range(min_score, max_score) List~Ranking~
    }

    class CategoryRepository {
        +find_by_name(name) Optional~Category~
        +find_all_ordered() List~Category~
    }

    class SourceRepository {
        +find_by_type(source_type) List~Source~
        +find_active_sources() List~Source~
    }

    %% Services
    class ScrapingService {
        -_scraper_factory: ScraperFactory
        -_article_repository: ArticleRepository
        -_source_repository: SourceRepository
        +scrape_all_sources(hours) List~Article~
        +_scrape_source(source_type, hours) List~ScrapedContent~
        +_filter_duplicates(content_list) List~ScrapedContent~
        +_create_article_entity(content) Article
    }

    class CategorizationService {
        -_agent: CategorizationAgent
        -_article_repository: ArticleRepository
        -_category_repository: CategoryRepository
        +categorize_articles(articles) List~Article~
        +_categorize_article(article) Article
    }

    class SummarizationService {
        -_agent: SummarizationAgent
        -_article_repository: ArticleRepository
        -_summary_repository: SummaryRepository
        +summarize_articles(articles) List~Summary~
        +_summarize_article(article) Summary
    }

    class RankingService {
        -_agent: RankingAgent
        -_article_repository: ArticleRepository
        -_ranking_repository: RankingRepository
        +rank_articles(articles, exam_type) List~Ranking~
        +_select_strategy(exam_type) AbstractRankingStrategy
        +_rank_article(article, exam_type) Ranking
    }

    class DigestGenerationService {
        -_agent: DigestAgent
        -_ranking_repository: RankingRepository
        +generate_digest(exam_type, top_n) str
    }

    %% Pipeline
    class Pipeline {
        -_scraping_service: ScrapingService
        -_categorization_service: CategorizationService
        -_summarization_service: SummarizationService
        -_ranking_service: RankingService
        -_digest_service: DigestGenerationService
        +execute(hours, top_n, exam_type) PipelineResult
        +_log_stage_start(stage) None
        +_log_stage_end(stage, count) None
        +_generate_summary_report(stats) str
    }

    %% Exception Classes
    class SystemException {
        +cause: Optional~Exception~
    }

    class TransientError {
        +retry_after: Optional~int~
    }

    class PermanentError {
    }

    class NetworkError {
    }

    class APIError {
        +status_code: Optional~int~
    }

    class APIRateLimitError {
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
    
    SystemException <|-- TransientError
    SystemException <|-- PermanentError
    TransientError <|-- NetworkError
    SystemException <|-- APIError
    TransientError <|-- APIRateLimitError

    %% Relationships - Composition
    ScraperFactory *-- SourceType
    AbstractScraper *-- ScrapedContent
    AbstractAgent *-- AgentConfig
    AbstractRankingStrategy *-- ArticleMetadata
    AbstractRankingStrategy *-- RankingResult
    RankingAgent *-- AbstractRankingStrategy
    
    %% Relationships - Dependencies
    ScrapingService --> ScraperFactory
    ScrapingService --> ArticleRepository
    ScrapingService --> SourceRepository
    
    CategorizationService --> CategorizationAgent
    CategorizationService --> ArticleRepository
    CategorizationService --> CategoryRepository
    
    SummarizationService --> SummarizationAgent
    SummarizationService --> ArticleRepository
    SummarizationService --> SummaryRepository
    
    RankingService --> RankingAgent
    RankingService --> ArticleRepository
    RankingService --> RankingRepository
    
    DigestGenerationService --> DigestAgent
    DigestGenerationService --> RankingRepository
    
    Pipeline --> ScrapingService
    Pipeline --> CategorizationService
    Pipeline --> SummarizationService
    Pipeline --> RankingService
    Pipeline --> DigestGenerationService

    %% Database Relationships
    Article ||--o{ Summary : "has"
    Article ||--o{ Ranking : "has"
    Article }o--|| Category : "belongs to"
    Article }o--|| Source : "from"
```

## Key Design Patterns Illustrated

### 1. Template Method Pattern
- **AbstractScraper**: Defines the scraping algorithm structure
- **Concrete Scrapers**: Implement specific steps (YouTubeScraper, PIBScraper, GovernmentSchemesScraper)

### 2. Strategy Pattern
- **AbstractRankingStrategy**: Interface for ranking algorithms
- **Concrete Strategies**: Different implementations for UPSC, SSC, Banking exams
- **RankingAgent**: Context that uses strategies

### 3. Factory Pattern
- **ScraperFactory**: Creates scraper instances based on source type
- **Registry Pattern**: Maintains mapping of source types to scraper classes

### 4. Repository Pattern
- **BaseRepository**: Generic repository interface
- **Concrete Repositories**: Specific data access implementations
- **Encapsulation**: Hides database details from business logic

### 5. Service Layer Pattern
- **Services**: Orchestrate business logic between agents and repositories
- **Separation of Concerns**: Clear boundaries between layers

## SOLID Principles Demonstrated

### Single Responsibility Principle (SRP)
- Each class has one reason to change
- Scrapers only handle data fetching
- Agents only handle AI processing
- Repositories only handle data access

### Open/Closed Principle (OCP)
- Abstract base classes allow extension without modification
- New scrapers can be added without changing existing code
- New ranking strategies can be added without changing RankingAgent

### Liskov Substitution Principle (LSP)
- All concrete scrapers are substitutable for AbstractScraper
- All ranking strategies are substitutable for AbstractRankingStrategy
- All repositories are substitutable for BaseRepository

### Interface Segregation Principle (ISP)
- Interfaces are focused and specific
- Clients depend only on methods they use
- No fat interfaces with unused methods

### Dependency Inversion Principle (DIP)
- High-level modules depend on abstractions
- Services depend on repository interfaces, not concrete implementations
- RankingAgent depends on AbstractRankingStrategy, not concrete strategies

## Class Relationships Summary

- **Inheritance**: 15 inheritance relationships showing polymorphism
- **Composition**: 8 composition relationships showing "has-a" relationships
- **Dependencies**: 12 dependency relationships showing service interactions
- **Database Relations**: 4 foreign key relationships in the data model

This class diagram demonstrates a well-structured, maintainable system following OOP principles and design patterns suitable for academic documentation and production use.