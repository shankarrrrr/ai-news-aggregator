"""
Quick test script to verify Gemini integration works
"""
import os
from dotenv import load_dotenv
from app.agent.digest_agent import DigestAgent
from app.agent.curator_agent import CuratorAgent
from app.agent.email_agent import EmailAgent
from app.profiles.user_profile import USER_PROFILE

load_dotenv()

def test_digest_agent():
    print("\n=== Testing Digest Agent ===")
    agent = DigestAgent()
    
    test_content = """
    Google has announced a new breakthrough in AI reasoning with their latest model.
    The model shows significant improvements in mathematical problem-solving and code generation.
    This represents a major step forward in AI capabilities.
    """
    
    result = agent.generate_digest(
        title="Google Announces New AI Model",
        content=test_content,
        article_type="blog_post"
    )
    
    if result:
        print(f"✓ Title: {result.title}")
        print(f"✓ Summary: {result.summary}")
        return True
    else:
        print("✗ Failed to generate digest")
        return False

def test_curator_agent():
    print("\n=== Testing Curator Agent ===")
    agent = CuratorAgent(USER_PROFILE)
    
    test_digests = [
        {
            "id": "blog:1",
            "title": "New Advances in Large Language Models",
            "summary": "Recent research shows improvements in LLM reasoning capabilities.",
            "article_type": "blog_post"
        },
        {
            "id": "youtube:2",
            "title": "How to Build a Chatbot",
            "summary": "Tutorial on building chatbots with Python.",
            "article_type": "youtube_video"
        },
        {
            "id": "blog:3",
            "title": "AI Safety Research Update",
            "summary": "Latest developments in AI alignment and safety.",
            "article_type": "blog_post"
        }
    ]
    
    results = agent.rank_digests(test_digests)
    
    if results:
        print(f"✓ Ranked {len(results)} articles:")
        for article in results:
            print(f"  Rank {article.rank}: {article.digest_id} (Score: {article.relevance_score:.1f}/10)")
            print(f"    Reasoning: {article.reasoning}")
        return True
    else:
        print("✗ Failed to rank digests")
        return False

def test_email_agent():
    print("\n=== Testing Email Agent ===")
    agent = EmailAgent(USER_PROFILE)
    
    test_articles = [
        type('Article', (), {
            'title': 'New AI Model Released',
            'relevance_score': 9.5
        })(),
        type('Article', (), {
            'title': 'AI Safety Research',
            'relevance_score': 8.7
        })(),
    ]
    
    intro = agent.generate_introduction(test_articles)
    
    if intro:
        print(f"✓ Greeting: {intro.greeting}")
        print(f"✓ Introduction: {intro.introduction}")
        return True
    else:
        print("✗ Failed to generate introduction")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Gemini Integration")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Digest Agent", test_digest_agent()))
    except Exception as e:
        print(f"✗ Digest Agent error: {e}")
        results.append(("Digest Agent", False))
    
    try:
        results.append(("Curator Agent", test_curator_agent()))
    except Exception as e:
        print(f"✗ Curator Agent error: {e}")
        results.append(("Curator Agent", False))
    
    try:
        results.append(("Email Agent", test_email_agent()))
    except Exception as e:
        print(f"✗ Email Agent error: {e}")
        results.append(("Email Agent", False))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Gemini integration is working correctly.")
        print("\nNext steps:")
        print("1. Install Docker Desktop for Windows")
        print("2. Start PostgreSQL: cd docker && docker-compose up -d")
        print("3. Initialize database: python -c \"from app.database.create_tables import create_tables; create_tables()\"")
        print("4. Run full pipeline: python scripts/run_pipeline.py 24 10 --no-email")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
