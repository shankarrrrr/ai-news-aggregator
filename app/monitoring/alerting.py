"""
Monitoring and alerting system for Competitive Exam Intelligence System.

This module provides comprehensive monitoring capabilities including
pipeline execution tracking, performance monitoring, error alerting,
and system health monitoring.
"""

import logging
import json
import smtplib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import time
import threading
from contextlib import contextmanager

# Optional email imports
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

from app import config


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert data structure."""
    level: AlertLevel
    title: str
    message: str
    component: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PipelineMetrics:
    """Pipeline execution metrics."""
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    articles_scraped: int = 0
    articles_categorized: int = 0
    articles_summarized: int = 0
    articles_ranked: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate execution duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def is_completed(self) -> bool:
        """Check if pipeline execution is completed."""
        return self.status in ["completed", "failed"]


class MonitoringSystem:
    """
    Comprehensive monitoring system for the application.
    
    Provides pipeline monitoring, performance tracking, error alerting,
    and system health monitoring capabilities.
    """
    
    def __init__(self, config_module=None):
        """
        Initialize monitoring system.
        
        Args:
            config_module: Optional configuration module
        """
        self.config = config_module or config
        self.logger = logging.getLogger(__name__)
        
        # Monitoring state
        self.pipeline_metrics: Dict[str, PipelineMetrics] = {}
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self.performance_thresholds = {
            "api_call_timeout": 5.0,  # seconds
            "slow_query_timeout": 1.0,  # seconds
            "pipeline_timeout": 1800,  # 30 minutes
            "max_error_rate": 0.1  # 10%
        }
        
        # Setup default alert handlers
        self._setup_alert_handlers()
        
        # Background monitoring thread
        self._monitoring_active = False
        self._monitoring_thread = None
    
    def _setup_alert_handlers(self) -> None:
        """Setup default alert handlers."""
        # Always add logging handler
        self.add_alert_handler(self._log_alert)
        
        # Add email handler if configured
        if (hasattr(self.config, 'SMTP_HOST') and 
            hasattr(self.config, 'EMAIL_TO') and
            getattr(self.config, 'SMTP_HOST', None) and 
            getattr(self.config, 'EMAIL_TO', None)):
            self.add_alert_handler(self._email_alert)
    
    def add_alert_handler(self, handler: Callable[[Alert], None]) -> None:
        """
        Add an alert handler function.
        
        Args:
            handler: Function that takes an Alert and handles it
        """
        self.alert_handlers.append(handler)
    
    def send_alert(self, alert: Alert) -> None:
        """
        Send an alert through all configured handlers.
        
        Args:
            alert: Alert to send
        """
        self.logger.info(f"Sending {alert.level.value} alert: {alert.title}")
        
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {str(e)}")
    
    def start_pipeline_monitoring(self, execution_id: str) -> PipelineMetrics:
        """
        Start monitoring a pipeline execution.
        
        Args:
            execution_id: Unique identifier for this execution
            
        Returns:
            PipelineMetrics object for tracking
        """
        metrics = PipelineMetrics(
            execution_id=execution_id,
            start_time=datetime.now(timezone.utc)
        )
        
        self.pipeline_metrics[execution_id] = metrics
        
        self.logger.info(f"Started monitoring pipeline execution: {execution_id}")
        
        # Send info alert
        self.send_alert(Alert(
            level=AlertLevel.INFO,
            title="Pipeline Execution Started",
            message=f"Pipeline execution {execution_id} has started",
            component="pipeline",
            timestamp=metrics.start_time,
            metadata={"execution_id": execution_id}
        ))
        
        return metrics
    
    def update_pipeline_metrics(
        self, 
        execution_id: str, 
        **kwargs
    ) -> Optional[PipelineMetrics]:
        """
        Update pipeline metrics.
        
        Args:
            execution_id: Pipeline execution ID
            **kwargs: Metrics to update
            
        Returns:
            Updated PipelineMetrics or None if not found
        """
        if execution_id not in self.pipeline_metrics:
            self.logger.warning(f"Pipeline metrics not found: {execution_id}")
            return None
        
        metrics = self.pipeline_metrics[execution_id]
        
        for key, value in kwargs.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)
        
        return metrics
    
    def complete_pipeline_monitoring(
        self, 
        execution_id: str, 
        status: str = "completed"
    ) -> Optional[PipelineMetrics]:
        """
        Complete pipeline monitoring and generate summary.
        
        Args:
            execution_id: Pipeline execution ID
            status: Final status (completed, failed)
            
        Returns:
            Final PipelineMetrics or None if not found
        """
        if execution_id not in self.pipeline_metrics:
            self.logger.warning(f"Pipeline metrics not found: {execution_id}")
            return None
        
        metrics = self.pipeline_metrics[execution_id]
        metrics.end_time = datetime.now(timezone.utc)
        metrics.status = status
        
        # Generate summary alert
        self._generate_pipeline_summary_alert(metrics)
        
        # Check for issues
        self._check_pipeline_issues(metrics)
        
        self.logger.info(f"Completed monitoring pipeline execution: {execution_id}")
        
        return metrics
    
    def log_api_latency(
        self, 
        api_name: str, 
        latency_seconds: float,
        execution_id: Optional[str] = None
    ) -> None:
        """
        Log API call latency and alert if slow.
        
        Args:
            api_name: Name of the API (e.g., "gemini", "youtube")
            latency_seconds: Latency in seconds
            execution_id: Optional pipeline execution ID
        """
        self.logger.info(f"API {api_name} latency: {latency_seconds:.2f}s")
        
        # Check if latency exceeds threshold
        if latency_seconds > self.performance_thresholds["api_call_timeout"]:
            self.send_alert(Alert(
                level=AlertLevel.WARNING,
                title="Slow API Call Detected",
                message=f"API {api_name} took {latency_seconds:.2f}s (threshold: {self.performance_thresholds['api_call_timeout']}s)",
                component="api",
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "api_name": api_name,
                    "latency_seconds": latency_seconds,
                    "execution_id": execution_id
                }
            ))
    
    def log_slow_query(
        self, 
        query: str, 
        duration_seconds: float,
        execution_id: Optional[str] = None
    ) -> None:
        """
        Log slow database query and alert.
        
        Args:
            query: SQL query (truncated for logging)
            duration_seconds: Query duration in seconds
            execution_id: Optional pipeline execution ID
        """
        query_preview = query[:100] + "..." if len(query) > 100 else query
        
        self.logger.warning(f"Slow query detected: {duration_seconds:.2f}s - {query_preview}")
        
        self.send_alert(Alert(
            level=AlertLevel.WARNING,
            title="Slow Database Query",
            message=f"Query took {duration_seconds:.2f}s (threshold: {self.performance_thresholds['slow_query_timeout']}s)",
            component="database",
            timestamp=datetime.now(timezone.utc),
            metadata={
                "query_preview": query_preview,
                "duration_seconds": duration_seconds,
                "execution_id": execution_id
            }
        ))
    
    def log_pipeline_error(
        self, 
        execution_id: str, 
        error: str, 
        component: str
    ) -> None:
        """
        Log pipeline error and update metrics.
        
        Args:
            execution_id: Pipeline execution ID
            error: Error message
            component: Component where error occurred
        """
        self.logger.error(f"Pipeline error in {component}: {error}")
        
        # Update metrics
        if execution_id in self.pipeline_metrics:
            self.pipeline_metrics[execution_id].errors.append(f"{component}: {error}")
        
        # Send error alert
        self.send_alert(Alert(
            level=AlertLevel.ERROR,
            title="Pipeline Error",
            message=f"Error in {component}: {error}",
            component=component,
            timestamp=datetime.now(timezone.utc),
            metadata={
                "execution_id": execution_id,
                "component": component,
                "error": error
            }
        ))
    
    def log_pipeline_warning(
        self, 
        execution_id: str, 
        warning: str, 
        component: str
    ) -> None:
        """
        Log pipeline warning and update metrics.
        
        Args:
            execution_id: Pipeline execution ID
            warning: Warning message
            component: Component where warning occurred
        """
        self.logger.warning(f"Pipeline warning in {component}: {warning}")
        
        # Update metrics
        if execution_id in self.pipeline_metrics:
            self.pipeline_metrics[execution_id].warnings.append(f"{component}: {warning}")
    
    def start_background_monitoring(self) -> None:
        """Start background monitoring thread."""
        if self._monitoring_active:
            self.logger.warning("Background monitoring already active")
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(
            target=self._background_monitoring_loop,
            daemon=True
        )
        self._monitoring_thread.start()
        
        self.logger.info("Started background monitoring")
    
    def stop_background_monitoring(self) -> None:
        """Stop background monitoring thread."""
        self._monitoring_active = False
        
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        
        self.logger.info("Stopped background monitoring")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status summary.
        
        Returns:
            Dictionary containing system status information
        """
        now = datetime.now(timezone.utc)
        
        # Recent pipeline executions (last 24 hours)
        recent_pipelines = [
            metrics for metrics in self.pipeline_metrics.values()
            if (now - metrics.start_time).total_seconds() < 86400
        ]
        
        # Calculate statistics
        completed_pipelines = [m for m in recent_pipelines if m.is_completed]
        failed_pipelines = [m for m in completed_pipelines if m.status == "failed"]
        
        return {
            "timestamp": now.isoformat(),
            "pipeline_statistics": {
                "total_executions_24h": len(recent_pipelines),
                "completed_executions": len(completed_pipelines),
                "failed_executions": len(failed_pipelines),
                "success_rate": (len(completed_pipelines) - len(failed_pipelines)) / max(len(completed_pipelines), 1) * 100,
                "average_duration_minutes": sum(
                    m.duration_seconds or 0 for m in completed_pipelines
                ) / max(len(completed_pipelines), 1) / 60
            },
            "active_executions": len([m for m in recent_pipelines if not m.is_completed]),
            "monitoring_active": self._monitoring_active
        }
    
    def _generate_pipeline_summary_alert(self, metrics: PipelineMetrics) -> None:
        """Generate pipeline execution summary alert."""
        duration_minutes = (metrics.duration_seconds or 0) / 60
        
        # Determine alert level based on status and issues
        if metrics.status == "failed":
            level = AlertLevel.ERROR
        elif metrics.errors:
            level = AlertLevel.WARNING
        else:
            level = AlertLevel.INFO
        
        message = f"""
Pipeline execution {metrics.execution_id} completed with status: {metrics.status}

Duration: {duration_minutes:.1f} minutes
Articles processed:
- Scraped: {metrics.articles_scraped}
- Categorized: {metrics.articles_categorized}
- Summarized: {metrics.articles_summarized}
- Ranked: {metrics.articles_ranked}

Errors: {len(metrics.errors)}
Warnings: {len(metrics.warnings)}
        """.strip()
        
        self.send_alert(Alert(
            level=level,
            title=f"Pipeline Execution {metrics.status.title()}",
            message=message,
            component="pipeline",
            timestamp=metrics.end_time or datetime.now(timezone.utc),
            metadata=asdict(metrics)
        ))
    
    def _check_pipeline_issues(self, metrics: PipelineMetrics) -> None:
        """Check for pipeline issues and send alerts."""
        # Check for timeout
        if metrics.duration_seconds and metrics.duration_seconds > self.performance_thresholds["pipeline_timeout"]:
            self.send_alert(Alert(
                level=AlertLevel.WARNING,
                title="Pipeline Execution Timeout",
                message=f"Pipeline took {metrics.duration_seconds/60:.1f} minutes (threshold: {self.performance_thresholds['pipeline_timeout']/60:.1f} minutes)",
                component="pipeline",
                timestamp=metrics.end_time or datetime.now(timezone.utc),
                metadata={"execution_id": metrics.execution_id}
            ))
        
        # Check error rate
        total_articles = metrics.articles_scraped
        if total_articles > 0:
            error_rate = len(metrics.errors) / total_articles
            if error_rate > self.performance_thresholds["max_error_rate"]:
                self.send_alert(Alert(
                    level=AlertLevel.WARNING,
                    title="High Error Rate Detected",
                    message=f"Error rate: {error_rate:.1%} (threshold: {self.performance_thresholds['max_error_rate']:.1%})",
                    component="pipeline",
                    timestamp=metrics.end_time or datetime.now(timezone.utc),
                    metadata={"execution_id": metrics.execution_id, "error_rate": error_rate}
                ))
    
    def _background_monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self._monitoring_active:
            try:
                # Check for stuck pipeline executions
                self._check_stuck_pipelines()
                
                # Sleep for monitoring interval
                time.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Background monitoring error: {str(e)}")
                time.sleep(60)  # Wait before retrying
    
    def _check_stuck_pipelines(self) -> None:
        """Check for pipeline executions that appear stuck."""
        now = datetime.now(timezone.utc)
        timeout_threshold = timedelta(seconds=self.performance_thresholds["pipeline_timeout"])
        
        for execution_id, metrics in self.pipeline_metrics.items():
            if not metrics.is_completed:
                execution_time = now - metrics.start_time
                
                if execution_time > timeout_threshold:
                    self.send_alert(Alert(
                        level=AlertLevel.CRITICAL,
                        title="Pipeline Execution Stuck",
                        message=f"Pipeline {execution_id} has been running for {execution_time.total_seconds()/60:.1f} minutes without completion",
                        component="pipeline",
                        timestamp=now,
                        metadata={"execution_id": execution_id, "runtime_minutes": execution_time.total_seconds()/60}
                    ))
    
    def _log_alert(self, alert: Alert) -> None:
        """Log alert to application logs."""
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }[alert.level]
        
        self.logger.log(
            log_level,
            f"ALERT [{alert.level.value.upper()}] {alert.component}: {alert.title} - {alert.message}"
        )
    
    def _email_alert(self, alert: Alert) -> None:
        """Send alert via email."""
        if not EMAIL_AVAILABLE:
            self.logger.warning("Email functionality not available - skipping email alert")
            return
            
        try:
            # Only send email for WARNING and above
            if alert.level in [AlertLevel.INFO]:
                return
            
            # Create email message
            msg = MimeMultipart()
            msg['From'] = getattr(self.config, 'EMAIL_FROM', 'noreply@examai.com')
            msg['To'] = getattr(self.config, 'EMAIL_TO', '')
            msg['Subject'] = f"[{alert.level.value.upper()}] Competitive Exam Intelligence: {alert.title}"
            
            # Email body
            body = f"""
Alert Details:
- Level: {alert.level.value.upper()}
- Component: {alert.component}
- Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
- Title: {alert.title}

Message:
{alert.message}

Metadata:
{json.dumps(alert.metadata, indent=2, default=str)}

---
Competitive Exam Intelligence System
Automated Monitoring Alert
            """.strip()
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            smtp_host = getattr(self.config, 'SMTP_HOST', 'smtp.gmail.com')
            smtp_port = getattr(self.config, 'SMTP_PORT', 587)
            smtp_username = getattr(self.config, 'SMTP_USERNAME', '')
            smtp_password = getattr(self.config, 'SMTP_PASSWORD', '')
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            self.logger.info(f"Email alert sent for: {alert.title}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")


# Global monitoring instance
_monitoring_system = None


def get_monitoring_system() -> MonitoringSystem:
    """Get global monitoring system instance."""
    global _monitoring_system
    if _monitoring_system is None:
        _monitoring_system = MonitoringSystem()
    return _monitoring_system


@contextmanager
def monitor_api_call(api_name: str, execution_id: Optional[str] = None):
    """
    Context manager for monitoring API call latency.
    
    Args:
        api_name: Name of the API being called
        execution_id: Optional pipeline execution ID
    """
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        latency = end_time - start_time
        get_monitoring_system().log_api_latency(api_name, latency, execution_id)


@contextmanager
def monitor_database_query(query: str, execution_id: Optional[str] = None):
    """
    Context manager for monitoring database query performance.
    
    Args:
        query: SQL query being executed
        execution_id: Optional pipeline execution ID
    """
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time
        
        if duration > get_monitoring_system().performance_thresholds["slow_query_timeout"]:
            get_monitoring_system().log_slow_query(query, duration, execution_id)