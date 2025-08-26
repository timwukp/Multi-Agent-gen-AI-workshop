"""
Test suite for security monitoring and compliance functionality.

This module tests the SecurityMonitor class and related security monitoring
components including audit trails, compliance reporting, and anomaly detection.
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Local imports
from src.observability.config import ObservabilityConfig, create_observability_config
from src.observability.security import (
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
from src.observability.security_dashboards import (
    SecurityDashboardService,
    create_security_dashboard_service
)
from src.observability.metrics import MetricsCollector


class TestSecurityMonitor:
    """Test cases for SecurityMonitor class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock observability configuration."""
        config = create_observability_config()
        config.environment = "development"
        config.aws_region = "us-west-2"
        config.aws_profile = None
        return config
    
    @pytest.fixture
    def mock_metrics_collector(self):
        """Create a mock metrics collector."""
        return Mock(spec=MetricsCollector)
    
    @pytest.fixture
    def mock_aws_clients(self):
        """Mock AWS service clients."""
        with patch('boto3.Session') as mock_session:
            mock_cloudwatch_logs = Mock()
            mock_cloudtrail = Mock()
            mock_sns = Mock()
            
            mock_session.return_value.client.side_effect = lambda service: {
                'logs': mock_cloudwatch_logs,
                'cloudtrail': mock_cloudtrail,
                'sns': mock_sns
            }[service]
            
            yield {
                'logs': mock_cloudwatch_logs,
                'cloudtrail': mock_cloudtrail,
                'sns': mock_sns
            }
    
    @pytest.fixture
    def security_monitor(self, mock_config, mock_metrics_collector, mock_aws_clients):
        """Create a SecurityMonitor instance for testing."""
        return SecurityMonitor(mock_config, mock_metrics_collector)
    
    def test_security_monitor_initialization(self, mock_config, mock_metrics_collector, mock_aws_clients):
        """Test SecurityMonitor initialization."""
        monitor = SecurityMonitor(mock_config, mock_metrics_collector)
        
        assert monitor.config == mock_config
        assert monitor.metrics_collector == mock_metrics_collector
        assert monitor._security_events == []
        assert monitor._audit_trails == []
        assert monitor._security_anomalies == []
    
    def test_log_authentication_success(self, security_monitor):
        """Test logging successful authentication events."""
        event_id = security_monitor.log_authentication_event(
            user_id="test_user",
            success=True,
            user_email="test@example.com",
            source_ip="192.168.1.1",
            session_id="session_123"
        )
        
        assert event_id is not None
        assert len(security_monitor._security_events) == 1
        
        event = security_monitor._security_events[0]
        assert event.event_type == SecurityEventType.AUTHENTICATION_SUCCESS
        assert event.user_id == "test_user"
        assert event.user_email == "test@example.com"
        assert event.source_ip == "192.168.1.1"
        assert event.result == "success"
        assert event.security_level == SecurityLevel.LOW
    
    def test_log_authentication_failure(self, security_monitor):
        """Test logging failed authentication events."""
        event_id = security_monitor.log_authentication_event(
            user_id="test_user",
            success=False,
            source_ip="192.168.1.1",
            details={"reason": "invalid_password"}
        )
        
        assert event_id is not None
        assert len(security_monitor._security_events) == 1
        
        event = security_monitor._security_events[0]
        assert event.event_type == SecurityEventType.AUTHENTICATION_FAILURE
        assert event.result == "failure"
        assert event.security_level == SecurityLevel.MEDIUM
        assert event.details["reason"] == "invalid_password"
    
    def test_log_authorization_event(self, security_monitor):
        """Test logging authorization events."""
        event_id = security_monitor.log_authorization_event(
            user_id="test_user",
            resource="/api/data",
            action="read",
            success=True,
            user_email="test@example.com"
        )
        
        assert event_id is not None
        assert len(security_monitor._security_events) == 1
        
        event = security_monitor._security_events[0]
        assert event.event_type == SecurityEventType.AUTHORIZATION_SUCCESS
        assert event.resource == "/api/data"
        assert event.action == "read"
        assert event.result == "success"
    
    def test_log_data_access_event(self, security_monitor):
        """Test logging data access events."""
        # Test regular data access
        event_id = security_monitor.log_data_access_event(
            user_id="test_user",
            resource="/data/reports",
            action="read",
            is_sensitive=False
        )
        
        assert event_id is not None
        assert len(security_monitor._security_events) == 1
        
        event = security_monitor._security_events[0]
        assert event.event_type == SecurityEventType.DATA_ACCESS
        assert event.security_level == SecurityLevel.LOW
        
        # Test sensitive data access
        event_id = security_monitor.log_data_access_event(
            user_id="test_user",
            resource="/data/pii",
            action="read",
            is_sensitive=True
        )
        
        assert len(security_monitor._security_events) == 2
        
        sensitive_event = security_monitor._security_events[1]
        assert sensitive_event.event_type == SecurityEventType.SENSITIVE_DATA_ACCESS
        assert sensitive_event.security_level == SecurityLevel.HIGH
        assert ComplianceFramework.GDPR in sensitive_event.compliance_frameworks
    
    def test_create_audit_trail(self, security_monitor):
        """Test creating audit trail entries."""
        audit_id = security_monitor.create_audit_trail(
            user_id="test_user",
            action="update_configuration",
            resource="/config/settings",
            resource_type="configuration",
            old_value={"setting": "old_value"},
            new_value={"setting": "new_value"}
        )
        
        assert audit_id is not None
        assert len(security_monitor._audit_trails) == 1
        
        audit = security_monitor._audit_trails[0]
        assert audit.user_id == "test_user"
        assert audit.action == "update_configuration"
        assert audit.resource == "/config/settings"
        assert audit.resource_type == "configuration"
        assert audit.old_value == {"setting": "old_value"}
        assert audit.new_value == {"setting": "new_value"}
    
    def test_log_security_alert(self, security_monitor):
        """Test logging security alerts."""
        event_id = security_monitor.log_security_alert(
            alert_type="suspicious_activity",
            description="Multiple failed login attempts detected",
            security_level=SecurityLevel.HIGH,
            user_id="test_user",
            details={"attempts": 5}
        )
        
        assert event_id is not None
        assert len(security_monitor._security_events) == 1
        
        event = security_monitor._security_events[0]
        assert event.event_type == SecurityEventType.SECURITY_ALERT
        assert event.security_level == SecurityLevel.HIGH
        assert event.details["alert_type"] == "suspicious_activity"
        assert event.details["description"] == "Multiple failed login attempts detected"
    
    def test_failed_authentication_anomaly_detection(self, security_monitor):
        """Test detection of failed authentication anomalies."""
        # Log multiple failed authentication attempts
        for i in range(6):  # Exceeds threshold of 5
            security_monitor.log_authentication_event(
                user_id="test_user",
                success=False,
                source_ip="192.168.1.1"
            )
        
        # Check that anomaly was detected
        assert len(security_monitor._security_anomalies) == 1
        
        anomaly = security_monitor._security_anomalies[0]
        assert anomaly.anomaly_type == "excessive_failed_authentication"
        assert anomaly.security_level == SecurityLevel.HIGH
        assert anomaly.affected_user == "test_user"
        assert anomaly.confidence_score == 0.9
    
    def test_detect_anomalies(self, security_monitor):
        """Test comprehensive anomaly detection."""
        # Create privilege escalation pattern
        for i in range(4):  # Exceeds threshold of 3
            security_monitor.log_authorization_event(
                user_id="test_user",
                resource="/admin/privileges",
                action="privilege_escalation",
                success=True
            )
        
        # Create unusual access pattern
        for i in range(25):  # Exceeds threshold of 20 resources
            security_monitor.log_data_access_event(
                user_id="test_user2",
                resource=f"/data/resource_{i}",
                action="read"
            )
        
        anomalies = security_monitor.detect_anomalies()
        
        assert len(anomalies) >= 2
        
        # Check for privilege escalation anomaly
        privilege_anomaly = next((a for a in anomalies if a.anomaly_type == "privilege_escalation_pattern"), None)
        assert privilege_anomaly is not None
        assert privilege_anomaly.affected_user == "test_user"
        
        # Check for unusual access pattern anomaly
        access_anomaly = next((a for a in anomalies if a.anomaly_type == "unusual_access_pattern"), None)
        assert access_anomaly is not None
        assert access_anomaly.affected_user == "test_user2"
    
    def test_generate_soc2_compliance_report(self, security_monitor):
        """Test SOC 2 compliance report generation."""
        # Create some test events
        security_monitor.log_authentication_event(
            user_id="test_user",
            success=False,
            details={}  # Missing reason - should be a violation
        )
        
        security_monitor.log_data_access_event(
            user_id="test_user",
            resource="/data/sensitive",
            action="read"
        )
        
        start_date = datetime.now(timezone.utc) - timedelta(days=1)
        end_date = datetime.now(timezone.utc)
        
        report = security_monitor.generate_compliance_report(
            framework=ComplianceFramework.SOC2,
            start_date=start_date,
            end_date=end_date
        )
        
        assert report.framework == ComplianceFramework.SOC2
        assert report.total_events > 0
        assert report.compliance_score <= 1.0
        assert len(report.violations) > 0
        assert len(report.recommendations) > 0
    
    def test_generate_gdpr_compliance_report(self, security_monitor):
        """Test GDPR compliance report generation."""
        # Create sensitive data access without consent
        security_monitor.log_data_access_event(
            user_id="test_user",
            resource="/data/pii",
            action="read",
            is_sensitive=True,
            details={}  # Missing consent_id - should be a violation
        )
        
        start_date = datetime.now(timezone.utc) - timedelta(days=1)
        end_date = datetime.now(timezone.utc)
        
        report = security_monitor.generate_compliance_report(
            framework=ComplianceFramework.GDPR,
            start_date=start_date,
            end_date=end_date
        )
        
        assert report.framework == ComplianceFramework.GDPR
        assert len(report.violations) > 0
        
        # Check for missing consent violation
        consent_violation = next((v for v in report.violations if v["type"] == "missing_consent"), None)
        assert consent_violation is not None
    
    def test_input_sanitization(self, security_monitor):
        """Test input sanitization to prevent injection attacks."""
        malicious_input = "<script>alert('xss')</script>"
        
        event_id = security_monitor.log_authentication_event(
            user_id=malicious_input,
            success=True,
            details={"malicious": malicious_input}
        )
        
        event = security_monitor._security_events[0]
        
        # Check that dangerous characters are removed
        assert "<script>" not in event.user_id
        assert "alert" not in event.user_id
        assert "<script>" not in str(event.details)
    
    def test_get_security_summary(self, security_monitor):
        """Test security summary generation."""
        # Create various types of events
        security_monitor.log_authentication_event("user1", True)
        security_monitor.log_authentication_event("user2", False)
        security_monitor.log_authorization_event("user1", "/data", "read", True)
        security_monitor.log_data_access_event("user1", "/data", "read", is_sensitive=True)
        security_monitor.log_security_alert("test_alert", "Test alert", SecurityLevel.HIGH)
        
        summary = security_monitor.get_security_summary()
        
        assert summary["total_events"] == 5
        assert summary["events_by_type"]["authentication_success"] == 1
        assert summary["events_by_type"]["authentication_failure"] == 1
        assert summary["high_severity_events"] == 2  # sensitive data access + security alert
        assert summary["failed_authentications"] == 1
        assert summary["data_access_events"] == 1


class TestSecurityDashboardService:
    """Test cases for SecurityDashboardService class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock observability configuration."""
        config = create_observability_config()
        config.environment = "development"
        config.aws_region = "us-west-2"
        config.aws_profile = None
        return config
    
    @pytest.fixture
    def mock_aws_clients(self):
        """Mock AWS service clients."""
        with patch('boto3.Session') as mock_session:
            mock_cloudwatch = Mock()
            mock_logs = Mock()
            
            mock_session.return_value.client.side_effect = lambda service: {
                'cloudwatch': mock_cloudwatch,
                'logs': mock_logs
            }[service]
            
            yield {
                'cloudwatch': mock_cloudwatch,
                'logs': mock_logs
            }
    
    @pytest.fixture
    def dashboard_service(self, mock_config, mock_aws_clients):
        """Create a SecurityDashboardService instance for testing."""
        return SecurityDashboardService(mock_config)
    
    def test_dashboard_service_initialization(self, mock_config, mock_aws_clients):
        """Test SecurityDashboardService initialization."""
        service = SecurityDashboardService(mock_config)
        
        assert service.config == mock_config
        assert service._cloudwatch_client is not None
        assert service._logs_client is not None
    
    def test_create_security_overview_dashboard(self, dashboard_service, mock_aws_clients):
        """Test creation of security overview dashboard."""
        dashboard_name = dashboard_service.create_security_overview_dashboard()
        
        assert "BedrockWorkshop-Security-Overview-development" in dashboard_name
        
        # Verify CloudWatch put_dashboard was called
        mock_aws_clients['cloudwatch'].put_dashboard.assert_called_once()
        
        # Check dashboard configuration
        call_args = mock_aws_clients['cloudwatch'].put_dashboard.call_args
        dashboard_body = json.loads(call_args[1]['DashboardBody'])
        
        assert 'widgets' in dashboard_body
        assert len(dashboard_body['widgets']) > 0
    
    def test_create_compliance_dashboard(self, dashboard_service, mock_aws_clients):
        """Test creation of compliance dashboard."""
        dashboard_name = dashboard_service.create_compliance_dashboard()
        
        assert "BedrockWorkshop-Compliance-development" in dashboard_name
        
        # Verify CloudWatch put_dashboard was called
        mock_aws_clients['cloudwatch'].put_dashboard.assert_called_once()
    
    def test_create_security_alarms(self, dashboard_service, mock_aws_clients):
        """Test creation of security alarms."""
        alarm_names = dashboard_service.create_security_alarms()
        
        assert len(alarm_names) > 0
        
        # Verify CloudWatch put_metric_alarm was called multiple times
        assert mock_aws_clients['cloudwatch'].put_metric_alarm.call_count >= 1
    
    def test_setup_all_security_dashboards(self, dashboard_service, mock_aws_clients):
        """Test setup of all security dashboards."""
        dashboards = dashboard_service.setup_all_security_dashboards()
        
        assert 'overview' in dashboards
        assert 'compliance' in dashboards
        assert 'alarms' in dashboards
        
        # Verify multiple CloudWatch calls were made
        assert mock_aws_clients['cloudwatch'].put_dashboard.call_count >= 2
        assert mock_aws_clients['cloudwatch'].put_metric_alarm.call_count >= 1


if __name__ == "__main__":
    # Run basic functionality test
    print("Testing SecurityMonitor functionality...")
    
    try:
        # Create test configuration
        config = create_observability_config()
        config.environment = "development"
        
        with patch('boto3.Session'):
            # Test security monitor creation
            monitor = create_security_monitor(config)
            print("✓ SecurityMonitor created successfully")
            
            # Test event logging
            event_id = monitor.log_authentication_event(
                user_id="test_user",
                success=True,
                user_email="test@example.com"
            )
            print(f"✓ Authentication event logged: {event_id}")
            
            # Test audit trail creation
            audit_id = monitor.create_audit_trail(
                user_id="test_user",
                action="test_action",
                resource="/test/resource",
                resource_type="test"
            )
            print(f"✓ Audit trail created: {audit_id}")
            
            # Test security summary
            summary = monitor.get_security_summary()
            print(f"✓ Security summary generated: {summary['total_events']} events")
            
            # Test dashboard service creation
            dashboard_service = create_security_dashboard_service(config)
            print("✓ SecurityDashboardService created successfully")
            
            print("\n🎉 All security monitoring tests passed!")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
