#!/usr/bin/env python3
"""
Test script for monitoring and alerting functionality.

This script tests the monitoring module structure without requiring
all dependencies to be installed.
"""

import sys
import os
import json
from datetime import datetime, timezone

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_monitoring_structure():
    """Test that monitoring module has correct structure."""
    try:
        # Import the monitoring module
        from app.monitoring import alerting
        
        # Check that required classes exist
        assert hasattr(alerting, 'MonitoringSystem'), "MonitoringSystem class not found"
        assert hasattr(alerting, 'Alert'), "Alert class not found"
        assert hasattr(alerting, 'PipelineMetrics'), "PipelineMetrics class not found"
        assert hasattr(alerting, 'AlertLevel'), "AlertLevel enum not found"
        
        # Check MonitoringSystem methods
        monitoring_methods = [
            'start_pipeline_monitoring', 'update_pipeline_metrics', 
            'complete_pipeline_monitoring', 'log_api_latency',
            'log_slow_query', 'log_pipeline_error', 'log_pipeline_warning',
            'start_background_monitoring', 'stop_background_monitoring',
            'get_system_status', 'send_alert', 'add_alert_handler'
        ]
        
        for method in monitoring_methods:
            assert hasattr(alerting.MonitoringSystem, method), f"Method {method} not found in MonitoringSystem"
        
        # Check utility functions
        assert hasattr(alerting, 'get_monitoring_system'), "get_monitoring_system function not found"
        assert hasattr(alerting, 'monitor_api_call'), "monitor_api_call context manager not found"
        assert hasattr(alerting, 'monitor_database_query'), "monitor_database_query context manager not found"
        
        print("✅ Monitoring module structure is correct")
        print(f"   - {len(monitoring_methods)} monitoring methods defined")
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

def test_alert_levels():
    """Test alert level enumeration."""
    try:
        from app.monitoring.alerting import AlertLevel
        
        expected_levels = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level in expected_levels:
            assert hasattr(AlertLevel, level), f"Missing alert level: {level}"
        
        # Test enum values
        assert AlertLevel.INFO.value == "info"
        assert AlertLevel.WARNING.value == "warning"
        assert AlertLevel.ERROR.value == "error"
        assert AlertLevel.CRITICAL.value == "critical"
        
        print("✅ Alert levels are correctly defined")
        print(f"   - Levels: {', '.join(expected_levels)}")
        return True
        
    except Exception as e:
        print(f"❌ Alert levels test failed: {e}")
        return False

def test_pipeline_metrics():
    """Test pipeline metrics data structure."""
    try:
        from app.monitoring.alerting import PipelineMetrics
        
        # Create test metrics
        execution_id = "test_execution_123"
        start_time = datetime.now(timezone.utc)
        
        metrics = PipelineMetrics(
            execution_id=execution_id,
            start_time=start_time
        )
        
        # Test required attributes
        assert metrics.execution_id == execution_id
        assert metrics.start_time == start_time
        assert metrics.status == "running"
        assert metrics.articles_scraped == 0
        assert isinstance(metrics.errors, list)
        assert isinstance(metrics.warnings, list)
        
        # Test properties
        assert not metrics.is_completed  # Should be False for "running" status
        assert metrics.duration_seconds is None  # No end_time set
        
        # Test completion
        metrics.end_time = datetime.now(timezone.utc)
        metrics.status = "completed"
        assert metrics.is_completed
        assert metrics.duration_seconds is not None
        
        print("✅ Pipeline metrics structure is correct")
        print("   - All required attributes present")
        print("   - Properties work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline metrics test failed: {e}")
        return False

def test_alert_structure():
    """Test alert data structure."""
    try:
        from app.monitoring.alerting import Alert, AlertLevel
        
        # Create test alert
        alert = Alert(
            level=AlertLevel.WARNING,
            title="Test Alert",
            message="This is a test alert message",
            component="test_component",
            timestamp=datetime.now(timezone.utc),
            metadata={"test_key": "test_value"}
        )
        
        # Test required attributes
        assert alert.level == AlertLevel.WARNING
        assert alert.title == "Test Alert"
        assert alert.message == "This is a test alert message"
        assert alert.component == "test_component"
        assert isinstance(alert.timestamp, datetime)
        assert isinstance(alert.metadata, dict)
        assert alert.metadata["test_key"] == "test_value"
        
        # Test alert without metadata
        simple_alert = Alert(
            level=AlertLevel.INFO,
            title="Simple Alert",
            message="Simple message",
            component="simple_component",
            timestamp=datetime.now(timezone.utc)
        )
        
        assert isinstance(simple_alert.metadata, dict)
        assert len(simple_alert.metadata) == 0
        
        print("✅ Alert structure is correct")
        print("   - All required attributes present")
        print("   - Metadata handling works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Alert structure test failed: {e}")
        return False

def test_monitoring_thresholds():
    """Test monitoring performance thresholds."""
    try:
        from app.monitoring.alerting import MonitoringSystem
        
        # Create monitoring system instance
        monitoring = MonitoringSystem()
        
        # Check default thresholds exist
        expected_thresholds = [
            "api_call_timeout",
            "slow_query_timeout", 
            "pipeline_timeout",
            "max_error_rate"
        ]
        
        for threshold in expected_thresholds:
            assert threshold in monitoring.performance_thresholds, f"Missing threshold: {threshold}"
            assert isinstance(monitoring.performance_thresholds[threshold], (int, float)), f"Threshold {threshold} should be numeric"
        
        # Validate threshold values are reasonable
        assert monitoring.performance_thresholds["api_call_timeout"] > 0
        assert monitoring.performance_thresholds["slow_query_timeout"] > 0
        assert monitoring.performance_thresholds["pipeline_timeout"] > 0
        assert 0 < monitoring.performance_thresholds["max_error_rate"] < 1
        
        print("✅ Monitoring thresholds are correctly configured")
        print(f"   - API timeout: {monitoring.performance_thresholds['api_call_timeout']}s")
        print(f"   - Query timeout: {monitoring.performance_thresholds['slow_query_timeout']}s")
        print(f"   - Pipeline timeout: {monitoring.performance_thresholds['pipeline_timeout']}s")
        print(f"   - Max error rate: {monitoring.performance_thresholds['max_error_rate']:.1%}")
        return True
        
    except Exception as e:
        print(f"❌ Monitoring thresholds test failed: {e}")
        return False

def test_system_status():
    """Test system status reporting."""
    try:
        from app.monitoring.alerting import MonitoringSystem
        
        # Create monitoring system instance
        monitoring = MonitoringSystem()
        
        # Get system status
        status = monitoring.get_system_status()
        
        # Validate status structure
        required_keys = ["timestamp", "pipeline_statistics", "active_executions", "monitoring_active"]
        for key in required_keys:
            assert key in status, f"Missing status key: {key}"
        
        # Validate pipeline statistics
        stats = status["pipeline_statistics"]
        stats_keys = ["total_executions_24h", "completed_executions", "failed_executions", "success_rate", "average_duration_minutes"]
        for key in stats_keys:
            assert key in stats, f"Missing statistics key: {key}"
        
        # Validate data types
        assert isinstance(status["timestamp"], str)
        assert isinstance(status["active_executions"], int)
        assert isinstance(status["monitoring_active"], bool)
        assert isinstance(stats["success_rate"], (int, float))
        
        print("✅ System status reporting is correct")
        print("   - All required status fields present")
        print("   - Data types are correct")
        return True
        
    except Exception as e:
        print(f"❌ System status test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing monitoring and alerting functionality...")
    
    tests = [
        ("Monitoring Structure", test_monitoring_structure),
        ("Alert Levels", test_alert_levels),
        ("Pipeline Metrics", test_pipeline_metrics),
        ("Alert Structure", test_alert_structure),
        ("Monitoring Thresholds", test_monitoring_thresholds),
        ("System Status", test_system_status)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
    
    print(f"\n🏁 Monitoring Tests: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All monitoring tests passed!")
        print("\n📋 Monitoring & Alerting Summary:")
        print("   - Comprehensive monitoring system implemented")
        print("   - Pipeline execution tracking with metrics")
        print("   - Performance monitoring (API calls, database queries)")
        print("   - Multi-level alerting system (INFO, WARNING, ERROR, CRITICAL)")
        print("   - Email alerting for critical issues")
        print("   - Background monitoring for stuck processes")
        print("   - System status reporting and statistics")
        print("   - Context managers for easy integration")
        sys.exit(0)
    else:
        print("💥 Some monitoring tests failed!")
        sys.exit(1)