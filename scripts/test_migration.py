#!/usr/bin/env python3
"""
Test script for database migration functionality.

This script tests the migration module structure without requiring
a database connection.
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_migration_structure():
    """Test that migration module has correct structure."""
    try:
        # Import the migration module
        from app.database.migrations import transform_to_exam_system as migration
        
        # Check that required classes and functions exist
        assert hasattr(migration, 'DatabaseMigration'), "DatabaseMigration class not found"
        assert hasattr(migration, 'run_migration'), "run_migration function not found"
        assert hasattr(migration, 'rollback_migration'), "rollback_migration function not found"
        
        # Check DatabaseMigration methods
        migration_methods = [
            'execute_migration', 'rollback_migration', 'verify_migration'
        ]
        
        for method in migration_methods:
            assert hasattr(migration.DatabaseMigration, method), f"Method {method} not found in DatabaseMigration"
        
        # Check constants exist
        assert hasattr(migration, 'EXAM_CATEGORIES'), "EXAM_CATEGORIES not found"
        assert hasattr(migration, 'CONTENT_SOURCES'), "CONTENT_SOURCES not found"
        
        # Validate exam categories
        categories = migration.EXAM_CATEGORIES
        assert len(categories) == 8, f"Expected 8 categories, got {len(categories)}"
        
        required_category_keys = ['name', 'description', 'priority']
        for category in categories:
            for key in required_category_keys:
                assert key in category, f"Category missing key: {key}"
        
        # Validate content sources
        sources = migration.CONTENT_SOURCES
        assert len(sources) == 3, f"Expected 3 sources, got {len(sources)}"
        
        required_source_keys = ['name', 'source_type', 'base_url', 'is_active', 'description']
        for source in sources:
            for key in required_source_keys:
                assert key in source, f"Source missing key: {key}"
        
        print("✅ Migration module structure is correct")
        print(f"   - {len(categories)} exam categories defined")
        print(f"   - {len(sources)} content sources defined")
        print("   - All required methods present")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Structure error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_migration_runner_structure():
    """Test that migration runner has correct structure."""
    try:
        # Import the runner module
        from scripts import run_migration
        
        # Check that required functions exist
        runner_functions = [
            'setup_logging', 'check_prerequisites', 'backup_verification',
            'run_production_migration', 'run_production_rollback', 
            'verify_migration_status', 'main'
        ]
        
        for func in runner_functions:
            assert hasattr(run_migration, func), f"Function {func} not found in migration runner"
        
        print("✅ Migration runner structure is correct")
        print("   - All required functions present")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Structure error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_exam_categories():
    """Test exam categories configuration."""
    try:
        from app.database.migrations.transform_to_exam_system import EXAM_CATEGORIES
        
        expected_categories = [
            'Polity', 'Economy', 'International Relations', 'Science & Tech',
            'Environment & Ecology', 'Defence & Security', 'Government Schemes', 'Social Issues'
        ]
        
        actual_categories = [cat['name'] for cat in EXAM_CATEGORIES]
        
        for expected in expected_categories:
            assert expected in actual_categories, f"Missing category: {expected}"
        
        print("✅ Exam categories configuration is correct")
        print(f"   - Categories: {', '.join(actual_categories)}")
        return True
        
    except Exception as e:
        print(f"❌ Exam categories test failed: {e}")
        return False

def test_content_sources():
    """Test content sources configuration."""
    try:
        from app.database.migrations.transform_to_exam_system import CONTENT_SOURCES
        
        expected_source_types = ['youtube', 'pib', 'government_schemes']
        actual_source_types = [source['source_type'] for source in CONTENT_SOURCES]
        
        for expected in expected_source_types:
            assert expected in actual_source_types, f"Missing source type: {expected}"
        
        print("✅ Content sources configuration is correct")
        print(f"   - Source types: {', '.join(actual_source_types)}")
        return True
        
    except Exception as e:
        print(f"❌ Content sources test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing database migration functionality...")
    
    tests = [
        ("Migration Structure", test_migration_structure),
        ("Migration Runner Structure", test_migration_runner_structure),
        ("Exam Categories", test_exam_categories),
        ("Content Sources", test_content_sources)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
    
    print(f"\n🏁 Migration Tests: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All migration tests passed!")
        sys.exit(0)
    else:
        print("💥 Some migration tests failed!")
        sys.exit(1)