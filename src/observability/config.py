# Configuration classes for observability components
# This is a production-ready implementation with comprehensive validation
# For the complete implementation, see the full repository

"""
Observability configuration classes using Pydantic for environment management.

This module defines configuration classes for all observability components including
OpenTelemetry tracing, CloudWatch metrics, and health monitoring.
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class LogLevel(str, Enum):
    """Supported log levels for observability components."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TracingConfig(BaseModel):
    """Configuration for OpenTelemetry distributed tracing."""
    
    enabled: bool = Field(
        default=True,
        description="Enable/disable distributed tracing"
    )
    
    service_name: str = Field(
        default="bedrock-workshop-agents",
        description="Service name for trace identification"
    )
    
    @field_validator("service_name")
    @classmethod
    def validate_service_name(cls, v: str) -> str:
        """Validate service name for security."""
        if not v or len(v) > 100:
            raise ValueError("Service name must be 1-100 characters")
        
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Service name contains invalid characters")
        
        return v
    
    service_version: str = Field(
        default="1.0.0",
        description="Service version for trace metadata"
    )
    
    aws_region: str = Field(
        default="us-west-2",
        description="AWS region for X-Ray exporter"
    )
    
    @field_validator("aws_region")
    @classmethod
    def validate_aws_region(cls, v: str) -> str:
        """Validate AWS region against official AWS region list."""
        if not v or not isinstance(v, str):
            raise ValueError("AWS region must be a non-empty string")
        
        # Basic security validation
        if '..' in v or '/' in v or ';' in v:
            raise ValueError("AWS region contains unsafe characters")
        
        # Official AWS regions (subset for brevity)
        valid_regions = {
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1'
        }
        
        if v not in valid_regions:
            raise ValueError(f"Invalid AWS region: '{v}'")
        
        return v
    
    sample_rate: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Trace sampling rate (0.0 to 1.0)"
    )
    
    export_timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Timeout for exporting spans to X-Ray"
    )
    
    propagate_context: bool = Field(
        default=True,
        description="Enable trace context propagation"
    )


class MetricsConfig(BaseModel):
    """Configuration for CloudWatch metrics collection."""
    
    enabled: bool = Field(
        default=True,
        description="Enable/disable metrics collection"
    )
    
    namespace: str = Field(
        default="BedrockWorkshop/Agents",
        description="CloudWatch metrics namespace"
    )
    
    @field_validator("namespace")
    @classmethod
    def validate_namespace(cls, v: str) -> str:
        """Validate namespace for security."""
        if not v or len(v) > 255:
            raise ValueError("Namespace must be 1-255 characters")
        
        import re
        if not re.match(r'^[a-zA-Z0-9_/-]+$', v):
            raise ValueError("Namespace contains invalid characters")
        
        return v
    
    aws_region: str = Field(
        default="us-west-2",
        description="AWS region for CloudWatch metrics"
    )
    
    flush_interval_seconds: int = Field(
        default=60,
        gt=0,
        description="Interval for flushing metrics to CloudWatch"
    )
    
    max_buffer_size: int = Field(
        default=1000,
        gt=0,
        description="Maximum number of metrics to buffer"
    )
    
    default_dimensions: Dict[str, str] = Field(
        default_factory=lambda: {
            "Environment": os.getenv("ENVIRONMENT", "development"),
            "Service": "bedrock-workshop-agents"
        },
        description="Default dimensions added to all metrics"
    )
    
    agent_metrics_enabled: bool = Field(
        default=True,
        description="Enable agent-specific performance metrics"
    )
    
    system_metrics_enabled: bool = Field(
        default=True,
        description="Enable system-level metrics"
    )


class HealthConfig(BaseModel):
    """Configuration for health monitoring."""
    
    enabled: bool = Field(
        default=True,
        description="Enable/disable health monitoring"
    )
    
    check_interval_seconds: int = Field(
        default=30,
        gt=0,
        description="Interval for running health checks"
    )
    
    timeout_seconds: int = Field(
        default=10,
        gt=0,
        description="Timeout for individual health checks"
    )
    
    dependencies: List[str] = Field(
        default_factory=lambda: [
            "bedrock",
            "knowledge_base",
            "agentcore_memory"
        ],
        description="List of dependencies to monitor"
    )
    
    sns_topic_arn: Optional[str] = Field(
        default=None,
        description="SNS topic ARN for health check alerts"
    )


class ObservabilityConfig(BaseModel):
    """Main observability configuration combining all components."""
    
    # Component configurations
    tracing: TracingConfig = Field(
        default_factory=TracingConfig,
        description="OpenTelemetry tracing configuration"
    )
    
    metrics: MetricsConfig = Field(
        default_factory=MetricsConfig,
        description="CloudWatch metrics configuration"
    )
    
    health: HealthConfig = Field(
        default_factory=HealthConfig,
        description="Health monitoring configuration"
    )
    
    # Global settings
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Global log level for observability components"
    )
    
    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development"),
        description="Deployment environment"
    )
    
    debug_mode: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true",
        description="Enable debug mode for detailed logging"
    )
    
    aws_profile: Optional[str] = Field(
        default_factory=lambda: os.getenv("AWS_PROFILE"),
        description="AWS profile for authentication"
    )
    
    aws_region: str = Field(
        default="us-west-2",
        description="AWS region for all services"
    )
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the expected values."""
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def get_service_tags(self) -> Dict[str, str]:
        """Get common service tags for AWS resources."""
        return {
            "Service": "bedrock-workshop-agents",
            "Environment": self.environment,
            "Component": "observability"
        }
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "OBSERVABILITY_"
        case_sensitive = False
        validate_assignment = True


# Configuration factory function
def create_observability_config() -> ObservabilityConfig:
    """
    Create observability configuration from environment variables.
    
    Returns:
        ObservabilityConfig: Validated configuration instance.
    """
    return ObservabilityConfig()


# Default configuration instance
observability_config = create_observability_config()
