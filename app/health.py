"""
Health check module for the Competitive Exam Intelligence System.

This module provides health check functionality to verify system components
are operational, including database connectivity, external API access,
and content source availability.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import requests
import google.generativeai as genai
from sqlalchemy import text

from app.database.connection import get_session
from app import config


logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Health check service for system components.
    
    Provides methods to check database connectivity, external APIs,
    and content sources to ensure system operational status.
    """
    
    def __init__(self):
        """
        Initialize health checker.
        """
        self.timeout = 10  # seconds
    
    def check_all(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all system components.
        
        Returns:
            Dictionary containing health status of all components
        """
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        # Check database connectivity
        db_status = self.check_database_connection()
        health_status["checks"]["database"] = db_status
        
        # Check Gemini API
        gemini_status = self.check_gemini_api()
        health_status["checks"]["gemini_api"] = gemini_status
        
        # Check external sources
        sources_status = self.check_external_sources()
        health_status["checks"]["external_sources"] = sources_status
        
        # Determine overall status
        all_checks = [db_status, gemini_status, sources_status]
        if any(not check["healthy"] for check in all_checks):
            health_status["status"] = "unhealthy"
        elif any(check.get("warning") for check in all_checks):
            health_status["status"] = "degraded"
        
        return health_status
    
    def check_database_connection(self) -> Dict[str, Any]:
        """
        Check PostgreSQL database connectivity and basic operations.
        
        Returns:
            Dictionary with database health status
        """
        check_result = {
            "healthy": False,
            "message": "",
            "response_time_ms": 0,
            "details": {}
        }
        
        start_time = datetime.now()
        
        try:
            session = get_session()
            try:
                # Test basic connectivity
                result = session.execute(text("SELECT 1 as test"))
                test_value = result.scalar()
                
                if test_value != 1:
                    raise Exception("Database query returned unexpected result")
                
                # Check if main tables exist
                tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('articles', 'sources', 'categories', 'summaries', 'rankings')
                """)
                
                tables_result = session.execute(tables_query)
                existing_tables = [row[0] for row in tables_result]
                
                check_result.update({
                    "healthy": True,
                    "message": "Database connection successful",
                    "details": {
                        "existing_tables": existing_tables,
                        "tables_count": len(existing_tables)
                    }
                })
            finally:
                session.close()
                
        except Exception as e:
            check_result.update({
                "healthy": False,
                "message": f"Database connection failed: {str(e)}",
                "details": {"error": str(e)}
            })
            logger.error(f"Database health check failed: {e}")
        
        finally:
            end_time = datetime.now()
            check_result["response_time_ms"] = int(
                (end_time - start_time).total_seconds() * 1000
            )
        
        return check_result
    
    def check_gemini_api(self) -> Dict[str, Any]:
        """
        Check Google Gemini API connectivity and basic functionality.
        
        Returns:
            Dictionary with Gemini API health status
        """
        check_result = {
            "healthy": False,
            "message": "",
            "response_time_ms": 0,
            "details": {}
        }
        
        start_time = datetime.now()
        
        try:
            # Configure Gemini API
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel(config.GEMINI_MODEL)
            
            # Test with simple prompt
            test_prompt = "Respond with exactly: 'API_TEST_SUCCESS'"
            response = model.generate_content(
                test_prompt,
                generation_config={
                    "temperature": 0.0,
                    "max_output_tokens": 50,
                }
            )
            
            response_text = response.text.strip()
            
            if "API_TEST_SUCCESS" in response_text:
                check_result.update({
                    "healthy": True,
                    "message": "Gemini API connection successful",
                    "details": {
                        "model": config.GEMINI_MODEL,
                        "response_received": True
                    }
                })
            else:
                check_result.update({
                    "healthy": False,
                    "message": "Gemini API returned unexpected response",
                    "details": {
                        "expected": "API_TEST_SUCCESS",
                        "received": response_text[:100]
                    }
                })
                
        except Exception as e:
            check_result.update({
                "healthy": False,
                "message": f"Gemini API connection failed: {str(e)}",
                "details": {"error": str(e)}
            })
            logger.error(f"Gemini API health check failed: {e}")
        
        finally:
            end_time = datetime.now()
            check_result["response_time_ms"] = int(
                (end_time - start_time).total_seconds() * 1000
            )
        
        return check_result
    
    def check_external_sources(self) -> Dict[str, Any]:
        """
        Check availability of external content sources.
        
        Returns:
            Dictionary with external sources health status
        """
        check_result = {
            "healthy": True,
            "message": "All external sources accessible",
            "response_time_ms": 0,
            "details": {
                "sources": {}
            },
            "warning": False
        }
        
        start_time = datetime.now()
        sources_to_check = [
            {
                "name": "YouTube RSS",
                "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCYRBFLkuZ8ZAfwz7ayGGvZQ",
                "expected_status": 200
            },
            {
                "name": "PIB Website",
                "url": "https://pib.gov.in",
                "expected_status": 200
            },
            {
                "name": "Government Schemes Portal",
                "url": "https://www.myscheme.gov.in",
                "expected_status": 200
            }
        ]
        
        failed_sources = []
        warning_sources = []
        
        for source in sources_to_check:
            source_result = {
                "accessible": False,
                "status_code": None,
                "response_time_ms": 0,
                "error": None
            }
            
            source_start = datetime.now()
            
            try:
                response = requests.get(
                    source["url"],
                    timeout=self.timeout,
                    headers={
                        "User-Agent": "CompetitiveExamIntelligence/1.0 HealthCheck"
                    }
                )
                
                source_result.update({
                    "accessible": True,
                    "status_code": response.status_code
                })
                
                if response.status_code != source["expected_status"]:
                    warning_sources.append(source["name"])
                    source_result["warning"] = f"Unexpected status code: {response.status_code}"
                
            except requests.exceptions.Timeout:
                failed_sources.append(source["name"])
                source_result["error"] = "Request timeout"
                
            except requests.exceptions.RequestException as e:
                failed_sources.append(source["name"])
                source_result["error"] = str(e)
                
            except Exception as e:
                failed_sources.append(source["name"])
                source_result["error"] = f"Unexpected error: {str(e)}"
            
            finally:
                source_end = datetime.now()
                source_result["response_time_ms"] = int(
                    (source_end - source_start).total_seconds() * 1000
                )
            
            check_result["details"]["sources"][source["name"]] = source_result
        
        # Update overall status
        if failed_sources:
            check_result.update({
                "healthy": False,
                "message": f"Failed to access sources: {', '.join(failed_sources)}"
            })
        elif warning_sources:
            check_result.update({
                "warning": True,
                "message": f"Warning for sources: {', '.join(warning_sources)}"
            })
        
        end_time = datetime.now()
        check_result["response_time_ms"] = int(
            (end_time - start_time).total_seconds() * 1000
        )
        
        return check_result


def get_health_status() -> str:
    """
    Get system health status as JSON string.
    
    Returns:
        JSON string containing health check results
    """
    try:
        health_checker = HealthChecker()
        health_status = health_checker.check_all()
        return json.dumps(health_status, indent=2)
    except Exception as e:
        error_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "error": str(e)
        }
        return json.dumps(error_status, indent=2)


if __name__ == "__main__":
    """Run health check when executed directly."""
    print(get_health_status())