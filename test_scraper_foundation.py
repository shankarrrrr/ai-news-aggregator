"""
Test script to verify scraper foundation implementation.

This script tests Phase 1 and Phase 2 implementations:
- Abstract base classes (AbstractScraper, AbstractAgent, AbstractRankingStrategy)
- Concrete scraper implementations (YouTube, PIB, GovernmentSchemes)
- Scraper factory pattern
- Configuration management
"""

import sys
from datetime import datetime, timezone


def test_abstract_base_classes():
    """Test that all abstract base classes are properly defined."""
    print("\n=== Testing Abstract Base Classes ===")
    
    try:
        from app.scrapers.abstract_scraper import AbstractScraper, ScrapedContent, ScraperException
        print("✓ AbstractScraper imported successfully")
        
        # Verify ScrapedContent model
        test_content = ScrapedContent(
            title="Test Article",
            content="This is test content with more than 50 characters to pass validation.",
            url="https://example.com/test",
            published_at=datetime.now(timezone.utc),
            source_type="test",
            metadata={"key": "value"}
        )
        print("✓ ScrapedContent model works correctly")
        
    except Exception as e:
        print(f"✗ AbstractScraper test failed: {e}")
        return False
    
    try:
        from app.agent.abstract_agent import AbstractAgent, AgentConfig, AgentException
        print("✓ AbstractAgent imported successfully")
        
    except Exception as e:
        print(f"✗ AbstractAgent test failed: {e}")
        return False
    
    try:
        from app.services.ranking.abstract_ranking_strategy import (
            AbstractRankingStrategy, ArticleMetadata, RankingResult
        )
        print("✓ AbstractRankingStrategy imported successfully")
        
        # Verify ArticleMetadata model
        test_metadata = ArticleMetadata(
            category="Polity",
            source_type="youtube",
            published_at=datetime.now(timezone.utc),
            content_length=500,
            keywords=["test", "keyword"]
        )
        print("✓ ArticleMetadata model works correctly")
        
    except Exception as e:
        print(f"✗ AbstractRankingStrategy test failed: {e}")
        return False
    
    return True


def test_concrete_scrapers():
    """Test that all concrete scraper implementations exist."""
    print("\n=== Testing Concrete Scraper Implementations ===")
    
    try:
        from app.scrapers.youtube_scraper import YouTubeScraper
        scraper = YouTubeScraper()
        print(f"✓ YouTubeScraper instantiated: {scraper.source_name}")
        print(f"  - Configured channels: {len(scraper._channel_ids)}")
        
    except Exception as e:
        print(f"✗ YouTubeScraper test failed: {e}")
        return False
    
    try:
        from app.scrapers.pib_scraper import PIBScraper
        scraper = PIBScraper()
        print(f"✓ PIBScraper instantiated: {scraper.source_name}")
        print(f"  - Configured categories: {len(scraper._categories)}")
        
    except Exception as e:
        print(f"✗ PIBScraper test failed: {e}")
        return False
    
    try:
        from app.scrapers.government_schemes_scraper import GovernmentSchemesScraper
        scraper = GovernmentSchemesScraper()
        print(f"✓ GovernmentSchemesScraper instantiated: {scraper.source_name}")
        print(f"  - Configured portals: {len(scraper._portals)}")
        
    except Exception as e:
        print(f"✗ GovernmentSchemesScraper test failed: {e}")
        return False
    
    return True


def test_scraper_factory():
    """Test the scraper factory pattern implementation."""
    print("\n=== Testing Scraper Factory Pattern ===")
    
    try:
        from app.scrapers.scraper_factory import ScraperFactory, SourceType
        
        # Test get_available_sources
        sources = ScraperFactory.get_available_sources()
        print(f"✓ Available sources: {[s.value for s in sources]}")
        
        if len(sources) != 3:
            print(f"✗ Expected 3 sources, got {len(sources)}")
            return False
        
        # Test create_scraper for each source type
        for source_type in sources:
            scraper = ScraperFactory.create_scraper(source_type)
            print(f"✓ Created {source_type.value} scraper: {scraper.source_name}")
        
        # Test create_all_scrapers
        all_scrapers = ScraperFactory.create_all_scrapers()
        print(f"✓ Created all scrapers: {len(all_scrapers)} total")
        
        if len(all_scrapers) != 3:
            print(f"✗ Expected 3 scrapers, got {len(all_scrapers)}")
            return False
        
    except Exception as e:
        print(f"✗ ScraperFactory test failed: {e}")
        return False
    
    return True


def test_configuration():
    """Test configuration management."""
    print("\n=== Testing Configuration Management ===")
    
    try:
        from app.config import (
            EXAM_CATEGORIES, YOUTUBE_CHANNELS, PIB_CATEGORIES,
            GOVERNMENT_SCHEME_PORTALS, UPSC_RANKING_WEIGHTS,
            SSC_RANKING_WEIGHTS, BANKING_RANKING_WEIGHTS,
            get_configuration_summary
        )
        
        # Test exam categories
        print(f"✓ Exam categories configured: {len(EXAM_CATEGORIES)}")
        if len(EXAM_CATEGORIES) != 8:
            print(f"✗ Expected 8 categories, got {len(EXAM_CATEGORIES)}")
            return False
        
        # Test YouTube channels
        print(f"✓ YouTube channels configured: {len(YOUTUBE_CHANNELS)}")
        if len(YOUTUBE_CHANNELS) != 11:
            print(f"✗ Expected 11 channels, got {len(YOUTUBE_CHANNELS)}")
            return False
        
        # Test PIB categories
        print(f"✓ PIB categories configured: {len(PIB_CATEGORIES)}")
        
        # Test government portals
        print(f"✓ Government portals configured: {len(GOVERNMENT_SCHEME_PORTALS)}")
        
        # Test ranking weights sum to 1.0
        for exam_type, weights in [
            ("UPSC", UPSC_RANKING_WEIGHTS),
            ("SSC", SSC_RANKING_WEIGHTS),
            ("Banking", BANKING_RANKING_WEIGHTS)
        ]:
            total = sum(weights.values())
            if 0.99 <= total <= 1.01:
                print(f"✓ {exam_type} ranking weights sum to {total:.2f}")
            else:
                print(f"✗ {exam_type} ranking weights sum to {total:.2f} (expected 1.0)")
                return False
        
        # Test configuration summary
        summary = get_configuration_summary()
        print(f"✓ Configuration summary generated: {len(summary)} fields")
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False
    
    return True


def test_liskov_substitution():
    """Test Liskov Substitution Principle for scrapers."""
    print("\n=== Testing Liskov Substitution Principle ===")
    
    try:
        from app.scrapers.abstract_scraper import AbstractScraper
        from app.scrapers.scraper_factory import ScraperFactory
        
        # Create all scrapers
        scrapers = ScraperFactory.create_all_scrapers()
        
        # Test that all scrapers are substitutable for AbstractScraper
        for scraper in scrapers:
            if not isinstance(scraper, AbstractScraper):
                print(f"✗ {scraper.__class__.__name__} is not an AbstractScraper")
                return False
            
            # Test that all scrapers have the required interface
            if not hasattr(scraper, 'scrape'):
                print(f"✗ {scraper.__class__.__name__} missing scrape() method")
                return False
            
            if not hasattr(scraper, 'validate_content'):
                print(f"✗ {scraper.__class__.__name__} missing validate_content() method")
                return False
            
            print(f"✓ {scraper.__class__.__name__} is substitutable for AbstractScraper")
        
    except Exception as e:
        print(f"✗ Liskov Substitution test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("Scraper Foundation Verification")
    print("Testing Phase 1 and Phase 2 Implementations")
    print("=" * 70)
    
    results = []
    
    # Run all tests
    tests = [
        ("Abstract Base Classes", test_abstract_base_classes),
        ("Concrete Scrapers", test_concrete_scrapers),
        ("Scraper Factory", test_scraper_factory),
        ("Configuration", test_configuration),
        ("Liskov Substitution", test_liskov_substitution),
    ]
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 All tests passed! Scraper foundation is solid.")
        print("\nPhase 1 (Foundation) - COMPLETE:")
        print("  ✓ AbstractScraper base class")
        print("  ✓ AbstractAgent base class")
        print("  ✓ AbstractRankingStrategy base class")
        print("  ✓ Configuration management")
        print("\nPhase 2 (Scrapers) - COMPLETE:")
        print("  ✓ YouTubeScraper implementation")
        print("  ✓ PIBScraper implementation")
        print("  ✓ GovernmentSchemesScraper implementation")
        print("  ✓ ScraperFactory with registry pattern")
        print("\nNext Steps:")
        print("  → Proceed to Phase 3: Agent Implementations")
        print("  → Implement CategorizationAgent")
        print("  → Implement SummarizationAgent")
        print("  → Implement RankingAgent")
        print("  → Implement DigestAgent")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
