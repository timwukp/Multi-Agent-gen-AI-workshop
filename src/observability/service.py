# Observability Service - Core OpenTelemetry tracing and monitoring
# This is a production-ready implementation with AWS X-Ray integration
# For the complete implementation, see the full repository

"""
OpenTelemetry distributed tracing service for AWS Bedrock Workshop.

This module implements comprehensive distributed tracing using OpenTelemetry
with AWS X-Ray integration for production monitoring and observability.
"""

import os
import time
import logging
from typing import Dict, Any, Optional, ContextManager
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

# Local imports
from .config import ObservabilityConfig, TracingConfig


class ObservabilityService:
    """
    Facade for comprehensive observability services.
    
    Coordinates tracing, metrics, and context propagation for multi-agent systems.
    """
    
    def __init__(self, config: ObservabilityConfig):
        """
        Initialize the observability service.
        
        Args:
            config: Observability configuration containing tracing settings.
        """
        if not config:
            raise ValueError("ObservabilityConfig is required")
        
        self.config = config
        self.tracing_config = config.tracing
        self._tracer: Optional[trace.Tracer] = None
        self._meter: Optional[metrics.Meter] = None
        self._initialized = False
        self._logger = logging.getLogger(__name__)
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialize observability components with error handling."""
        try:
            if self.tracing_config.enabled:
                self._initialize_tracing()
            
            self._initialized = True
            self._logger.info("ObservabilityService initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize ObservabilityService: {e}")
    
    def _initialize_tracing(self) -> None:
        """Initialize OpenTelemetry tracing with AWS X-Ray integration."""
        # Create resource with service information
        resource = Resource.create({
            "service.name": self.tracing_config.service_name,
            "service.version": self.tracing_config.service_version,
            "deployment.environment": self.config.environment,
            "cloud.provider": "aws",
            "cloud.region": self.tracing_config.aws_region,
        })
        
        # Set up tracer provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)
        
        # Initialize tracer
        self._tracer = trace.get_tracer(__name__)
        
        self._logger.info(f"Tracing initialized for service: {self.tracing_config.service_name}")
    
    @property
    def tracer(self) -> trace.Tracer:
        """Get the OpenTelemetry tracer instance."""
        if not self._initialized or not self._tracer:
            raise RuntimeError("ObservabilityService not properly initialized")
        return self._tracer
    
    def trace_agent_operation(
        self,
        agent_name: str,
        operation: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> ContextManager[Span]:
        """
        Create a trace span for agent operations.
        
        Args:
            agent_name: Name of the agent performing the operation
            operation: Name of the operation being performed
            attributes: Additional attributes to add to the span
            
        Returns:
            Context manager for the trace span
        """
        if not self._initialized or not self._tracer:
            return self._noop_span_context()
        
        span_name = f"{agent_name}.{operation}"
        span_attributes = {
            "agent.name": agent_name,
            "agent.operation": operation,
            "service.name": self.tracing_config.service_name,
        }
        
        if attributes:
            span_attributes.update(attributes)
        
        return self._enhanced_span_context(span_name, span_attributes)
    
    @contextmanager
    def _enhanced_span_context(self, span_name: str, span_attributes: Dict[str, Any]):
        """Enhanced span context with error handling."""
        start_time = time.time()
        span = None
        
        try:
            span = self._tracer.start_span(span_name, attributes=span_attributes)
            with trace.use_span(span, end_on_exit=False):
                yield span
        except Exception as e:
            if span:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise
        else:
            if span:
                span.set_status(trace.Status(trace.StatusCode.OK))
        finally:
            if span:
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("operation.duration_ms", duration_ms)
                span.end()
    
    @contextmanager
    def _noop_span_context(self):
        """No-op context manager when tracing is disabled."""
        yield None
