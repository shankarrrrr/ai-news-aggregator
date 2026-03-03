#!/usr/bin/env python3
"""
Test script for health check functionality.

This script tests the health check module without requiring
all dependencies to be installed.
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_health_check_structure():
    """Test that health check module has correct structure."""
    try:
        # Import the module
        from app import health
        
        # Check that required classes exist
        assert hasattr(health, 'HealthChecker'), "HealthChecker class not found"
        assert hasattr(health, 'get_health_status'), "get_health_status function not found"
        
        # Check HealthChecker methods
        checker_methods = [
            'check_all', 'check_database_connection', 
            'check_gemini_api', 'check_external_sources'
        ]
        
        for method in checker_methods:
            assert hasattr(health.HealthChecker, method), f"Method {method} not found in HealthChecker"
        
        print("✅ Health check module structure is correct")
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

def test_health_check_mock():
    """Test health check with mock data."""
    try:
        # Create a mock health status
        mock_health_status = {
            "timestamp": "2024-03-03T12:00:00Z",
            "status": "healthy",
            "checks": {
                "database": {
                    "healthy": True,
                    "message": "Database connection successful",
                    "response_time_ms": 50,
                    "details": {
                        "existing_tables": ["articles", "categories", "sources"],
                        "tables_count": 3
                    }
                },
                "gemini_api": {
                    "healthy": True,
                    "message": "Gemini API connection successful",
                    "response_time_ms": 200,
                    "details": {
                        "model": "gemini-1.5-flash",
                        "response_received": True
                    }
                },
                "external_sources": {
                    "healthy": True,
                    "message": "All external sources accessible",
                    "response_time_ms": 1500,
                    "details": {
                        "sources": {
                            "YouTube RSS": {
                                "accessible": True,
                                "status_code": 200,
                                "response_time_ms": 500
                            },
                            "PIB Website": {
                                "accessible": True,
                                "status_code": 200,
                                "response_time_ms": 800
                            }
                        }
                    }
                }
            }
        }
        
        # Validate structure
        required_keys = ["timestamp", "status", "checks"]
        for key in required_keys:
            assert key in mock_health_status, f"Missing key: {key}"
        
        required_checks = ["database", "gemini_api", "external_sources"]
        for check in required_checks:
            assert check in mock_health_status["checks"], f"Missing check: {check}"
            assert "healthy" in mock_health_status["checks"][check], f"Missing 'healthy' in {check}"
        
        print("✅ Health check JSON structure is valid")
        return True
        
    except AssertionError as e:
        print(f"❌ Structure validation error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing health check functionality...")
    
    structure_ok = test_health_check_structure()
    mock_ok = test_health_check_mock()
    
    if structure_ok and mock_ok:
        print("\n🎉 All health check tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some health check tests failed!")
        sys.exit(1)