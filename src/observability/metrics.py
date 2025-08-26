# Metrics Collection Service - CloudWatch integration with security validation
# This is a production-ready implementation with comprehensive input sanitization
# For the complete implementation, see the full repository

"""
CloudWatch metrics collection service for AWS Bedrock Workshop.

This module implements comprehensive metrics collection using AWS CloudWatch
for monitoring agent performance, system metrics, and business KPIs.
"""

import time
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock

import boto3
from botocore.exceptions import ClientError

from .config import MetricsConfig


@dataclass
class AgentMetrics:
    """Data class for agent-specific performance metrics."""
    agent_name: str
    operation: str
    timestamp: datetime
    response_time_ms: float
    success_rate: float = 1.0
    error_count: int = 0
    concurrent_requests: int = 1
    memory_usage_mb: float = 0.0
    custom_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """Data class for AgentCore runtime system metrics."""
    timestamp: datetime
    cpu_utilization: float
    memory_utilization: float
    active_agents: int
    total_requests: int
    error_rate: float
    custom_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricDataPoint:
    """Individual metric data point for CloudWatch."""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    dimensions: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    CloudWatch metrics collection service with buffering and batch sending.
    
    Collects agent-specific performance metrics, system metrics, and business KPIs,
    then sends them to CloudWatch in batches for efficient monitoring.
    """
    
    def __init__(self, config: MetricsConfig):
        """
        Initialize the metrics collector.
        
        Args:
            config: Metrics configuration containing CloudWatch settings.
        """
        self.config = config
        self._logger = logging.getLogger(f"{__name__}.MetricsCollector")
        
        # Initialize CloudWatch client
        self._cloudwatch_client = self._create_cloudwatch_client()
        
        # Metrics buffer for batch sending
        self._metrics_buffer: List[MetricDataPoint] = []
        self._buffer_lock = Lock()
        
        if self.config.enabled:
            self._logger.info(f"MetricsCollector initialized for namespace: {self.config.namespace}")
    
    def _create_cloudwatch_client(self):
        """Create CloudWatch client with proper configuration."""
        try:
            session = boto3.Session()
            client = session.client('cloudwatch', region_name=self.config.aws_region)
            self._logger.info(f"CloudWatch client initialized for region: {self.config.aws_region}")
            return client
        except Exception as e:
            self._logger.error(f"Failed to initialize CloudWatch client: {e}")
            raise RuntimeError("Failed to initialize CloudWatch client")
    
    def record_agent_metrics(self, agent_name: str, metrics: AgentMetrics) -> None:
        """
        Record agent-specific performance metrics.
        
        Args:
            agent_name: Name of the agent
            metrics: AgentMetrics object containing performance data
        """
        if not self.config.enabled or not self.config.agent_metrics_enabled:
            return
        
        try:
            # Validate inputs
            if not agent_name or not isinstance(agent_name, str):
                raise ValueError("agent_name must be a non-empty string")
            
            # Prepare dimensions with security validation
            dimensions = {
                "AgentName": self._sanitize_dimension_value(agent_name),
                "Operation": self._sanitize_dimension_value(metrics.operation),
                **self.config.default_dimensions
            }
            
            # Create metric data points
            metric_points = [
                MetricDataPoint(
                    metric_name="AgentResponseTime",
                    value=metrics.response_time_ms,
                    unit="Milliseconds",
                    timestamp=metrics.timestamp,
                    dimensions=dimensions
                ),
                MetricDataPoint(
                    metric_name="AgentSuccessRate",
                    value=metrics.success_rate * 100,
                    unit="Percent",
                    timestamp=metrics.timestamp,
                    dimensions=dimensions
                )
            ]
            
            # Buffer the metrics
            self._buffer_metrics(metric_points)
            
            self._logger.debug(f"Recorded {len(metric_points)} agent metrics for {agent_name}")
            
        except Exception as e:
            self._logger.error(f"Failed to record agent metrics for {agent_name}: {e}")
    
    def _sanitize_dimension_value(self, value: str) -> str:
        """
        Sanitize dimension value for CloudWatch compatibility and security.
        
        Args:
            value: Raw dimension value
            
        Returns:
            str: Sanitized dimension value
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Remove dangerous characters and limit length
        sanitized = ''.join(c for c in value if c.isalnum() or c in ' ._-')
        return sanitized[:255].strip()
    
    def _buffer_metrics(self, metrics: List[MetricDataPoint]) -> None:
        """
        Add metrics to the buffer.
        
        Args:
            metrics: List of metric data points to buffer
        """
        with self._buffer_lock:
            self._metrics_buffer.extend(metrics)
    
    def flush_metrics(self) -> bool:
        """
        Flush all buffered metrics to CloudWatch.
        
        Returns:
            bool: True if flush was successful, False otherwise
        """
        if not self.config.enabled:
            return True
        
        with self._buffer_lock:
            if not self._metrics_buffer:
                return True
            
            metrics_to_send = self._metrics_buffer.copy()
            self._metrics_buffer.clear()
        
        try:
            # Send metrics in batches (CloudWatch limit is 20 metrics per request)
            batch_size = 20
            success_count = 0
            
            for i in range(0, len(metrics_to_send), batch_size):
                batch = metrics_to_send[i:i + batch_size]
                if self._send_metrics_batch(batch):
                    success_count += len(batch)
            
            if success_count > 0:
                self._logger.info(f"Successfully sent {success_count}/{len(metrics_to_send)} metrics")
            
            return success_count == len(metrics_to_send)
            
        except Exception as e:
            self._logger.error(f"Failed to flush metrics: {e}")
            return False
    
    def _send_metrics_batch(self, metrics: List[MetricDataPoint]) -> bool:
        """
        Send a batch of metrics to CloudWatch.
        
        Args:
            metrics: List of metric data points to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert metrics to CloudWatch format
            metric_data = []
            
            for metric in metrics:
                dimensions = [
                    {"Name": name, "Value": value}
                    for name, value in metric.dimensions.items()
                ]
                
                metric_data.append({
                    "MetricName": metric.metric_name,
                    "Value": metric.value,
                    "Unit": metric.unit,
                    "Timestamp": metric.timestamp,
                    "Dimensions": dimensions
                })
            
            # Send to CloudWatch
            response = self._cloudwatch_client.put_metric_data(
                Namespace=self.config.namespace,
                MetricData=metric_data
            )
            
            return response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200
            
        except ClientError as e:
            self._logger.error(f"CloudWatch API error: {e}")
            return False
        except Exception as e:
            self._logger.error(f"Unexpected error sending metrics batch: {e}")
            return False


# Utility functions for creating metrics objects

def create_agent_metrics(
    agent_name: str,
    operation: str,
    response_time_ms: float,
    success: bool = True,
    **kwargs
) -> AgentMetrics:
    """
    Create an AgentMetrics object with common defaults.
    
    Args:
        agent_name: Name of the agent
        operation: Operation performed
        response_time_ms: Response time in milliseconds
        success: Whether the operation was successful
        **kwargs: Additional keyword arguments
        
    Returns:
        AgentMetrics: Configured metrics object
    """
    return AgentMetrics(
        agent_name=agent_name,
        operation=operation,
        timestamp=datetime.now(timezone.utc),
        response_time_ms=response_time_ms,
        success_rate=1.0 if success else 0.0,
        **kwargs
    )
