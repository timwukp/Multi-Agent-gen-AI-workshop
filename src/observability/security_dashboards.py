# Security Dashboards Service - CloudWatch dashboards for security monitoring
# This is a production-ready implementation with comprehensive security visualization
# For the complete implementation, see the full repository

"""
Security dashboards and alerting for AWS Bedrock Workshop.

This module implements security-specific CloudWatch dashboards and alerting
for comprehensive security monitoring and compliance tracking.
"""

import json
import logging
from typing import Dict, Any, List
import boto3
from botocore.exceptions import ClientError

# Local imports
from .config import ObservabilityConfig


class SecurityDashboardService:
    """
    Service for creating and managing security-focused CloudWatch dashboards.
    
    Provides specialized dashboards for security monitoring, compliance tracking,
    and anomaly detection visualization.
    """
    
    def __init__(self, config: ObservabilityConfig):
        """
        Initialize the security dashboard service.
        
        Args:
            config: Observability configuration
        """
        self.config = config
        self._logger = logging.getLogger(f"{__name__}.SecurityDashboardService")
        
        # Initialize AWS clients
        self._cloudwatch_client = None
        self._logs_client = None
        
        self._initialize_aws_clients()
    
    def _initialize_aws_clients(self) -> None:
        """Initialize AWS service clients."""
        try:
            session = boto3.Session(
                profile_name=self.config.aws_profile,
                region_name=self.config.aws_region
            )
            
            self._cloudwatch_client = session.client('cloudwatch')
            self._logs_client = session.client('logs')
            
            self._logger.info("AWS clients initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize AWS clients: {e}")
            raise
    
    def create_security_overview_dashboard(self) -> str:
        """
        Create a comprehensive security overview dashboard.
        
        Returns:
            str: Dashboard name
        """
        dashboard_name = f"BedrockWorkshop-Security-Overview-{self.config.environment}"
        
        dashboard_body = {
            "widgets": [
                # Security Events Overview
                {
                    "type": "metric",
                    "x": 0, "y": 0, "width": 12, "height": 6,
                    "properties": {
                        "metrics": [
                            [self.config.metrics.namespace, "SecurityEvents", "EventType", "authentication_success"],
                            [".", ".", ".", "authentication_failure"],
                            [".", ".", ".", "authorization_success"],
                            [".", ".", ".", "authorization_failure"],
                            [".", ".", ".", "data_access"],
                            [".", ".", ".", "sensitive_data_access"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.config.aws_region,
                        "title": "Security Events by Type",
                        "period": 300,
                        "stat": "Sum"
                    }
                },
                
                # Security Levels Distribution
                {
                    "type": "metric",
                    "x": 12, "y": 0, "width": 12, "height": 6,
                    "properties": {
                        "metrics": [
                            [self.config.metrics.namespace, "SecurityEvents", "SecurityLevel", "low"],
                            [".", ".", ".", "medium"],
                            [".", ".", ".", "high"],
                            [".", ".", ".", "critical"]
                        ],
                        "view": "pie",
                        "region": self.config.aws_region,
                        "title": "Security Events by Severity Level",
                        "period": 3600,
                        "stat": "Sum"
                    }
                },
                
                # Authentication Metrics
                {
                    "type": "metric",
                    "x": 0, "y": 6, "width": 8, "height": 6,
                    "properties": {
                        "metrics": [
                            [self.config.metrics.namespace, "SecurityEvents", "EventType", "authentication_success"],
                            [".", ".", ".", "authentication_failure"]
                        ],
                        "view": "timeSeries",
                        "stacked": True,
                        "region": self.config.aws_region,
                        "title": "Authentication Success vs Failure",
                        "period": 300,
                        "stat": "Sum"
                    }
                },
                
                # Security Logs Query
                {
                    "type": "log",
                    "x": 0, "y": 12, "width": 24, "height": 6,
                    "properties": {
                        "query": f"SOURCE '/aws/bedrock-workshop/security/{self.config.environment}'\n| fields @timestamp, log_type, data.event_type, data.security_level, data.user_id, data.resource\n| filter log_type = \"SecurityEvent\"\n| sort @timestamp desc\n| limit 100",
                        "region": self.config.aws_region,
                        "title": "Recent Security Events",
                        "view": "table"
                    }
                }
            ]
        }
        
        try:
            self._cloudwatch_client.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
            
            self._logger.info(f"Created security overview dashboard: {dashboard_name}")
def create_security_overview_dashboard(self) -> str:
        """
        Create a comprehensive security overview dashboard.
        
        Returns:
            str: Dashboard name
        """
        # Import html module for escaping
        # html.escape() is used to sanitize untrusted input before returning
        import html

        dashboard_name = f"BedrockWorkshop-Security-Overview-{self.config.environment}"
        
        dashboard_body = {
            "widgets": [
                # Security Events Overview
                {
                    "type": "metric",
                    "x": 0, "y": 0, "width": 12, "height": 6,
                    "properties": {
                        "metrics": [
                            [self.config.metrics.namespace, "SecurityEvents", "EventType", "authentication_success"],
                            [".", ".", ".", "authentication_failure"],
                            [".", ".", ".", "authorization_success"],
                            [".", ".", ".", "authorization_failure"],
                            [".", ".", ".", "data_access"],
                            [".", ".", ".", "sensitive_data_access"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.config.aws_region,
                        "title": "Security Events by Type",
                        "period": 300,
                        "stat": "Sum"
                    }
                },
                
                # Security Levels Distribution
                {
                    "type": "metric",
                    "x": 12, "y": 0, "width": 12, "height": 6,
                    "properties": {
                        "metrics": [
                            [self.config.metrics.namespace, "SecurityEvents", "SecurityLevel", "low"],
                            [".", ".", ".", "medium"],
                            [".", ".", ".", "high"],
                            [".", ".", ".", "critical"]
                        ],
                        "view": "pie",
                        "region": self.config.aws_region,
                        "title": "Security Events by Severity Level",
                        "period": 3600,
                        "stat": "Sum"
                    }
                },
                
                # Authentication Metrics
                {
                    "type": "metric",
                    "x": 0, "y": 6, "width": 8, "height": 6,
                    "properties": {
                        "metrics": [
                            [self.config.metrics.namespace, "SecurityEvents", "EventType", "authentication_success"],
                            [".", ".", ".", "authentication_failure"]
                        ],
                        "view": "timeSeries",
                        "stacked": True,
                        "region": self.config.aws_region,
                        "title": "Authentication Success vs Failure",
                        "period": 300,
                        "stat": "Sum"
                    }
                },
                
                # Security Logs Query
                {
                    "type": "log",
                    "x": 0, "y": 12, "width": 24, "height": 6,
                    "properties": {
                        "query": f"SOURCE '/aws/bedrock-workshop/security/{self.config.environment}'
| fields @timestamp, log_type, data.event_type, data.security_level, data.user_id, data.resource
| filter log_type = \"SecurityEvent\"
| sort @timestamp desc
| limit 100",
                        "region": self.config.aws_region,
                        "title": "Recent Security Events",
                        "view": "table"
                    }
                }
            ]
        }
        
        try:
            self._cloudwatch_client.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
            
            self._logger.info(f"Created security overview dashboard: {dashboard_name}")
            return html.escape(dashboard_name)
            
        except Exception as e:
            self._logger.error(f"Failed to create security overview dashboard: {e}")
            raise
            
        except Exception as e:
            self._logger.error(f"Failed to create security overview dashboard: {e}")
            raise
    
    def create_compliance_dashboard(self) -> str:
        """
        Create a compliance monitoring dashboard.
        
        Returns:
            str: Dashboard name
        """
        dashboard_name = f"BedrockWorkshop-Compliance-{self.config.environment}"
        
        dashboard_body = {
            "widgets": [
                # Compliance Scores
                {
                    "type": "metric",
                    "x": 0, "y": 0, "width": 12, "height": 6,
                    "properties": {
                        "metrics": [
                            [self.config.metrics.namespace, "ComplianceScore", "Framework", "soc2"],
                            [".", ".", ".", "gdpr"],
                            [".", ".", ".", "hipaa"],
                            [".", ".", ".", "iso27001"]
                        ],
                        "view": "timeSeries",
                        "stacked": False,
                        "region": self.config.aws_region,
                        "title": "Compliance Scores by Framework",
                        "period": 3600,
                        "stat": "Average",
                        "yAxis": {
                            "left": {
                                "min": 0,
                                "max": 100
                            }
                        }
                    }
                },
                
                # Audit Trail Coverage
                {
                    "type": "metric",
                    "x": 12, "y": 0, "width": 12, "height": 6,
                    "properties": {
                        "metrics": [
                            [self.config.metrics.namespace, "AuditTrailEntries", "ResourceType", "agent"],
                            [".", ".", ".", "configuration"],
                            [".", ".", ".", "data"],
                            [".", ".", ".", "user"]
                        ],
                        "view": "timeSeries",
                        "stacked": True,
                        "region": self.config.aws_region,
                        "title": "Audit Trail Entries by Resource Type",
                        "period": 300,
                        "stat": "Sum"
                    }
                }
            ]
        }
        
        try:
            self._cloudwatch_client.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
            
            self._logger.info(f"Created compliance dashboard: {dashboard_name}")
)
            
            self._logger.info(f"Created compliance dashboard: {dashboard_name}")
            return html.escape(dashboard_name)  # import html
            
        except Exception as e:
            self._logger.error(f"Failed to create compliance dashboard: {e}")
            
        except Exception as e:
            self._logger.error(f"Failed to create compliance dashboard: {e}")
            raise
    
    def create_security_alarms(self) -> List[str]:
        """
        Create CloudWatch alarms for security monitoring.
        
        Returns:
            List[str]: List of created alarm names
        """
        alarm_names = []
        
        # High severity security events alarm
        alarm_name = f"BedrockWorkshop-HighSeveritySecurityEvents-{self.config.environment}"
        try:
            self._cloudwatch_client.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=1,
                MetricName='SecurityEvents',
                Namespace=self.config.metrics.namespace,
                Period=300,
                Statistic='Sum',
                Threshold=5.0,
                ActionsEnabled=True,
                AlarmActions=[
                    self.config.health.sns_topic_arn
                ] if self.config.health.sns_topic_arn else [],
                AlarmDescription='Alert when high severity security events exceed threshold',
                Dimensions=[
                    {
                        'Name': 'SecurityLevel',
                        'Value': 'high'
                    }
                ],
                Unit='Count'
            )
            alarm_names.append(alarm_name)
            self._logger.info(f"Created alarm: {alarm_name}")
        except Exception as e:
            self._logger.error(f"Failed to create alarm {alarm_name}: {e}")
        
        return alarm_names
    
    def setup_all_security_dashboards(self) -> Dict[str, Any]:
        """
        Set up all security dashboards and alarms.
        
        Returns:
            Dict[str, Any]: Dictionary mapping dashboard types to names
        """
        dashboards = {}
        
        try:
            dashboards['overview'] = self.create_security_overview_dashboard()
            dashboards['compliance'] = self.create_compliance_dashboard()
            
            # Create alarms
            alarm_names = self.create_security_alarms()
            dashboards['alarms'] = alarm_names
            
            self._logger.info("All security dashboards and alarms created successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to setup security dashboards: {e}")
            raise
        
        return dashboards


def create_security_dashboard_service(config: ObservabilityConfig) -> SecurityDashboardService:
    """
    Factory function to create a SecurityDashboardService instance.
    
    Args:
        config: Observability configuration
        
    Returns:
        SecurityDashboardService: Configured security dashboard service
    """
    return SecurityDashboardService(config)
