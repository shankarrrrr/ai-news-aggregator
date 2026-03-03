#!/usr/bin/env python3
"""
Seed database with categories and sources for the Competitive Exam Intelligence System.
"""
from dotenv import load_dotenv
load_dotenv()

from app.database.repositories.category_repository import CategoryRepository
from app.database.repositories.source_repository import SourceRepository
from app.database.models import Category, Source, SourceType
from app.config import EXAM_CATEGORIES, PIB_BASE_URL, GOVERNMENT_SCHEME_PORTALS

def seed_categories():
    """Seed the database with exam categories."""
    print('Seeding categories...')
    category_repo = CategoryRepository()
    
    for category_name in EXAM_CATEGORIES:
        try:
            existing = category_repo.find_by_name(category_name)
            if not existing:
                category = Category(
                    name=category_name,
                    description=f'Articles related to {category_name} for competitive exams'
                )
                category_repo.create(category)
                print(f'✓ Created category: {category_name}')
            else:
                print(f'- Category already exists: {category_name}')
        except Exception as e:
            print(f'✗ Failed to create category {category_name}: {e}')

def seed_youtube_sources():
    """Seed the database with YouTube channel sources."""
    print('Seeding YouTube sources...')
    source_repo = SourceRepository()
    
    youtube_channels = {
        'UCYRBFLkuZ8ZAfwz7ayGGvZQ': 'StudyIQ IAS',
        'UCnvC2wLZOiKdFkM8Ml4EzQg': 'Drishti IAS',
        'UCZ8QY-RF48rE3LJRgdD0kVQ': 'Vision IAS',
        'UCawZsQWqfGSbCI5yjkdVkTA': 'OnlyIAS',
        'UCOEVlIHEsILuTV_Ix8dDW5A': 'Insights IAS',
        'UC3cBGxYNVQURTNdvIjn05pA': 'PIB India Official',
        'UCawZsQWqfGSbCI5yjkdVkTC': 'Sansad TV',
        'UCawZsQWqfGSbCI5yjkdVkTD': 'Vajiram & Ravi',
        'UCawZsQWqfGSbCI5yjkdVkTE': 'Adda247',
        'UCawZsQWqfGSbCI5yjkdVkTF': 'BYJU\'s Exam Prep',
        'UCawZsQWqfGSbCI5yjkdVkTG': 'Unacademy UPSC'
    }

    for channel_id, channel_name in youtube_channels.items():
        try:
            channel_url = f'https://www.youtube.com/channel/{channel_id}'
            existing = source_repo.find_by_url(channel_url)
            if not existing:
                source = Source(
                    name=channel_name,
                    source_type=SourceType.YOUTUBE,
                    url=channel_url,
                    is_active=True,
                    source_metadata=f'{{"channel_id": "{channel_id}"}}'
                )
                source_repo.create(source)
                print(f'✓ Created YouTube source: {channel_name}')
            else:
                print(f'- YouTube source already exists: {channel_name}')
        except Exception as e:
            print(f'✗ Failed to create YouTube source {channel_name}: {e}')

def seed_pib_source():
    """Seed the database with PIB source."""
    print('Seeding PIB source...')
    source_repo = SourceRepository()
    
    try:
        existing = source_repo.find_by_url(PIB_BASE_URL)
        if not existing:
            source = Source(
                name='Press Information Bureau',
                source_type=SourceType.PIB,
                url=PIB_BASE_URL,
                is_active=True,
                source_metadata='{"categories": ["Government Policies", "Economy", "Defence", "International Relations", "Science & Technology", "Environment", "Social Welfare"]}'
            )
            source_repo.create(source)
            print('✓ Created PIB source')
        else:
            print('- PIB source already exists')
    except Exception as e:
        print(f'✗ Failed to create PIB source: {e}')

def seed_government_schemes_sources():
    """Seed the database with Government Schemes sources."""
    print('Seeding Government Schemes sources...')
    source_repo = SourceRepository()
    
    for portal in GOVERNMENT_SCHEME_PORTALS:
        try:
            portal_name = portal['name']
            portal_url = portal['url']
            portal_description = portal.get('description', '')
            
            existing = source_repo.find_by_url(portal_url)
            if not existing:
                source = Source(
                    name=f'Government Schemes - {portal_name}',
                    source_type=SourceType.GOVERNMENT_SCHEMES,
                    url=portal_url,
                    is_active=True,
                    source_metadata=f'{{"portal_name": "{portal_name}", "description": "{portal_description}"}}'
                )
                source_repo.create(source)
                print(f'✓ Created Government Schemes source: {portal_name}')
            else:
                print(f'- Government Schemes source already exists: {portal_name}')
        except Exception as e:
            print(f'✗ Failed to create Government Schemes source {portal_name}: {e}')

def main():
    """Main seeding function."""
    print('🌱 Starting database seeding...')
    
    seed_categories()
    seed_youtube_sources()
    seed_pib_source()
    seed_government_schemes_sources()
    
    print('✅ Database seeding completed!')

if __name__ == "__main__":
    main()