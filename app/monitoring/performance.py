"""
Performance monitoring and logging utilities.

This module provides decorators and functions for monitoring system performance,
tracking API latencies, and logging slow operations.
"""

import time
import logging
import functools
from typing import Callable, Any, Optional, Dict
from datetime import datetime, timezone
from contextlib import contextmanager


# Configure structured logging
def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging with timestamps and context.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s:%(lineno)d',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add custom formatter for structured logging
    class StructuredFormatter(logging.Formatter):
        def format(self, record):
            # Add timestamp in ISO format
            record.timestamp = datetime.now(timezone.utc).isoformat()
            
            # Add context if available
            if hasattr(record, 'extra'):
                for key, value in record.extra.items():
                    setattr(record, key, value)
            
            return super().format(record)
    
    # Apply structured formatter to all handlers
    for handler in logging.root.handlers:
        handler.setFormatter(StructuredFormatter(
            '%(timestamp)s - %(name)s - %(levelname)s - %(message)s'
        ))


def monitor_performance(
    operation_name: Optional[str] = None,
    log_slow_threshold: float = 1.0,
    include_args: bool = False
) -> Callable:
    """
    Decorator to monitor function performance and log execution times.
    
    Logs slow operations (>threshold) and tracks performance metrics.
    
    Args:
        operation_name: Custom name for the operation (uses function name if None)
        log_slow_threshold: Threshold in seconds to log slow operations
        include_args: Whether to include function arguments in logs
        
    Returns:
        Decorated function
        
    Example:
        @monitor_performance("scrape_youtube", log_slow_threshold=2.0)
        def scrape_videos(channel_id: str) -> List[Video]:
            # Function implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(func.__module__)
            op_name = operation_name or f"{func.__name__}"
            
            # Log operation start
            start_time = time.time()
            logger.debug(
                f"Starting operation: {op_name}",
                extra={
                    'operation': op_name,
                    'start_time': start_time,
                    'args': str(args) if include_args else None,
                    'kwargs': str(kwargs) if include_args else None
                }
            )
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                
                # Log completion with timing
                log_level = logging.WARNING if duration > log_slow_threshold else logging.DEBUG
                logger.log(
                    log_level,
                    f"Completed operation: {op_name} in {duration:.3f}s",
                    extra={
                        'operation': op_name,
                        'duration': duration,
                        'slow_operation': duration > log_slow_threshold,
                        'success': True
                    }
                )
                
                return result
                
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                
                logger.error(
                    f"Failed operation: {op_name} after {duration:.3f}s - {str(e)}",
                    exc_info=True,
                    extra={
                        'operation': op_name,
                        'duration': duration,
                        'success': False,
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                )
                raise
        
        return wrapper
    return decorator


def log_api_latency(
    api_name: str,
    endpoint: str,
    latency: float,
    status_code: Optional[int] = None,
    response_size: Optional[int] = None
) -> None:
    """
    Log API call latency for monitoring purposes.
    
    Args:
        api_name: Name of the API (e.g., "Gemini", "YouTube")
        endpoint: API endpoint or operation name
        latency: Response time in seconds
        status_code: HTTP status code if applicable
        response_size: Response size in bytes if applicable
    """
    logger = logging.getLogger("api_monitoring")
    
    # Determine log level based on latency
    if latency > 5.0:
        log_level = logging.WARNING
    elif latency > 1.0:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    
    logger.log(
        log_level,
        f"API call: {api_name}/{endpoint} - {latency:.3f}s",
        extra={
            'api_name': api_name,
            'endpoint': endpoint,
            'latency': latency,
            'status_code': status_code,
            'response_size': response_size,
            'slow_api_call': latency > 1.0
        }
    )


def log_slow_query(
    query_type: str,
    query: str,
    duration: float,
    row_count: Optional[int] = None,
    table_name: Optional[str] = None
) -> None:
    """
    Log slow database queries for performance monitoring.
    
    Args:
        query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        query: SQL query (truncated for logging)
        duration: Query execution time in seconds
        row_count: Number of rows affected/returned
        table_name: Primary table involved in query
    """
    logger = logging.getLogger("db_monitoring")
    
    # Only log queries that exceed 1 second threshold
    if duration > 1.0:
        # Truncate query for logging (first 200 chars)
        truncated_query = query[:200] + "..." if len(query) > 200 else query
        
        logger.warning(
            f"Slow query detected: {query_type} on {table_name or 'unknown'} - {duration:.3f}s",
            extra={
                'query_type': query_type,
                'query': truncated_query,
                'duration': duration,
                'row_count': row_count,
                'table_name': table_name,
                'slow_query': True
            }
        )


@contextmanager
def api_call_timer(api_name: str, endpoint: str):
    """
    Context manager for timing API calls.
    
    Args:
        api_name: Name of the API
        endpoint: API endpoint or operation
        
    Yields:
        Dictionary to store additional metrics
        
    Example:
        with api_call_timer("Gemini", "generate_content") as metrics:
            response = api_client.generate(prompt)
            metrics['response_size'] = len(response.text)
            metrics['status_code'] = 200
    """
    start_time = time.time()
    metrics = {}
    
    try:
        yield metrics
        
    finally:
        end_time = time.time()
        latency = end_time - start_time
        
        log_api_latency(
            api_name=api_name,
            endpoint=endpoint,
            latency=latency,
            status_code=metrics.get('status_code'),
            response_size=metrics.get('response_size')
        )


@contextmanager
def database_query_timer(query_type: str, table_name: Optional[str] = None):
    """
    Context manager for timing database queries.
    
    Args:
        query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        table_name: Primary table involved
        
    Yields:
        Dictionary to store query details
        
    Example:
        with database_query_timer("SELECT", "articles") as query_info:
            results = session.query(Article).filter(...).all()
            query_info['query'] = str(results.statement)
            query_info['row_count'] = len(results)
    """
    start_time = time.time()
    query_info = {}
    
    try:
        yield query_info
        
    finally:
        end_time = time.time()
        duration = end_time - start_time
        
        # Only log if duration exceeds threshold
        if duration > 1.0:
            log_slow_query(
                query_type=query_type,
                query=query_info.get('query', 'Unknown query'),
                duration=duration,
                row_count=query_info.get('row_count'),
                table_name=table_name
            )


class PerformanceTracker:
    """
    Class for tracking performance metrics across operations.
    
    Useful for collecting statistics during pipeline execution.
    """
    
    def __init__(self):
        """Initialize performance tracker."""
        self.metrics: Dict[str, list] = {}
        self.start_time = time.time()
    
    def record_operation(
        self, 
        operation: str, 
        duration: float, 
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record performance metrics for an operation.
        
        Args:
            operation: Operation name
            duration: Duration in seconds
            success: Whether operation succeeded
            metadata: Additional metadata
        """
        if operation not in self.metrics:
            self.metrics[operation] = []
        
        self.metrics[operation].append({
            'duration': duration,
            'success': success,
            'timestamp': time.time(),
            'metadata': metadata or {}
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get performance summary statistics.
        
        Returns:
            Dictionary with performance statistics
        """
        summary = {
            'total_runtime': time.time() - self.start_time,
            'operations': {}
        }
        
        for operation, records in self.metrics.items():
            durations = [r['duration'] for r in records]
            successes = [r['success'] for r in records]
            
            summary['operations'][operation] = {
                'count': len(records),
                'success_rate': sum(successes) / len(successes) if successes else 0,
                'avg_duration': sum(durations) / len(durations) if durations else 0,
                'min_duration': min(durations) if durations else 0,
                'max_duration': max(durations) if durations else 0,
                'total_duration': sum(durations)
            }
        
        return summary
    
    def log_summary(self) -> None:
        """Log performance summary."""
        logger = logging.getLogger("performance_summary")
        summary = self.get_summary()
        
        logger.info(
            f"Performance Summary - Total Runtime: {summary['total_runtime']:.2f}s",
            extra=summary
        )
        
        for operation, stats in summary['operations'].items():
            logger.info(
                f"Operation {operation}: {stats['count']} calls, "
                f"{stats['success_rate']:.1%} success rate, "
                f"{stats['avg_duration']:.3f}s avg duration"
            )


# Global performance tracker instance
_global_tracker = PerformanceTracker()


def get_global_tracker() -> PerformanceTracker:
    """Get the global performance tracker instance."""
    return _global_tracker


def reset_global_tracker() -> None:
    """Reset the global performance tracker."""
    global _global_tracker
    _global_tracker = PerformanceTracker()