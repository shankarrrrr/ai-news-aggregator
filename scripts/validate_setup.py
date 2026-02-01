#!/usr/bin/env python3
"""
Validation script to ensure Gemini migration is complete and working.
Run this before deploying to production.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def print_status(test_name, passed, message=""):
    status = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {test_name}")
    if message:
        print(f"  {message}")
    return passed

def test_no_openai_imports():
    """Ensure no OpenAI API imports remain."""
    import subprocess
    result = subprocess.run(
        ["grep", "-r", "from openai import OpenAI", "app/"],
        capture_output=True,
        text=True
    )
    return print_status(
        "No OpenAI API imports",
        result.returncode != 0,
        "OpenAI API has been fully removed" if result.returncode != 0 else "Found OpenAI imports!"
    )

def test_gemini_api_key():
    """Check if Gemini API key is set."""
    key = os.getenv("GEMINI_API_KEY")
    return print_status(
        "Gemini API key configured",
        bool(key),
        f"Key found: {key[:10]}..." if key else "GEMINI_API_KEY not set in environment"
    )

def test_gemini_connection():
    """Test Gemini API connection."""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return print_status("Gemini API connection", False, "No API key")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say 'OK'")
        
        return print_status(
            "Gemini API connection",
            bool(response and response.text),
            f"Response: {response.text[:30]}"
        )
    except Exception as e:
        return print_status("Gemini API connection", False, str(e))

def test_digest_agent():
    """Test DigestAgent with Gemini."""
    try:
        from app.agent.digest_agent import DigestAgent
        agent = DigestAgent()
        result = agent.generate_digest(
            title="Test Article",
            content="This is a test article about AI.",
            article_type="test"
        )
        return print_status(
            "Digest Agent",
            result is not None and hasattr(result, 'title'),
            f"Generated: {result.title[:40]}..." if result else "Failed"
        )
    except Exception as e:
        return print_status("Digest Agent", False, str(e))

def test_curator_agent():
    """Test CuratorAgent with Gemini."""
    try:
        from app.agent.curator_agent import CuratorAgent
        from app.profiles.user_profile import USER_PROFILE
        
        agent = CuratorAgent(USER_PROFILE)
        digests = [
            {
                'id': 'test:1',
                'title': 'Test Article',
                'summary': 'Test summary',
                'article_type': 'test'
            }
        ]
        result = agent.rank_digests(digests)
        return print_status(
            "Curator Agent",
            len(result) > 0,
            f"Ranked {len(result)} articles" if result else "Failed"
        )
    except Exception as e:
        return print_status("Curator Agent", False, str(e))

def test_email_agent():
    """Test EmailAgent with Gemini."""
    try:
        from app.agent.email_agent import EmailAgent, RankedArticleDetail
        from app.profiles.user_profile import USER_PROFILE
        
        agent = EmailAgent(USER_PROFILE)
        articles = [
            RankedArticleDetail(
                digest_id='test:1',
                rank=1,
                relevance_score=8.5,
                title='Test',
                summary='Test',
                url='https://example.com',
                article_type='test',
                reasoning='Test'
            )
        ]
        result = agent.generate_introduction(articles)
        return print_status(
            "Email Agent",
            result is not None and hasattr(result, 'greeting'),
            f"Generated: {result.greeting[:40]}..." if result else "Failed"
        )
    except Exception as e:
        return print_status("Email Agent", False, str(e))

def test_database_connection():
    """Test database connection."""
    try:
        from app.database.connection import get_engine
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return print_status(
            "Database connection",
            True,
            "Connected successfully"
        )
    except Exception as e:
        return print_status("Database connection", False, str(e))

def test_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import google.generativeai
        import sqlalchemy
        import pydantic
        import feedparser
        import requests
        return print_status(
            "Dependencies installed",
            True,
            "All required packages found"
        )
    except ImportError as e:
        return print_status("Dependencies installed", False, str(e))

def main():
    print("=" * 60)
    print("🔍 Validating Gemini Migration")
    print("=" * 60)
    print()
    
    results = []
    
    # Run all tests
    results.append(test_dependencies())
    results.append(test_no_openai_imports())
    results.append(test_gemini_api_key())
    results.append(test_gemini_connection())
    results.append(test_digest_agent())
    results.append(test_curator_agent())
    results.append(test_email_agent())
    results.append(test_database_connection())
    
    print()
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All {total} tests passed! Ready for deployment.")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"✗ {total - passed} of {total} tests failed.")
        print("=" * 60)
        print("\nFix the failing tests before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
