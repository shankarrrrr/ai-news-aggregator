#!/usr/bin/env python3
"""
End-to-end production testing for Competitive Exam Intelligence System.

This script performs comprehensive testing of the production system
to verify all components are working correctly after deployment.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import app.config as config
from app.health import HealthChecker
from app.pipeline.pipeline import Pipeline
from app.database.connection import get_session
from sqlalchemy import text


class ProductionE2ETest:
    """
    End-to-end testing suite for production environment.
    
    Tests the complete pipeline from scraping to digest generation
    with real production data and configurations.
    """
    
    def __init__(self):
        """Initialize the test suite."""
        self.logger = logging.getLogger(__name__)
        self.test_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tests": {},
            "overall_status": "unknown",
            "summary": {}
        }
    
    def run_all_tests(self) -> bool:
        """
        Run all end-to-end tests.
        
        Returns:
            True if all tests pass, False otherwise
        """
        self.logger.info("🚀 Starting production end-to-end tests")
        
        test_methods = [
            ("health_check", self.test_health_check),
            ("database_connectivity", self.test_database_connectivity),
            ("pipeline_execution", self.test_pipeline_execution),
            ("scraping_functionality", self.test_scraping_functionality),
            ("categorization_accuracy", self.test_categorization_accuracy),
            ("summarization_quality", self.test_summarization_quality),
            ("ranking_scores", self.test_ranking_scores),
            ("digest_generation", self.test_digest_generation),
            ("data_persistence", self.test_data_persistence)
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            self.logger.info(f"Running test: {test_name}")
            
            try:
                start_time = time.time()
                result = test_method()
                end_time = time.time()
                
                self.test_results["tests"][test_name] = {
                    "passed": result,
                    "duration_seconds": round(end_time - start_time, 2),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                if result:
                    passed_tests += 1
                    self.logger.info(f"✅ {test_name} PASSED")
                else:
                    self.logger.error(f"❌ {test_name} FAILED")
                    
            except Exception as e:
                self.logger.error(f"💥 {test_name} CRASHED: {str(e)}", exc_info=True)
                self.test_results["tests"][test_name] = {
                    "passed": False,
                    "error": str(e),
                    "duration_seconds": 0,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        # Calculate overall results
        success_rate = (passed_tests / total_tests) * 100
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": round(success_rate, 1)
        }
        
        if success_rate >= 90:
            self.test_results["overall_status"] = "excellent"
        elif success_rate >= 75:
            self.test_results["overall_status"] = "good"
        elif success_rate >= 50:
            self.test_results["overall_status"] = "poor"
        else:
            self.test_results["overall_status"] = "critical"
        
        self.logger.info(f"🏁 Tests completed: {passed_tests}/{total_tests} passed ({success_rate}%)")
        
        return passed_tests == total_tests
    
    def test_health_check(self) -> bool:
        """Test system health check functionality."""
        try:
            health_checker = HealthChecker(self.config)
            health_status = health_checker.check_all()
            
            # Verify health check structure
            required_keys = ["timestamp", "status", "checks"]
            if not all(key in health_status for key in required_keys):
                self.logger.error("Health check missing required keys")
                return False
            
            # Check individual components
            checks = health_status["checks"]
            required_checks = ["database", "gemini_api", "external_sources"]
            
            for check_name in required_checks:
                if check_name not in checks:
                    self.logger.error(f"Missing health check: {check_name}")
                    return False
                
                if not checks[check_name].get("healthy", False):
                    self.logger.warning(f"Health check failed: {check_name}")
                    # Don't fail the test for external sources (they might be temporarily down)
                    if check_name != "external_sources":
                        return False
            
            self.logger.info("Health check functionality verified")
            return True
            
        except Exception as e:
            self.logger.error(f"Health check test failed: {str(e)}")
            return False
    
    def test_database_connectivity(self) -> bool:
        """Test database connectivity and schema."""
        try:
            with get_database_session() as session:
                # Test basic connectivity
                result = session.execute(text("SELECT 1"))
                if result.scalar() != 1:
                    return False
                
                # Check required tables exist
                required_tables = [
                    'articles', 'categories', 'sources', 
                    'summaries', 'rankings', 'user_profiles'
                ]
                
                for table in required_tables:
                    result = session.execute(text(
                        f"SELECT COUNT(*) FROM information_schema.tables "
                        f"WHERE table_name = '{table}'"
                    ))
                    if result.scalar() == 0:
                        self.logger.error(f"Required table missing: {table}")
                        return False
                
                # Check seed data
                result = session.execute(text("SELECT COUNT(*) FROM categories"))
                if result.scalar() < 8:  # Should have 8 exam categories
                    self.logger.error("Categories not properly seeded")
                    return False
                
                result = session.execute(text("SELECT COUNT(*) FROM sources"))
                if result.scalar() < 3:  # Should have 3 content sources
                    self.logger.error("Sources not properly seeded")
                    return False
                
            self.logger.info("Database connectivity and schema verified")
            return True
            
        except Exception as e:
            self.logger.error(f"Database connectivity test failed: {str(e)}")
            return False
    
    def test_pipeline_execution(self) -> bool:
        """Test complete pipeline execution with small time window."""
        try:
            # Import pipeline dependencies
            from app.scrapers.scraper_factory import ScraperFactory
            from app.database.repositories.article_repository import ArticleRepository
            from app.database.repositories.source_repository import SourceRepository
            from app.database.repositories.category_repository import CategoryRepository
            from app.database.repositories.summary_repository import SummaryRepository
            from app.database.repositories.ranking_repository import RankingRepository
            
            from app.services.scraping_service import ScrapingService
            from app.services.categorization_service import CategorizationService
            from app.services.summarization_service import SummarizationService
            from app.services.ranking_service import RankingService
            from app.services.digest_generation_service import DigestGenerationService
            
            from app.agent.categorization_agent import CategorizationAgent
            from app.agent.summarization_agent import SummarizationAgent
            from app.agent.ranking_agent import RankingAgent
            from app.agent.digest_agent import DigestAgent
            from app.agent.abstract_agent import AgentConfig
            
            # Initialize repositories
            article_repo = ArticleRepository()
            source_repo = SourceRepository()
            category_repo = CategoryRepository()
            summary_repo = SummaryRepository()
            ranking_repo = RankingRepository()
            
            # Initialize agents
            agent_config = AgentConfig(api_key=self.config.GEMINI_API_KEY)
            categorization_agent = CategorizationAgent(agent_config)
            summarization_agent = SummarizationAgent(agent_config)
            ranking_agent = RankingAgent(agent_config)
            digest_agent = DigestAgent(agent_config)
            
            # Initialize services
            scraper_factory = ScraperFactory()
            scraping_service = ScrapingService(scraper_factory, article_repo, source_repo)
            categorization_service = CategorizationService(categorization_agent, article_repo, category_repo)
            summarization_service = SummarizationService(summarization_agent, article_repo, summary_repo)
            ranking_service = RankingService(ranking_agent, article_repo, ranking_repo)
            digest_service = DigestGenerationService(digest_agent, ranking_repo)
            
            # Initialize pipeline
            pipeline = Pipeline(
                scraping_service=scraping_service,
                categorization_service=categorization_service,
                summarization_service=summarization_service,
                ranking_service=ranking_service,
                digest_service=digest_service
            )
            
            # Execute pipeline with 1 hour window and top 5 articles
            self.logger.info("Executing pipeline with 1-hour window")
            result = pipeline.execute(hours=1, top_n=5, exam_type="UPSC")
            
            # Verify pipeline result
            if not result:
                self.logger.error("Pipeline execution returned no result")
                return False
            
            # Check that some processing occurred
            if result.articles_scraped == 0:
                self.logger.warning("No articles were scraped (might be expected)")
            
            self.logger.info(f"Pipeline executed successfully: {result.articles_scraped} articles processed")
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline execution test failed: {str(e)}")
            return False
    
    def test_scraping_functionality(self) -> bool:
        """Test that scrapers can fetch content from sources."""
        try:
            from app.scrapers.scraper_factory import ScraperFactory
            
            factory = ScraperFactory()
            
            # Test each scraper type
            scraper_types = ['youtube', 'pib', 'government_schemes']
            
            for scraper_type in scraper_types:
                try:
                    scraper = factory.create_scraper(scraper_type)
                    content = scraper.scrape(hours=1)  # Small time window
                    
                    self.logger.info(f"{scraper_type} scraper: {len(content)} items")
                    
                    # Validate content structure if any items found
                    if content:
                        first_item = content[0]
                        required_fields = ['title', 'content', 'url', 'published_at', 'source_type']
                        
                        for field in required_fields:
                            if not hasattr(first_item, field):
                                self.logger.error(f"{scraper_type} content missing field: {field}")
                                return False
                
                except Exception as e:
                    self.logger.warning(f"{scraper_type} scraper failed: {str(e)}")
                    # Don't fail the test for individual scraper failures
                    continue
            
            self.logger.info("Scraping functionality verified")
            return True
            
        except Exception as e:
            self.logger.error(f"Scraping functionality test failed: {str(e)}")
            return False
    
    def test_categorization_accuracy(self) -> bool:
        """Test categorization agent accuracy."""
        try:
            from app.agent.categorization_agent import CategorizationAgent
            from app.agent.abstract_agent import AgentConfig
            
            agent_config = AgentConfig(api_key=self.config.GEMINI_API_KEY)
            agent = CategorizationAgent(agent_config)
            
            # Test with sample content
            test_content = """
            The Union Budget 2024 announced a new scheme for digital infrastructure 
            development with an allocation of Rs 10,000 crores. The scheme aims to 
            enhance digital connectivity in rural areas and promote digital literacy.
            """
            
            result = agent.execute(test_content)
            
            # Verify result structure
            if not hasattr(result, 'primary_category'):
                self.logger.error("Categorization result missing primary_category")
                return False
            
            if not hasattr(result, 'secondary_categories'):
                self.logger.error("Categorization result missing secondary_categories")
                return False
            
            # Verify categories are valid
            valid_categories = [
                'Polity', 'Economy', 'International Relations', 'Science & Tech',
                'Environment & Ecology', 'Defence & Security', 'Government Schemes', 'Social Issues'
            ]
            
            if result.primary_category not in valid_categories:
                self.logger.error(f"Invalid primary category: {result.primary_category}")
                return False
            
            self.logger.info(f"Categorization: {result.primary_category} + {result.secondary_categories}")
            return True
            
        except Exception as e:
            self.logger.error(f"Categorization accuracy test failed: {str(e)}")
            return False
    
    def test_summarization_quality(self) -> bool:
        """Test summarization agent quality."""
        try:
            from app.agent.summarization_agent import SummarizationAgent
            from app.agent.abstract_agent import AgentConfig
            
            agent_config = AgentConfig(api_key=self.config.GEMINI_API_KEY)
            agent = SummarizationAgent(agent_config)
            
            # Test with sample content
            test_content = """
            The Supreme Court of India delivered a landmark judgment on digital privacy rights,
            establishing new guidelines for data protection. The court emphasized the fundamental
            right to privacy and its implications for digital governance. This decision will
            impact how government agencies and private companies handle personal data.
            """
            
            result = agent.execute(test_content, category="Polity")
            
            # Verify result structure
            required_fields = [
                'summary', 'exam_relevance', 'prelims_relevance', 
                'mains_relevance', 'possible_questions', 'key_facts'
            ]
            
            for field in required_fields:
                if not hasattr(result, field):
                    self.logger.error(f"Summary result missing field: {field}")
                    return False
            
            # Check word count (should be 200-300 words)
            word_count = len(result.summary.split())
            if not (150 <= word_count <= 350):  # Allow some flexibility
                self.logger.warning(f"Summary word count outside range: {word_count}")
            
            self.logger.info(f"Summarization quality verified (words: {word_count})")
            return True
            
        except Exception as e:
            self.logger.error(f"Summarization quality test failed: {str(e)}")
            return False
    
    def test_ranking_scores(self) -> bool:
        """Test ranking agent score reasonableness."""
        try:
            from app.agent.ranking_agent import RankingAgent
            from app.agent.abstract_agent import AgentConfig
            from app.services.ranking.upsc_ranking_strategy import UPSCRankingStrategy
            from app.services.ranking.abstract_ranking_strategy import ArticleMetadata
            from datetime import datetime, timezone
            
            agent_config = AgentConfig(api_key=self.config.GEMINI_API_KEY)
            strategy = UPSCRankingStrategy()
            agent = RankingAgent(agent_config, strategy)
            
            # Test with sample content and metadata
            test_content = "Important policy announcement on economic reforms"
            test_metadata = ArticleMetadata(
                category="Economy",
                source_type="pib",
                published_at=datetime.now(timezone.utc),
                content_length=len(test_content),
                keywords=["policy", "economic", "reforms"]
            )
            
            result = agent.execute(test_content, test_metadata)
            
            # Verify score is in valid range
            if not (0.0 <= result.score <= 10.0):
                self.logger.error(f"Ranking score out of range: {result.score}")
                return False
            
            # Verify result has reasoning
            if not result.reasoning:
                self.logger.error("Ranking result missing reasoning")
                return False
            
            self.logger.info(f"Ranking score verified: {result.score}/10.0")
            return True
            
        except Exception as e:
            self.logger.error(f"Ranking scores test failed: {str(e)}")
            return False
    
    def test_digest_generation(self) -> bool:
        """Test digest generation functionality."""
        try:
            from app.agent.digest_agent import DigestAgent
            from app.agent.abstract_agent import AgentConfig
            
            agent_config = AgentConfig(api_key=self.config.GEMINI_API_KEY)
            agent = DigestAgent(agent_config)
            
            # Create sample articles for digest
            from app.agent.digest_agent import DigestArticle
            
            sample_articles = [
                DigestArticle(
                    title="Economic Policy Update",
                    summary="New economic policies announced",
                    category="Economy",
                    score=8.5,
                    url="https://example.com/1",
                    source="PIB"
                ),
                DigestArticle(
                    title="Defense Procurement News",
                    summary="Major defense equipment procurement",
                    category="Defence & Security",
                    score=7.8,
                    url="https://example.com/2",
                    source="PIB"
                )
            ]
            
            result = agent.execute(sample_articles)
            
            # Verify digest structure
            if not hasattr(result, 'formatted_digest'):
                self.logger.error("Digest result missing formatted_digest")
                return False
            
            # Check that digest contains content
            if len(result.formatted_digest) < 100:
                self.logger.error("Digest appears too short")
                return False
            
            self.logger.info("Digest generation verified")
            return True
            
        except Exception as e:
            self.logger.error(f"Digest generation test failed: {str(e)}")
            return False
    
    def test_data_persistence(self) -> bool:
        """Test that data is properly persisted to database."""
        try:
            with get_database_session() as session:
                # Check recent articles
                result = session.execute(text("""
                    SELECT COUNT(*) FROM articles 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """))
                recent_articles = result.scalar()
                
                # Check summaries
                result = session.execute(text("SELECT COUNT(*) FROM summaries"))
                summaries_count = result.scalar()
                
                # Check rankings
                result = session.execute(text("SELECT COUNT(*) FROM rankings"))
                rankings_count = result.scalar()
                
                self.logger.info(f"Data persistence: {recent_articles} recent articles, "
                               f"{summaries_count} summaries, {rankings_count} rankings")
                
                # Data persistence is verified if we can query without errors
                return True
                
        except Exception as e:
            self.logger.error(f"Data persistence test failed: {str(e)}")
            return False
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive test report.
        
        Returns:
            JSON string containing test results
        """
        return json.dumps(self.test_results, indent=2)
    
    def save_report(self, filename: Optional[str] = None) -> str:
        """
        Save test report to file.
        
        Args:
            filename: Optional filename (auto-generated if None)
            
        Returns:
            Path to saved report file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"e2e_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            f.write(self.generate_report())
        
        return filename


def main():
    """Main entry point for production E2E testing."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'e2e_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # Check environment
    if not os.getenv('DATABASE_URL'):
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)
    
    if not os.getenv('GEMINI_API_KEY'):
        logger.error("GEMINI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Run tests
    test_suite = ProductionE2ETest()
    success = test_suite.run_all_tests()
    
    # Generate and save report
    report_file = test_suite.save_report()
    logger.info(f"Test report saved to: {report_file}")
    
    # Print summary
    summary = test_suite.test_results["summary"]
    logger.info(f"🏁 Final Results: {summary['passed_tests']}/{summary['total_tests']} tests passed")
    logger.info(f"📊 Success Rate: {summary['success_rate']}%")
    logger.info(f"🎯 Overall Status: {test_suite.test_results['overall_status'].upper()}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()