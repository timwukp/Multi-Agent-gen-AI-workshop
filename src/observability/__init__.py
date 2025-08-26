"""
Observability module for AWS Bedrock Workshop.

This module provides comprehensive observability capabilities including:
- OpenTelemetry distributed tracing with AWS X-Ray integration
- CloudWatch metrics collection and reporting
- Health monitoring and dependency validation
- Performance monitoring and optimization
"""

from .config import ObservabilityConfig, TracingConfig, MetricsConfig, HealthConfig
from .service import ObservabilityService, trace_operation, get_observability_service
from .metrics import (
    MetricsCollector, 
    AgentMetrics, 
    SystemMetrics, 
    MetricDataPoint,
    create_agent_metrics,
    create_system_metrics
)
from .health import (
    HealthMonitor,
    HealthStatus,
    DependencyStatus,
    OverallHealthStatus,
    HealthCheckFunction,
    create_health_monitor
)
from .performance import (
    PerformanceAnalyzer,
    PerformanceMetrics,
    BottleneckAlert,
    CostMetrics,
    CapacityPrediction,
    PerformanceStatus,
    BottleneckType,
    create_performance_metrics
)
from .dashboards import (
    DashboardService,
    AlertingService,
    AlarmConfiguration,
    DashboardConfiguration,
    DashboardWidget,
    AlarmState,
    ComparisonOperator,
    Statistic,
    create_dashboard_service,
    create_alerting_service
)
from .security import (
    SecurityMonitor,
    SecurityEvent,
    SecurityEventType,
    SecurityLevel,
    AuditTrail,
    SecurityAnomaly,
    ComplianceReport,
    ComplianceFramework,
    create_security_monitor
)
from .security_dashboards import (
    SecurityDashboardService,
    create_security_dashboard_service
)

__all__ = [
    "ObservabilityConfig",
    "TracingConfig", 
    "MetricsConfig",
    "HealthConfig",
    "ObservabilityService",
    "trace_operation",
    "get_observability_service",
    "MetricsCollector",
    "AgentMetrics",
    "SystemMetrics",
    "MetricDataPoint",
    "create_agent_metrics",
    "create_system_metrics",
    "HealthMonitor",
    "HealthStatus",
    "DependencyStatus",
    "OverallHealthStatus",
    "HealthCheckFunction",
    "create_health_monitor",
    "PerformanceAnalyzer",
    "PerformanceMetrics",
    "BottleneckAlert",
    "CostMetrics",
    "CapacityPrediction",
    "PerformanceStatus",
    "BottleneckType",
    "create_performance_metrics",
    "DashboardService",
    "AlertingService",
    "AlarmConfiguration",
    "DashboardConfiguration",
    "DashboardWidget",
    "AlarmState",
    "ComparisonOperator",
    "Statistic",
    "create_dashboard_service",
    "create_alerting_service",
    "SecurityMonitor",
    "SecurityEvent",
    "SecurityEventType",
    "SecurityLevel",
    "AuditTrail",
    "SecurityAnomaly",
    "ComplianceReport",
    "ComplianceFramework",
    "create_security_monitor",
    "SecurityDashboardService",
    "create_security_dashboard_service"
]