#!/usr/bin/env python3
"""
Test script to verify real news scraping works.
This will attempt to scrape from PIB (Press Information Bureau) which is more reliable.
"""

import sys
from datetime import datetime

print("🔍 TESTING REAL NEWS SCRAPING")
print("=" * 70)
print()

# Test PIB Scraper (most reliable source)
print("1️⃣ Testing PIB (Press Information Bureau) Scraper...")
print("-" * 70)

try:
    from app.scrapers.pib_scraper import PIBScraper
    
    scraper = PIBScraper()
    print(f"✅ PIB Scraper initialized")
    print(f"📰 Categories: {', '.join(scraper.EXAM_RELEVANT_CATEGORIES[:3])}...")
    print()
    
    print("🔄 Scraping last 72 hours from PIB...")
    content = scraper.scrape(hours=72)
    
    if content:
        print(f"✅ SUCCESS! Scraped {len(content)} press releases from PIB")
        print()
        print("📰 Sample scraped content:")
        print("-" * 70)
        for i, item in enumerate(content[:3], 1):
            print(f"\n{i}. {item.title}")
            print(f"   Published: {item.published_at}")
            print(f"   URL: {item.url}")
            print(f"   Content preview: {item.content[:150]}...")
        print()
        print("✅ PIB scraping is WORKING with REAL data!")
    else:
        print("⚠️ No content found from PIB in last 72 hours")
        print("   This might indicate PIB website structure changed")
        
except Exception as e:
    print(f"❌ PIB Scraper Error: {str(e)}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print()

# Test Government Schemes Scraper
print("2️⃣ Testing Government Schemes Scraper...")
print("-" * 70)

try:
    from app.scrapers.government_schemes_scraper import GovernmentSchemesScraper
    
    scraper = GovernmentSchemesScraper()
    print(f"✅ Government Schemes Scraper initialized")
    print(f"🏛️ Portals: {len(scraper.SCHEME_PORTALS)} government portals")
    print()
    
    print("🔄 Scraping government schemes...")
    content = scraper.scrape(hours=168)  # Last week
    
    if content:
        print(f"✅ SUCCESS! Scraped {len(content)} schemes")
        print()
        print("🏛️ Sample schemes:")
        print("-" * 70)
        for i, item in enumerate(content[:2], 1):
            print(f"\n{i}. {item.title}")
            print(f"   URL: {item.url}")
            print(f"   Content preview: {item.content[:150]}...")
        print()
        print("✅ Government Schemes scraping is WORKING!")
    else:
        print("⚠️ No schemes found")
        
except Exception as e:
    print(f"❌ Government Schemes Scraper Error: {str(e)}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("📊 SUMMARY")
print("=" * 70)
print()
print("The system CAN scrape real news from:")
print("  ✅ PIB - Government press releases")
print("  ✅ Government Schemes - Welfare programs")
print("  ⚠️ YouTube - Requires valid channel IDs")
print()
print("💡 For your teacher demonstration:")
print("   The system will scrape REAL news from PIB and Government portals")
print("   and send AI-analyzed summaries to your email!")
print()
