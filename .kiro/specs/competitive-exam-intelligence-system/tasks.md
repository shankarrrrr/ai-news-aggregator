# Implementation Plan: Competitive Exam Intelligence System

## Overview

This implementation plan transforms the existing AI News Aggregator into a Competitive Exam Intelligence System. The transformation maintains all production infrastructure (Gemini API, PostgreSQL, Docker, Render) while implementing strong OOP principles and design patterns. The implementation follows an incremental approach across 8 phases, building from foundation to deployment.

## Implementation Approach

- Maintain existing tech stack: Gemini 1.5 Flash API, PostgreSQL, SQLAlchemy, Docker, Render
- Follow SOLID principles throughout all implementations
- Implement 5 design patterns: Factory, Strategy, Repository, Service Layer, Singleton
- Use type hints and Google-style docstrings for all code
- Property-based testing with Hypothesis (100 iterations minimum per property)
- Target 80% code coverage
- Production-ready error handling and logging

## Tasks

- [x] 1. Phase 1: Foundation - Abstract Base Classes and Configuration
  - [x] 1.1 Create AbstractScraper base class with template method pattern
    - Create `app/scrapers/abstract_scraper.py`
    - Implement AbstractScraper with abstract scrape() method
    - Add ScrapedContent Pydantic model for type safety
    - Implement common validation and error handling methods
    - Use private attributes (_source_name, _base_url, _timeout) with property accessors
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 16.1, 18.1, 18.2_

  - [x] 1.2 Create AbstractAgent base class for AI processing
    - Create `app/agent/abstract_agent.py`
    - Implement AbstractAgent with abstract execute() method
    - Add AgentConfig Pydantic model for configuration
    - Implement common Gemini API client initialization
    - Add _call_gemini_api() and _parse_json_response() helper methods
    - Add AgentException custom exception class
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 16.1, 18.1, 18.2_

  - [x] 1.3 Create AbstractRankingStrategy base class for strategy pattern
    - Create `app/services/ranking/abstract_ranking_strategy.py`
    - Implement AbstractRankingStrategy with abstract calculate_score() method
    - Add ArticleMetadata and RankingResult Pydantic models
    - Implement weight validation in __init__
    - Add helper methods: _calculate_freshness_score(), _calculate_category_relevance()
    - _Requirements: 11.1, 16.2, 17.2, 18.1, 18.2_

  - [x] 1.4 Update configuration management for exam system
    - Update `app/config.py` with exam-specific configuration
    - Add EXAM_CATEGORIES list (8 categories)
    - Add YouTube exam channel IDs (11 channels)
    - Add PIB and government scheme portal URLs
    - Add ranking strategy weights for UPSC/SSC/Banking
    - Add configuration validation on startup
    - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.5, 21.7_

- [x] 2. Phase 2: Scraper Implementations
  - [x] 2.1 Implement YouTubeScraper for exam preparation channels
    - Create `app/scrapers/youtube_scraper.py`
    - Inherit from AbstractScraper
    - Implement scrape() method using RSS feeds and transcript API
    - Add EXAM_CHANNELS class constant with 11 channel IDs
    - Implement _get_recent_videos(), _extract_video_id(), _get_transcript()
    - Handle missing transcripts gracefully (return None, don't crash)
    - Filter out YouTube Shorts
    - Store video metadata in ScrapedContent.metadata
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 16.3, 16.7_


  - [ ]* 2.2 Write property test for YouTubeScraper output completeness
    - **Property 1: Scraper Output Completeness**
    - **Validates: Requirements 2.4**
    - Create `tests/property/test_scraper_properties.py`
    - Test that all scraped content has required fields (title, content, url, published_at, source_type, metadata)
    - Use Hypothesis with 100 iterations minimum
    - _Requirements: 2.4, Property 1_

  - [x] 2.3 Implement PIBScraper for government press releases
    - Create `app/scrapers/pib_scraper.py`
    - Inherit from AbstractScraper
    - Implement scrape() method using BeautifulSoup for HTML parsing
    - Add EXAM_RELEVANT_CATEGORIES class constant
    - Implement _scrape_category(), _parse_release(), _extract_ministry()
    - Handle PIB date format parsing (DD-MMM-YYYY HH:MM)
    - Handle network errors and malformed HTML gracefully
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 16.3, 16.7_

  - [ ]* 2.4 Write property test for time window filtering
    - **Property 2: Time Window Filtering**
    - **Validates: Requirements 3.4**
    - Test that all scraped content falls within specified time window
    - Use Hypothesis to generate various time windows (1-168 hours)
    - _Requirements: 3.4, Property 2_

  - [x] 2.5 Implement GovernmentSchemesScraper for welfare programs
    - Create `app/scrapers/government_schemes_scraper.py`
    - Inherit from AbstractScraper
    - Implement scrape() method for government scheme portals
    - Add SCHEME_PORTALS class constant
    - Implement _scrape_portal(), _parse_scheme(), _extract_scheme_metadata(), _format_scheme_content()
    - Handle varying HTML structures across portals
    - Use current timestamp for schemes (updated less frequently than news)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 16.3, 16.7_

  - [ ]* 2.6 Write property test for Liskov Substitution Principle
    - **Property 3: Liskov Substitution for Scrapers**
    - **Validates: Requirements 5.4, 16.7**
    - Test that all scraper subclasses are substitutable for AbstractScraper
    - Verify polymorphic usage works correctly
    - _Requirements: 5.4, 16.7, Property 3_

  - [x] 2.7 Implement ScraperFactory with registry pattern
    - Create `app/scrapers/scraper_factory.py`
    - Create SourceType enum (YOUTUBE, PIB, GOVERNMENT_SCHEMES)
    - Implement class-level _registry dictionary
    - Implement register_scraper(), create_scraper(), get_available_sources(), create_all_scrapers()
    - Register all three scrapers at module level
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 17.1, 16.2_

  - [ ]* 2.8 Write property test for Factory Pattern correctness
    - **Property 4: Factory Pattern Correctness**
    - **Validates: Requirements 6.2**
    - Test that factory returns correct scraper type for each SourceType
    - Verify all returned scrapers inherit from AbstractScraper
    - _Requirements: 6.2, Property 4_

- [x] 3. Checkpoint - Verify scraper foundation
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Phase 3: Agent Implementations
  - [x] 4.1 Implement CategorizationAgent for exam-relevant categorization
    - Create `app/agent/categorization_agent.py`
    - Inherit from AbstractAgent
    - Add EXAM_CATEGORIES class constant (8 categories)
    - Add CategoryResult Pydantic model
    - Implement execute() method with Gemini API integration
    - Implement _build_categorization_prompt() with structured JSON output
    - Implement _validate_categories() to ensure valid category assignment
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 16.3, 16.4_

  - [ ]* 4.2 Write property test for categorization constraints
    - **Property 5: Categorization Constraints**
    - **Validates: Requirements 7.2, 7.4, 7.6**
    - Test that categorization produces exactly 1 primary + max 2 secondary categories
    - Verify all categories are from predefined list and distinct
    - Use Hypothesis to generate various article content
    - _Requirements: 7.2, 7.4, 7.6, Property 5_

  - [x] 4.3 Implement SummarizationAgent for exam-focused summaries
    - Create `app/agent/summarization_agent.py`
    - Inherit from AbstractAgent
    - Add SummaryResult Pydantic model with all required sections
    - Implement execute() method with category-aware prompting
    - Implement _build_summarization_prompt() for exam-focused analysis
    - Implement get_formatted_summary() for readable output
    - Limit summary to 200-300 words
    - Include prelims/mains relevance, possible questions, key facts
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 16.3, 16.4_

  - [ ]* 4.4 Write property test for summary structure completeness
    - **Property 6: Summary Structure Completeness**
    - **Validates: Requirements 8.2, 8.4**
    - Test that summaries contain all required sections
    - Verify summary word count is 200-300 words
    - Verify at least 3 possible questions included
    - _Requirements: 8.2, 8.4, Property 6_

  - [ ]* 4.5 Write property test for summary content fidelity
    - **Property 7: Summary Content Fidelity**
    - **Validates: Requirements 8.6**
    - Test that summaries include at least one specific fact from source
    - Verify summaries are grounded in original content
    - _Requirements: 8.6, Property 7_

  - [x] 4.6 Implement RankingAgent with strategy pattern
    - Create `app/agent/ranking_agent.py`
    - Inherit from AbstractAgent
    - Accept AbstractRankingStrategy in __init__ (dependency injection)
    - Implement execute() method that delegates to strategy
    - Implement set_strategy() for runtime strategy switching
    - Implement _should_use_ai_enhancement() for borderline cases (scores 4.0-6.0)
    - Implement _enhance_with_ai() for hybrid ranking
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 16.9, 17.2_

  - [ ]* 4.7 Write property test for ranking score bounds
    - **Property 8: Ranking Score Bounds**
    - **Validates: Requirements 10.4**
    - Test that all ranking scores are between 0.0 and 10.0
    - Test with all three ranking strategies
    - Use Hypothesis to generate various article metadata
    - _Requirements: 10.4, Property 8_

  - [x] 4.8 Implement DigestAgent for formatted output compilation
    - Create `app/agent/digest_agent.py`
    - Inherit from AbstractAgent
    - Add DigestArticle and DigestResult Pydantic models
    - Implement execute() method to compile ranked articles
    - Implement _group_by_category() to organize articles
    - Implement _generate_introduction() and _generate_conclusion() with AI
    - Implement _get_top_categories() for summary statistics
    - Implement format_as_text() for readable output
    - _Requirements: 16.3, 16.4, 18.1, 18.2_

- [x] 5. Phase 4: Ranking Strategy Implementations
  - [x] 5.1 Implement UPSCRankingStrategy for civil services exam
    - Create `app/services/ranking/upsc_ranking_strategy.py`
    - Inherit from AbstractRankingStrategy
    - Add PRIORITY_CATEGORIES (Polity, International Relations, Economy)
    - Add DEFAULT_WEIGHTS for scoring factors
    - Implement calculate_score() with UPSC-specific logic
    - Implement _calculate_content_depth() for analytical depth
    - Implement _calculate_source_credibility() for source reliability
    - Implement _generate_reasoning() for explainable scores
    - _Requirements: 11.2, 16.2, 16.3, 17.2_

  - [x] 5.2 Implement SSCRankingStrategy for staff selection exam
    - Create `app/services/ranking/ssc_ranking_strategy.py`
    - Inherit from AbstractRankingStrategy
    - Add PRIORITY_CATEGORIES (Economy, Polity, Science & Tech)
    - Add DEFAULT_WEIGHTS optimized for SSC exam pattern
    - Implement calculate_score() with SSC-specific logic
    - Implement _calculate_factual_density() for fact-based content
    - Implement _calculate_source_credibility()
    - Implement _generate_reasoning()
    - _Requirements: 11.3, 16.2, 16.3, 17.2_

  - [x] 5.3 Implement BankingRankingStrategy for banking exams
    - Create `app/services/ranking/banking_ranking_strategy.py`
    - Inherit from AbstractRankingStrategy
    - Add PRIORITY_CATEGORIES (Economy, Government Schemes)
    - Add BANKING_KEYWORDS for domain-specific scoring
    - Add DEFAULT_WEIGHTS optimized for banking exams
    - Implement calculate_score() with banking-specific logic
    - Implement _calculate_banking_keyword_score() for domain relevance
    - Implement _calculate_source_credibility()
    - Implement _generate_reasoning()
    - _Requirements: 11.4, 16.2, 16.3, 17.2_

- [x] 6. Checkpoint - Verify agent and strategy implementations
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Phase 5: Database Models and Repositories
  - [x] 7.1 Create database models with SQLAlchemy ORM
    - Create `app/database/models.py`
    - Implement Base and TimestampMixin
    - Implement Source model with relationships
    - Implement Category model
    - Implement Article model with foreign keys to Source and Category
    - Implement Summary model with foreign key to Article
    - Implement Ranking model with foreign key to Article
    - Implement UserProfile model for future extensibility
    - Add indexes on: article.published_at, article.category_id, ranking.score, article.source_id
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 18.1, 18.2_

  - [ ]* 7.2 Write property test for database referential integrity
    - **Property 9: Database Referential Integrity**
    - **Validates: Requirements 12.7**
    - Test that deleting an article cascades to summaries and rankings
    - Verify referential integrity is maintained
    - _Requirements: 12.7, Property 9_

  - [x] 7.3 Implement BaseRepository with generic type support
    - Create `app/database/repositories/base_repository.py`
    - Implement BaseRepository[T] as generic class
    - Implement _get_session() context manager with proper error handling
    - Implement create(), find_by_id(), find_all(), update(), delete()
    - Add proper session management: commit on success, rollback on error, close always
    - Add RepositoryException custom exception
    - _Requirements: 13.6, 13.7, 16.1, 17.3, 18.1, 18.2_

  - [ ]* 7.4 Write property test for repository session management
    - **Property 10: Repository Session Management**
    - **Validates: Requirements 13.7**
    - Test that sessions are properly opened, committed/rolled back, and closed
    - Verify no connection leaks occur
    - _Requirements: 13.7, Property 10_

  - [x] 7.5 Implement ArticleRepository with exam-specific queries
    - Create `app/database/repositories/article_repository.py`
    - Inherit from BaseRepository[Article]
    - Implement find_by_date_range(), find_by_category(), find_by_source()
    - Implement find_by_url() for duplicate detection
    - Implement bulk_create() for efficient batch inserts
    - _Requirements: 13.1, 24.3, 18.1, 18.2_

  - [x] 7.6 Implement SummaryRepository
    - Create `app/database/repositories/summary_repository.py`
    - Inherit from BaseRepository[Summary]
    - Implement find_by_article_id()
    - _Requirements: 13.2, 18.1, 18.2_

  - [x] 7.7 Implement RankingRepository with top-N queries
    - Create `app/database/repositories/ranking_repository.py`
    - Inherit from BaseRepository[Ranking]
    - Implement find_by_article_id(), find_top_n(), find_by_score_range()
    - Optimize find_top_n() with proper indexing
    - _Requirements: 13.3, 18.1, 18.2_

  - [x] 7.8 Implement CategoryRepository
    - Create `app/database/repositories/category_repository.py`
    - Inherit from BaseRepository[Category]
    - Implement find_by_name(), find_all_ordered()
    - _Requirements: 13.4, 18.1, 18.2_

  - [x] 7.9 Implement SourceRepository
    - Create `app/database/repositories/source_repository.py`
    - Inherit from BaseRepository[Source]
    - Implement find_by_type(), find_active_sources()
    - _Requirements: 13.5, 18.1, 18.2_

- [-] 8. Phase 6: Service Layer Implementation
  - [x] 8.1 Implement ScrapingService for orchestrating scrapers
    - Create `app/services/scraping_service.py`
    - Accept ScraperFactory, ArticleRepository, SourceRepository via dependency injection
    - Implement scrape_all_sources() to coordinate scraping
    - Implement _scrape_source() for individual source processing
    - Implement _filter_duplicates() using URL comparison
    - Implement _create_article_entity() for ORM object creation
    - Use bulk_create() for efficient database inserts
    - Handle scraper errors gracefully (log and continue)
    - _Requirements: 14.1, 14.6, 16.9, 17.4, 24.3_

  - [x] 8.2 Implement CategorizationService
    - Create `app/services/categorization_service.py`
    - Accept CategorizationAgent, ArticleRepository, CategoryRepository via DI
    - Implement categorize_articles() for batch processing
    - Implement _categorize_article() for single article
    - Update article.category_id after categorization
    - Handle agent errors gracefully
    - _Requirements: 14.2, 14.6, 16.9, 17.4_

  - [x] 8.3 Implement SummarizationService
    - Create `app/services/summarization_service.py`
    - Accept SummarizationAgent, ArticleRepository, SummaryRepository via DI
    - Implement summarize_articles() for batch processing
    - Implement _summarize_article() for single article
    - Create Summary entity and persist to database
    - Handle agent errors gracefully
    - _Requirements: 14.3, 14.6, 16.9, 17.4_

  - [x] 8.4 Implement RankingService with strategy selection
    - Create `app/services/ranking_service.py`
    - Accept RankingAgent, ArticleRepository, RankingRepository via DI
    - Implement rank_articles() with exam_type parameter
    - Implement _select_strategy() to choose UPSC/SSC/Banking strategy
    - Implement _rank_article() for single article
    - Create Ranking entity and persist to database
    - Handle agent errors gracefully
    - _Requirements: 14.4, 14.6, 16.9, 17.4_

  - [x] 8.5 Implement DigestGenerationService
    - Create `app/services/digest_generation_service.py`
    - Accept DigestAgent, RankingRepository via DI
    - Implement generate_digest() to compile top-ranked articles
    - Fetch top N articles from RankingRepository
    - Convert to DigestArticle format
    - Call DigestAgent to generate formatted output
    - Return formatted text digest
    - _Requirements: 14.5, 14.6, 16.9, 17.4_

- [x] 9. Phase 7: Pipeline Orchestration and CLI
  - [x] 9.1 Implement Pipeline class for workflow orchestration
    - Create `app/pipeline/pipeline.py`
    - Accept all services via dependency injection
    - Implement execute() method with hours and top_n parameters
    - Execute stages in order: Scrape → Categorize → Summarize → Rank → Store → Digest
    - Implement _log_stage_start() and _log_stage_end() for observability
    - Implement _generate_summary_report() with execution statistics
    - Handle stage failures gracefully (log and continue with remaining items)
    - Return PipelineResult with statistics
    - _Requirements: 15.2, 15.3, 15.4, 15.5, 16.1, 25.1, 25.2, 25.5_

  - [ ]* 9.2 Write property test for pipeline execution order
    - **Property 11: Pipeline Execution Order**
    - **Validates: Requirements 15.2**
    - Test that pipeline stages execute in correct order
    - Verify each stage completes before next begins
    - _Requirements: 15.2, Property 11_

  - [ ]* 9.3 Write property test for pipeline progress logging
    - **Property 12: Pipeline Progress Logging**
    - **Validates: Requirements 15.3, 25.1, 25.2**
    - Test that logs are generated at start/end of each stage
    - Verify logs contain timestamps and stage names
    - _Requirements: 15.3, 25.1, 25.2, Property 12_

  - [ ]* 9.4 Write property test for pipeline summary report
    - **Property 13: Pipeline Summary Report**
    - **Validates: Requirements 15.5, 25.5**
    - Test that summary report contains all required statistics
    - Verify article counts and execution time are included
    - _Requirements: 15.5, 25.5, Property 13_

  - [x] 9.5 Update CLI script for exam intelligence pipeline
    - Update `scripts/run_pipeline.py`
    - Add command-line arguments: hours, top_n, --exam-type, --dry-run
    - Initialize all dependencies (factories, repositories, services, agents)
    - Create Pipeline instance with dependency injection
    - Execute pipeline and display results
    - Handle --dry-run flag (skip database writes)
    - Display formatted digest output
    - _Requirements: 15.1, 15.6, 22.1_

  - [x] 9.6 Implement configuration validation on startup
    - Create `app/config_validator.py`
    - Implement validate_configuration() function
    - Check required environment variables (GEMINI_API_KEY, DATABASE_URL)
    - Validate YouTube channel IDs format
    - Validate ranking weights sum to 1.0
    - Fail fast with clear error messages if validation fails
    - _Requirements: 21.7, 22.3_

- [x] 10. Checkpoint - Verify pipeline integration
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Phase 8: Testing, Error Handling, and Documentation
  - [x] 11.1 Implement comprehensive error handling patterns
    - Add scrape_with_retry() to AbstractScraper with exponential backoff
    - Add execute_with_fallback() to AbstractAgent
    - Implement TransientError and PermanentError exception classes
    - Add retry logic for network timeouts and API rate limits
    - Add proper logging for all error conditions
    - _Requirements: 21.4, 21.5, 21.6_

  - [ ]* 11.2 Write property test for external API error handling
    - **Property 14: External API Error Handling**
    - **Validates: Requirements 21.4, 21.6**
    - Test that API errors are caught and logged without crashing
    - Verify error context is included in logs
    - _Requirements: 21.4, 21.6, Property 14_

  - [x] 11.3 Implement performance monitoring and logging
    - Create `app/monitoring/performance.py`
    - Implement @monitor_performance decorator for timing
    - Implement log_api_latency() for Gemini API calls
    - Implement log_slow_query() for database queries >1 second
    - Configure structured logging with timestamps and context
    - _Requirements: 25.3, 25.4, 21.6_

  - [ ]* 11.4 Write property test for API call latency logging
    - **Property 15: API Call Latency Logging**
    - **Validates: Requirements 25.3**
    - Test that slow API calls (>1 second) are logged
    - Verify latency measurement is accurate
    - _Requirements: 25.3, Property 15_

  - [ ]* 11.5 Write property test for slow query logging
    - **Property 16: Slow Query Logging**
    - **Validates: Requirements 25.4**
    - Test that slow queries (>1 second) are logged
    - Verify query details are included
    - _Requirements: 25.4, Property 16_

  - [ ]* 11.6 Write unit tests for scrapers
    - Create `tests/unit/test_scrapers.py`
    - Test YouTubeScraper with specific channel
    - Test YouTubeScraper handles missing transcripts
    - Test PIBScraper network error handling
    - Test GovernmentSchemesScraper metadata extraction
    - Test ScraperFactory registration and creation
    - _Requirements: 21.1, 21.2, 21.3_

  - [ ]* 11.7 Write unit tests for agents
    - Create `tests/unit/test_agents.py`
    - Test CategorizationAgent with sample articles
    - Test SummarizationAgent output format
    - Test RankingAgent strategy switching
    - Test DigestAgent grouping logic
    - _Requirements: 21.1, 21.2, 21.3_

  - [ ]* 11.8 Write unit tests for repositories
    - Create `tests/unit/test_repositories.py`
    - Test ArticleRepository CRUD operations
    - Test ArticleRepository duplicate detection
    - Test RankingRepository top-N queries
    - Test repository error handling
    - _Requirements: 21.1, 21.2, 21.3_

  - [ ]* 11.9 Write integration tests for database operations
    - Create `tests/integration/test_database.py`
    - Test article creation with relationships
    - Test cascade delete behavior
    - Test transaction rollback on errors
    - Use test database fixture
    - _Requirements: 21.1, 21.2, 21.3_

  - [ ]* 11.10 Write integration tests for full pipeline
    - Create `tests/integration/test_pipeline.py`
    - Test complete pipeline execution end-to-end
    - Test pipeline with --dry-run flag
    - Test pipeline error recovery
    - Verify article counts at each stage
    - _Requirements: 21.1, 21.2, 21.3_

  - [x] 11.11 Create database migration script
    - Create `app/database/migrations/001_transform_to_exam_system.py`
    - Add new tables: sources, categories, summaries, rankings, user_profiles
    - Migrate existing articles table (add category_id, source_id foreign keys)
    - Create indexes on frequently queried columns
    - Seed categories table with 8 exam categories
    - Seed sources table with YouTube, PIB, Government Schemes
    - Add rollback procedures
    - _Requirements: 23.1, 23.2, 23.3, 23.5_

  - [x] 11.12 Generate UML diagrams for documentation
    - Create `docs/uml/class_diagram.md` with Mermaid syntax
    - Include all classes with attributes, methods, and relationships
    - Show inheritance (AbstractScraper → concrete scrapers)
    - Show composition (RankingAgent contains RankingStrategy)
    - Show dependencies (Services depend on Repositories)
    - Create `docs/uml/component_diagram.md` with architecture layers
    - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5_

  - [x] 11.13 Create academic project report
    - Create `docs/PROJECT_REPORT.md`
    - Write Introduction section (system overview, objectives)
    - Write System Architecture section (layered architecture, components)
    - Write OOP Principles section (examples of each SOLID principle)
    - Write Design Patterns section (examples of each pattern with code)
    - Write Database Design section (ER diagram, schema explanation)
    - Write Challenges and Solutions section
    - Write Conclusion section
    - Include UML diagrams
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_

  - [x] 11.14 Update README with transformation details
    - Update `README.md` with exam intelligence system description
    - Document new features (YouTube channels, PIB, government schemes)
    - Document exam categories and ranking strategies
    - Update installation instructions
    - Update usage examples with new CLI arguments
    - Document configuration options
    - _Requirements: 22.5_

- [x] 12. Phase 9: Deployment and Production Readiness
  - [x] 12.1 Update Docker configuration for new dependencies
    - Update `Dockerfile` with new Python dependencies
    - Add BeautifulSoup, feedparser, youtube-transcript-api, hypothesis
    - Ensure PostgreSQL client libraries included
    - Test Docker build locally
    - _Requirements: 21.1, 21.2, 23.1_

  - [x] 12.2 Update Render deployment configuration
    - Update `render.yaml` with new environment variables
    - Add EXAM_CATEGORIES, YOUTUBE_CHANNELS configuration
    - Verify PostgreSQL connection settings
    - Test deployment to Render staging environment
    - _Requirements: 21.2, 23.1, 23.4_

  - [x] 12.3 Implement health check endpoint
    - Create `app/health.py`
    - Implement check_database_connection()
    - Implement check_gemini_api()
    - Implement check_external_sources()
    - Return health status JSON
    - _Requirements: 25.1_

  - [x] 12.4 Run database migration on production
    - Execute migration script on production database
    - Verify all tables created successfully
    - Verify indexes created
    - Verify seed data inserted
    - Test rollback procedure
    - _Requirements: 23.1, 23.2, 23.3, 23.5_

  - [x] 12.5 Perform end-to-end testing in production
    - Run pipeline with small time window (1 hour)
    - Verify articles scraped from all sources
    - Verify categorization accuracy
    - Verify summaries generated correctly
    - Verify ranking scores reasonable
    - Verify digest output formatted correctly
    - _Requirements: 21.1, 21.2, 21.3_

  - [x] 12.6 Set up monitoring and alerting
    - Configure logging to capture all pipeline executions
    - Set up alerts for pipeline failures
    - Set up alerts for slow API calls (>5 seconds)
    - Set up alerts for database connection issues
    - Monitor daily digest generation
    - _Requirements: 25.1, 25.2, 25.3, 25.4, 25.5_

- [x] 13. Final checkpoint - Production deployment complete
  - Ensure all tests pass, verify production system is operational, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at phase boundaries
- Property tests validate universal correctness properties (16 properties total)
- Unit tests validate specific examples and edge cases
- Integration tests validate component interactions
- All code must include type hints and Google-style docstrings
- Follow SOLID principles throughout implementation
- Maintain backward compatibility during transformation
- Production infrastructure (Docker, Render, PostgreSQL) must remain functional
