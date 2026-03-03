 # Requirements Document

## Introduction

This document specifies the requirements for transforming the existing "AI News Aggregator - Gemini Powered" production system into an "AI-Powered Competitive Exam News Intelligence System". The system will aggregate, categorize, summarize, and rank news content specifically relevant to competitive exam aspirants (UPSC, MPSC, SSC, Banking, NDA/CDS, State PSC) in India. The transformation must maintain all existing production infrastructure (Google Gemini 1.5 Flash API, PostgreSQL, Docker, Render deployment) while implementing strong OOP principles and design patterns for academic requirements.

## Glossary

- **System**: The AI-Powered Competitive Exam News Intelligence System
- **Scraper**: A component that fetches content from external sources (YouTube, PIB, government websites)
- **AbstractScraper**: Base class defining the interface for all scraper implementations
- **PIB**: Press Information Bureau - official government news agency
- **Repository**: Data access layer implementing the Repository Pattern for database operations
- **Agent**: An AI-powered component that processes content (categorization, summarization, ranking)
- **AbstractAgent**: Base class defining the interface for all agent implementations
- **Digest**: A processed article with AI-generated summary and metadata
- **RankingStrategy**: Algorithm for scoring and ranking articles by exam relevance
- **AbstractRankingStrategy**: Base class defining the interface for ranking algorithms
- **Pipeline**: The orchestrated workflow: Scrape → Categorize → Summarize → Rank → Store → Generate Digest
- **ORM**: Object-Relational Mapping - SQLAlchemy models for database entities
- **UPSC**: Union Public Service Commission - India's premier civil services examination
- **Prelims**: Preliminary examination (objective type)
- **Mains**: Main examination (descriptive type)
- **Current_Affairs**: Recent events and developments relevant to exam preparation
- **Exam_Category**: Classification of content (Polity, Economy, International Relations, Science & Tech, Environment & Ecology, Defence & Security, Government Schemes, Social Issues)
- **CLI**: Command Line Interface for running the pipeline
- **Factory_Pattern**: Design pattern for creating scraper instances
- **Strategy_Pattern**: Design pattern for interchangeable ranking algorithms
- **Service_Layer**: Business logic layer coordinating between agents and repositories

## Requirements

### Requirement 1: Domain Transformation from AI News to Competitive Exam Intelligence

**User Story:** As a competitive exam aspirant, I want the system to aggregate exam-relevant news instead of AI news, so that I can stay updated with current affairs important for my preparation.

#### Acceptance Criteria

1. THE System SHALL replace AI news sources with competitive exam-relevant sources (PIB, government schemes, UPSC-relevant editorials, exam preparation YouTube channels)
2. THE System SHALL maintain the existing Google Gemini 1.5 Flash API integration for all AI processing
3. THE System SHALL maintain the existing PostgreSQL database with SQLAlchemy ORM
4. THE System SHALL maintain Docker compatibility and Render deployment configuration
5. THE System SHALL maintain the CLI-based pipeline execution interface

### Requirement 2: YouTube Channel Scraping for Exam Content

**User Story:** As a competitive exam aspirant, I want the system to scrape transcripts from exam preparation YouTube channels, so that I can access video content in text format.

#### Acceptance Criteria

1. THE YouTubeScraper SHALL inherit from AbstractScraper
2. THE YouTubeScraper SHALL scrape transcripts from the following channels: StudyIQ IAS, Drishti IAS, Vision IAS, OnlyIAS, Insights IAS, PIB India Official, Sansad TV, Vajiram & Ravi, Adda247, BYJU'S Exam Prep, Unacademy UPSC
3. WHEN a video has no transcript available, THE YouTubeScraper SHALL mark it as unavailable and skip processing
4. THE YouTubeScraper SHALL store video metadata (title, URL, channel_id, published_at, description) in the database
5. THE YouTubeScraper SHALL implement the scrape() method defined in AbstractScraper
6. THE YouTubeScraper SHALL use private attributes for internal state with controlled access methods

### Requirement 3: PIB (Press Information Bureau) Content Scraping

**User Story:** As a UPSC aspirant, I want the system to scrape official government press releases from PIB, so that I can access authentic government information for exam preparation.

#### Acceptance Criteria

1. THE PIBScraper SHALL inherit from AbstractScraper
2. THE PIBScraper SHALL scrape press releases from the PIB website (https://pib.gov.in)
3. WHEN scraping PIB content, THE PIBScraper SHALL extract title, content, publication date, category, and URL
4. THE PIBScraper SHALL filter content published within the specified time window (configurable hours)
5. THE PIBScraper SHALL implement the scrape() method defined in AbstractScraper
6. THE PIBScraper SHALL handle network errors gracefully and log failures

### Requirement 4: Government Schemes Content Scraping

**User Story:** As a competitive exam aspirant, I want the system to aggregate information about government schemes, so that I can prepare for questions on welfare programs and policies.

#### Acceptance Criteria

1. THE GovernmentSchemesScraper SHALL inherit from AbstractScraper
2. THE GovernmentSchemesScraper SHALL scrape scheme information from official government portals
3. WHEN scraping scheme data, THE GovernmentSchemesScraper SHALL extract scheme name, ministry, objectives, beneficiaries, and launch date
4. THE GovernmentSchemesScraper SHALL implement the scrape() method defined in AbstractScraper
5. THE GovernmentSchemesScraper SHALL store scheme data in a structured format in the database

### Requirement 5: Abstract Scraper Base Class

**User Story:** As a system architect, I want a common interface for all scrapers, so that new sources can be added without modifying existing code (Open/Closed Principle).

#### Acceptance Criteria

1. THE AbstractScraper SHALL define an abstract scrape() method that all concrete scrapers must implement
2. THE AbstractScraper SHALL define common attributes: source_name, base_url, timeout
3. THE AbstractScraper SHALL provide a common error handling mechanism for network failures
4. THE AbstractScraper SHALL enforce the Liskov Substitution Principle - all subclasses must be substitutable for the base class
5. THE AbstractScraper SHALL use the abc module for abstract base class definition

### Requirement 6: Scraper Factory Pattern

**User Story:** As a developer, I want a factory to create scraper instances, so that scraper instantiation logic is centralized and maintainable.

#### Acceptance Criteria

1. THE ScraperFactory SHALL implement the Factory Pattern for creating scraper instances
2. WHEN given a source type (youtube, pib, government_schemes), THE ScraperFactory SHALL return the appropriate scraper instance
3. THE ScraperFactory SHALL raise an exception for unknown source types
4. THE ScraperFactory SHALL support dependency injection for scraper configuration
5. THE ScraperFactory SHALL maintain a registry of available scrapers

### Requirement 7: Exam-Specific Categorization System

**User Story:** As a competitive exam aspirant, I want articles categorized by exam-relevant topics, so that I can focus on specific subjects during my preparation.

#### Acceptance Criteria

1. THE CategorizationAgent SHALL inherit from AbstractAgent
2. THE CategorizationAgent SHALL categorize content into: Polity, Economy, International Relations, Science & Tech, Environment & Ecology, Defence & Security, Government Schemes, Social Issues
3. WHEN categorizing content, THE CategorizationAgent SHALL use Google Gemini 1.5 Flash API
4. THE CategorizationAgent SHALL assign one primary category and up to two secondary categories per article
5. THE CategorizationAgent SHALL implement the execute() method defined in AbstractAgent
6. THE CategorizationAgent SHALL validate that assigned categories exist in the predefined category list

### Requirement 8: Enhanced AI Summaries for Exam Preparation

**User Story:** As a competitive exam aspirant, I want AI-generated summaries that explain exam relevance, so that I can quickly understand why an article matters for my preparation.

#### Acceptance Criteria

1. THE SummarizationAgent SHALL inherit from AbstractAgent
2. THE SummarizationAgent SHALL generate summaries containing: main content summary, why important for exam, prelims relevance, mains relevance, possible question angle
3. WHEN generating summaries, THE SummarizationAgent SHALL use Google Gemini 1.5 Flash API
4. THE SummarizationAgent SHALL limit summaries to 200-300 words
5. THE SummarizationAgent SHALL implement the execute() method defined in AbstractAgent
6. THE SummarizationAgent SHALL include specific examples and facts from the source content

### Requirement 9: Abstract Agent Base Class

**User Story:** As a system architect, I want a common interface for all AI agents, so that agent behavior is consistent and extensible.

#### Acceptance Criteria

1. THE AbstractAgent SHALL define an abstract execute() method that all concrete agents must implement
2. THE AbstractAgent SHALL provide common initialization for Gemini API client
3. THE AbstractAgent SHALL define common attributes: model_name, temperature, max_tokens
4. THE AbstractAgent SHALL provide error handling for API failures
5. THE AbstractAgent SHALL enforce the Interface Segregation Principle - agents should only depend on methods they use

### Requirement 10: Exam Relevance Ranking System

**User Story:** As a competitive exam aspirant, I want articles ranked by exam relevance, so that I can prioritize the most important content for my preparation.

#### Acceptance Criteria

1. THE RankingAgent SHALL inherit from AbstractAgent
2. THE RankingAgent SHALL use a RankingStrategy instance for scoring articles
3. WHEN ranking articles, THE RankingAgent SHALL consider: UPSC syllabus match, importance level, freshness, impact level
4. THE RankingAgent SHALL assign a relevance score from 0.0 to 10.0 for each article
5. THE RankingAgent SHALL implement the execute() method defined in AbstractAgent
6. THE RankingAgent SHALL support dependency injection of different ranking strategies

### Requirement 11: Abstract Ranking Strategy

**User Story:** As a system architect, I want interchangeable ranking algorithms, so that ranking logic can be customized for different exam types (Strategy Pattern).

#### Acceptance Criteria

1. THE AbstractRankingStrategy SHALL define an abstract calculate_score() method
2. THE UPSCRankingStrategy SHALL inherit from AbstractRankingStrategy and implement UPSC-specific scoring
3. THE SSCRankingStrategy SHALL inherit from AbstractRankingStrategy and implement SSC-specific scoring
4. THE BankingRankingStrategy SHALL inherit from AbstractRankingStrategy and implement Banking exam-specific scoring
5. WHERE a custom ranking algorithm is needed, THE System SHALL allow new strategy classes to be added without modifying existing code

### Requirement 12: Database Schema for Exam Content

**User Story:** As a system architect, I want a well-designed database schema, so that exam content is stored efficiently with proper relationships.

#### Acceptance Criteria

1. THE System SHALL create the following tables: articles, summaries, rankings, categories, user_profiles, sources
2. THE articles table SHALL have foreign key relationships to sources and categories tables
3. THE summaries table SHALL have a foreign key relationship to the articles table
4. THE rankings table SHALL have a foreign key relationship to the articles table
5. THE System SHALL create indexes on: article published_at, category_id, ranking score, source_id
6. THE System SHALL use SQLAlchemy ORM models for all database entities
7. THE System SHALL enforce referential integrity through foreign key constraints

### Requirement 13: Repository Pattern for Data Access

**User Story:** As a developer, I want database access abstracted through repositories, so that business logic is decoupled from data access details.

#### Acceptance Criteria

1. THE ArticleRepository SHALL implement methods: create(), find_by_id(), find_by_date_range(), find_by_category(), update(), delete()
2. THE SummaryRepository SHALL implement methods: create(), find_by_article_id(), update()
3. THE RankingRepository SHALL implement methods: create(), find_top_n(), find_by_article_id(), update()
4. THE CategoryRepository SHALL implement methods: find_all(), find_by_name()
5. THE SourceRepository SHALL implement methods: find_all(), find_by_type()
6. THE System SHALL use dependency injection to provide repository instances to services
7. THE System SHALL ensure repositories handle database sessions properly (open, commit, rollback, close)

### Requirement 14: Service Layer for Business Logic

**User Story:** As a system architect, I want business logic separated from data access and presentation, so that the system follows the Service Layer Pattern.

#### Acceptance Criteria

1. THE ScrapingService SHALL orchestrate scraper execution and store results via repositories
2. THE CategorizationService SHALL coordinate between CategorizationAgent and repositories
3. THE SummarizationService SHALL coordinate between SummarizationAgent and repositories
4. THE RankingService SHALL coordinate between RankingAgent and repositories
5. THE DigestGenerationService SHALL compile ranked articles into a formatted digest
6. THE System SHALL ensure services depend on abstractions (interfaces) not concrete implementations (Dependency Inversion Principle)

### Requirement 15: CLI Pipeline Execution

**User Story:** As a system operator, I want to run the complete pipeline via CLI, so that I can automate daily content processing.

#### Acceptance Criteria

1. WHEN executing "python scripts/run_pipeline.py 24 10", THE System SHALL run the complete pipeline for the last 24 hours and select top 10 articles
2. THE Pipeline SHALL execute steps in order: Scrape → Categorize → Summarize → Rank → Store → Generate Digest
3. THE Pipeline SHALL log progress at each step with timestamps
4. IF any step fails, THEN THE Pipeline SHALL log the error and continue with remaining articles
5. THE Pipeline SHALL output a summary report showing: articles scraped, articles categorized, articles summarized, articles ranked, top articles selected
6. THE Pipeline SHALL support command-line arguments: hours (lookback period), top_n (number of articles), --dry-run (skip database writes)

### Requirement 16: OOP Principles Implementation

**User Story:** As a student, I want the codebase to demonstrate strong OOP principles, so that I can learn and document best practices for my academic project.

#### Acceptance Criteria

1. THE System SHALL demonstrate Encapsulation through private attributes (prefixed with _) and controlled access via properties and methods
2. THE System SHALL demonstrate Abstraction through abstract base classes (AbstractScraper, AbstractAgent, AbstractRankingStrategy)
3. THE System SHALL demonstrate Inheritance through concrete classes extending abstract bases
4. THE System SHALL demonstrate Polymorphism through method overriding and duck typing
5. THE System SHALL follow the Single Responsibility Principle - each class has one reason to change
6. THE System SHALL follow the Open/Closed Principle - open for extension, closed for modification
7. THE System SHALL follow the Liskov Substitution Principle - subclasses are substitutable for base classes
8. THE System SHALL follow the Interface Segregation Principle - no client depends on unused methods
9. THE System SHALL follow the Dependency Inversion Principle - depend on abstractions, not concretions

### Requirement 17: Design Patterns Implementation

**User Story:** As a student, I want the codebase to implement common design patterns, so that I can document pattern usage for my academic project.

#### Acceptance Criteria

1. THE System SHALL implement the Factory Pattern for scraper creation (ScraperFactory)
2. THE System SHALL implement the Strategy Pattern for ranking algorithms (AbstractRankingStrategy with multiple implementations)
3. THE System SHALL implement the Repository Pattern for data access (ArticleRepository, SummaryRepository, etc.)
4. THE System SHALL implement the Service Layer Pattern for business logic (ScrapingService, CategorizationService, etc.)
5. THE System SHALL implement the Singleton Pattern for database connection management
6. THE System SHALL document each pattern usage with inline comments explaining the pattern and its benefits

### Requirement 18: Type Hints and Documentation

**User Story:** As a developer, I want comprehensive type hints and docstrings, so that the codebase is maintainable and self-documenting.

#### Acceptance Criteria

1. THE System SHALL include type hints for all function parameters and return values
2. THE System SHALL include docstrings for all classes following Google docstring format
3. THE System SHALL include docstrings for all public methods following Google docstring format
4. THE System SHALL include inline comments explaining complex logic
5. THE System SHALL use Pydantic models for data validation where appropriate

### Requirement 19: UML Diagrams for Documentation

**User Story:** As a student, I want UML diagrams generated, so that I can include them in my project report.

#### Acceptance Criteria

1. THE System SHALL provide a UML Class Diagram in Mermaid format showing all classes, attributes, methods, and relationships
2. THE Class Diagram SHALL show inheritance relationships (AbstractScraper → YouTubeScraper, PIBScraper, etc.)
3. THE Class Diagram SHALL show composition relationships (RankingAgent contains RankingStrategy)
4. THE Class Diagram SHALL show dependency relationships (Services depend on Repositories)
5. THE System SHALL provide a Component Diagram in Mermaid format showing system architecture layers (Presentation, Service, Data Access, External APIs)

### Requirement 20: Academic Project Report

**User Story:** As a student, I want a project report template, so that I can document my work for academic submission.

#### Acceptance Criteria

1. THE System SHALL provide a 2-3 page project report template covering: Introduction, System Architecture, OOP Principles Usage, Design Patterns Usage, Database Design, Conclusion
2. THE Report SHALL include explanations of how each OOP principle is implemented with code examples
3. THE Report SHALL include explanations of how each design pattern is implemented with code examples
4. THE Report SHALL include the UML Class Diagram and Component Diagram
5. THE Report SHALL include a section on challenges faced and solutions implemented

### Requirement 21: Production Readiness and Testing

**User Story:** As a system operator, I want the transformed system to be production-ready, so that it can be deployed without breaking existing functionality.

#### Acceptance Criteria

1. THE System SHALL maintain compatibility with existing Docker configuration
2. THE System SHALL maintain compatibility with existing Render deployment configuration
3. THE System SHALL maintain compatibility with existing PostgreSQL database connection
4. THE System SHALL include error handling for all external API calls (Gemini, YouTube, PIB)
5. THE System SHALL include retry logic for transient failures
6. THE System SHALL log all errors with sufficient context for debugging
7. THE System SHALL validate environment variables on startup and fail fast if required variables are missing

### Requirement 22: Configuration Management

**User Story:** As a system operator, I want centralized configuration, so that I can easily modify system behavior without code changes.

#### Acceptance Criteria

1. THE System SHALL store all configuration in environment variables or a config file
2. THE System SHALL support configuration for: YouTube channels, PIB URL, scraping intervals, ranking weights, Gemini API parameters
3. THE System SHALL validate configuration on startup
4. THE System SHALL provide sensible defaults for optional configuration
5. THE System SHALL document all configuration options in README.md

### Requirement 23: Backward Compatibility During Transformation

**User Story:** As a system operator, I want the transformation to be incremental, so that the system remains functional during development.

#### Acceptance Criteria

1. THE System SHALL maintain existing database tables during transformation
2. THE System SHALL support both old and new scrapers during transition period
3. THE System SHALL provide migration scripts for database schema changes
4. THE System SHALL maintain existing API contracts for any external integrations
5. THE System SHALL include rollback procedures in case of deployment issues

### Requirement 24: Performance and Scalability

**User Story:** As a system operator, I want the system to handle increased content volume, so that it scales with growing data sources.

#### Acceptance Criteria

1. WHEN processing 100+ articles, THE System SHALL complete within 30 minutes
2. THE System SHALL use database connection pooling for efficient resource usage
3. THE System SHALL implement batch processing for database inserts (bulk insert operations)
4. THE System SHALL cache frequently accessed data (categories, sources) in memory
5. THE System SHALL support parallel scraping of multiple sources using threading or async operations

### Requirement 25: Monitoring and Observability

**User Story:** As a system operator, I want comprehensive logging and monitoring, so that I can track system health and diagnose issues.

#### Acceptance Criteria

1. THE System SHALL log pipeline execution start and end times
2. THE System SHALL log article counts at each pipeline stage (scraped, categorized, summarized, ranked)
3. THE System SHALL log API call latencies for Gemini API
4. THE System SHALL log database query execution times for slow queries (>1 second)
5. THE System SHALL provide a summary report at pipeline completion showing success/failure counts and total execution time
