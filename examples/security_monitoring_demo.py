"""
Security monitoring and compliance demonstration for AWS Bedrock Workshop.

This demo shows how to use the SecurityMonitor class for comprehensive
security monitoring, audit trails, compliance reporting, and anomaly detection.
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

# Add parent directory to path for imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Local imports
from src.observability.config import create_observability_config
from src.observability.security import (
    SecurityMonitor,
    SecurityEventType,
    SecurityLevel,
    ComplianceFramework,
    create_security_monitor
)
from src.observability.security_dashboards import create_security_dashboard_service
from src.observability.metrics import MetricsCollector


class SecurityMonitoringDemo:
    """Demonstration of security monitoring capabilities."""
    
    def __init__(self):
        """Initialize the demo with observability configuration."""
        self.config = create_observability_config()
        self.config.environment = "development"
        
        # Initialize components
        self.metrics_collector = None
        try:
            self.metrics_collector = MetricsCollector(self.config.metrics)
        except Exception as e:
            print(f"Warning: Could not initialize metrics collector: {e}")
        
        self.security_monitor = create_security_monitor(self.config, self.metrics_collector)
        
        try:
            self.dashboard_service = create_security_dashboard_service(self.config)
        except Exception as e:
            print(f"Warning: Could not initialize dashboard service: {e}")
            self.dashboard_service = None
    
    def demonstrate_authentication_logging(self):
        """Demonstrate authentication event logging."""
        print("\n=== Authentication Event Logging Demo ===")
        
        # Successful authentication
        success_event_id = self.security_monitor.log_authentication_event(
            user_id="alice@company.com",
            success=True,
            user_email="alice@company.com",
            source_ip="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            session_id="sess_abc123",
            trace_id="trace_xyz789",
            details={
                "authentication_method": "oauth2",
                "provider": "cognito",
                "mfa_enabled": True
            }
        )
        print(f"✓ Successful authentication logged: {success_event_id}")
        
        # Failed authentication attempts
        for i in range(3):
            failure_event_id = self.security_monitor.log_authentication_event(
                user_id="bob@company.com",
                success=False,
                source_ip="10.0.1.50",
                details={
                    "reason": "invalid_password",
                    "attempt_number": i + 1,
                    "authentication_method": "password"
                }
            )
            print(f"✓ Failed authentication attempt {i+1} logged: {failure_event_id}")
    
    def demonstrate_authorization_logging(self):
        """Demonstrate authorization event logging."""
        print("\n=== Authorization Event Logging Demo ===")
        
        # Successful authorization
        auth_success_id = self.security_monitor.log_authorization_event(
            user_id="alice@company.com",
            resource="/api/financial-data",
            action="read",
            success=True,
            user_email="alice@company.com",
            source_ip="192.168.1.100",
            session_id="sess_abc123",
            details={
                "role": "financial_analyst",
                "permissions": ["read_financial_data", "generate_reports"]
            }
        )
        print(f"✓ Successful authorization logged: {auth_success_id}")
        
        # Failed authorization
        auth_failure_id = self.security_monitor.log_authorization_event(
            user_id="bob@company.com",
            resource="/api/admin-panel",
            action="write",
            success=False,
            source_ip="10.0.1.50",
            details={
                "role": "user",
                "required_role": "admin",
                "reason": "insufficient_privileges"
            }
        )
        print(f"✓ Failed authorization logged: {auth_failure_id}")
    
    def demonstrate_data_access_logging(self):
        """Demonstrate data access event logging."""
        print("\n=== Data Access Event Logging Demo ===")
        
        # Regular data access
        data_access_id = self.security_monitor.log_data_access_event(
            user_id="alice@company.com",
            resource="/data/quarterly-reports",
            action="read",
            is_sensitive=False,
            user_email="alice@company.com",
            source_ip="192.168.1.100",
            details={
                "file_name": "Q3_2024_report.pdf",
                "file_size": "2.5MB",
                "access_method": "api"
            }
        )
        print(f"✓ Regular data access logged: {data_access_id}")
        
        # Sensitive data access
        sensitive_access_id = self.security_monitor.log_data_access_event(
            user_id="alice@company.com",
            resource="/data/customer-pii",
            action="read",
            is_sensitive=True,
            user_email="alice@company.com",
            source_ip="192.168.1.100",
            details={
                "data_type": "pii",
                "customer_count": 1000,
                "consent_id": "consent_12345",
                "purpose": "financial_analysis"
            }
        )
        print(f"✓ Sensitive data access logged: {sensitive_access_id}")
    
    def demonstrate_audit_trails(self):
        """Demonstrate audit trail creation."""
        print("\n=== Audit Trail Demo ===")
        
        # Configuration change audit
        config_audit_id = self.security_monitor.create_audit_trail(
            user_id="admin@company.com",
            action="update_security_policy",
            resource="/config/security-policy",
            resource_type="configuration",
            user_email="admin@company.com",
            old_value={
                "password_policy": {
                    "min_length": 8,
                    "require_special_chars": False
                }
            },
            new_value={
                "password_policy": {
                    "min_length": 12,
                    "require_special_chars": True
                }
            },
            source_ip="192.168.1.10",
            compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.ISO27001]
        )
        print(f"✓ Configuration change audit trail created: {config_audit_id}")
        
        # User privilege change audit
        privilege_audit_id = self.security_monitor.create_audit_trail(
            user_id="admin@company.com",
            action="privilege_escalation",
            resource="/users/alice@company.com",
            resource_type="user",
            old_value={"role": "analyst", "permissions": ["read_data"]},
            new_value={"role": "senior_analyst", "permissions": ["read_data", "export_data"]},
            compliance_frameworks=[ComplianceFramework.SOC2]
        )
        print(f"✓ Privilege change audit trail created: {privilege_audit_id}")
    
    def demonstrate_security_alerts(self):
        """Demonstrate security alert logging."""
        print("\n=== Security Alerts Demo ===")
        
        # Suspicious activity alert
        suspicious_alert_id = self.security_monitor.log_security_alert(
            alert_type="suspicious_login_pattern",
            description="User logged in from multiple geographic locations within 1 hour",
            security_level=SecurityLevel.HIGH,
            user_id="bob@company.com",
            details={
                "locations": ["New York, US", "London, UK", "Tokyo, JP"],
                "time_span": "45 minutes",
                "confidence": 0.85
            }
        )
        print(f"✓ Suspicious activity alert logged: {suspicious_alert_id}")
        
        # Data breach attempt alert
        breach_alert_id = self.security_monitor.log_security_alert(
            alert_type="potential_data_breach",
            description="Unauthorized attempt to access sensitive customer data",
            security_level=SecurityLevel.CRITICAL,
            user_id="unknown_user",
            resource="/data/customer-pii",
            source_ip="198.51.100.42",
            details={
                "attack_vector": "sql_injection",
                "blocked": True,
                "affected_records": 0
            }
        )
        print(f"✓ Data breach attempt alert logged: {breach_alert_id}")
    
    def demonstrate_anomaly_detection(self):
        """Demonstrate comprehensive anomaly detection."""
        print("\n=== Anomaly Detection Demo ===")
        
        print("Running anomaly detection on recent events...")
        anomalies = self.security_monitor.detect_anomalies()
        
        print(f"✓ Detected {len(anomalies)} security anomalies:")
        
        for anomaly in anomalies:
            print(f"  - {anomaly.anomaly_type}: {anomaly.description}")
            print(f"    Security Level: {anomaly.security_level.value}")
            print(f"    Confidence: {anomaly.confidence_score:.2f}")
            if anomaly.affected_user:
                print(f"    Affected User: {anomaly.affected_user}")
            print(f"    Mitigation Actions: {', '.join(anomaly.mitigation_actions)}")
            print()
    
    def demonstrate_compliance_reporting(self):
        """Demonstrate compliance report generation."""
        print("\n=== Compliance Reporting Demo ===")
        
        # Generate reports for different frameworks
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(hours=1)  # Last hour of activity
        
        frameworks = [
            ComplianceFramework.SOC2,
            ComplianceFramework.GDPR,
            ComplianceFramework.ISO27001
        ]
        
        for framework in frameworks:
            print(f"\n--- {framework.value.upper()} Compliance Report ---")
            
            report = self.security_monitor.generate_compliance_report(
                framework=framework,
                start_date=start_date,
                end_date=end_date
            )
            
            print(f"Report ID: {report.report_id}")
            print(f"Report Period: {report.report_period_start.strftime('%Y-%m-%d %H:%M')} to {report.report_period_end.strftime('%Y-%m-%d %H:%M')}")
            print(f"Total Events: {report.total_events}")
            print(f"Compliant Events: {report.compliant_events}")
            print(f"Non-Compliant Events: {report.non_compliant_events}")
            print(f"Compliance Score: {report.compliance_score:.2%}")
            
            if report.violations:
                print(f"Violations ({len(report.violations)}):")
                for violation in report.violations[:3]:  # Show first 3
                    print(f"  - {violation['type']}: {violation['description']} (Severity: {violation['severity']})")
                if len(report.violations) > 3:
                    print(f"  ... and {len(report.violations) - 3} more")
            
            if report.recommendations:
                print(f"Recommendations ({len(report.recommendations)}):")
                for rec in report.recommendations[:2]:  # Show first 2
                    print(f"  - {rec}")
                if len(report.recommendations) > 2:
                    print(f"  ... and {len(report.recommendations) - 2} more")
    
    def demonstrate_security_summary(self):
        """Demonstrate security summary generation."""
        print("\n=== Security Summary Demo ===")
        
        summary = self.security_monitor.get_security_summary()
        
        print("Security Summary (Last 24 Hours):")
        print(f"  Total Events: {summary['total_events']}")
        print(f"  Total Anomalies: {summary['total_anomalies']}")
        print(f"  High Severity Events: {summary['high_severity_events']}")
        print(f"  Failed Authentications: {summary['failed_authentications']}")
        print(f"  Data Access Events: {summary['data_access_events']}")
        print(f"  Audit Trails Created: {summary['audit_trails_created']}")
        
        print("\nEvents by Type:")
        for event_type, count in summary['events_by_type'].items():
            print(f"  {event_type}: {count}")
        
        print("\nEvents by Security Level:")
        for level, count in summary['events_by_security_level'].items():
            print(f"  {level}: {count}")
        
        print(f"\nActive Compliance Frameworks: {', '.join(summary['compliance_frameworks_active'])}")
    
    def demonstrate_dashboard_creation(self):
        """Demonstrate security dashboard creation."""
        print("\n=== Security Dashboard Creation Demo ===")
        
        if not self.dashboard_service:
            print("⚠️  Dashboard service not available (AWS credentials may not be configured)")
            return
        
        try:
            # Create all security dashboards
            dashboards = self.dashboard_service.setup_all_security_dashboards()
            
            print("✓ Security dashboards created successfully:")
            for dashboard_type, name in dashboards.items():
                if dashboard_type != 'alarms':
                    print(f"  - {dashboard_type.title()}: {name}")
            
            if 'alarms' in dashboards:
                print(f"  - Alarms: {len(dashboards['alarms'])} created")
            
        except Exception as e:
            print(f"⚠️  Could not create dashboards: {e}")
            print("This is expected if AWS credentials are not configured for CloudWatch access")
    
    def run_full_demo(self):
        """Run the complete security monitoring demonstration."""
        print("🔒 AWS Bedrock Workshop - Security Monitoring Demo")
        print("=" * 60)
        
        try:
            # Run all demonstrations
            self.demonstrate_authentication_logging()
            self.demonstrate_authorization_logging()
            self.demonstrate_data_access_logging()
            self.demonstrate_audit_trails()
            self.demonstrate_security_alerts()
            self.demonstrate_anomaly_detection()
            self.demonstrate_compliance_reporting()
            self.demonstrate_security_summary()
            self.demonstrate_dashboard_creation()
            
            print("\n" + "=" * 60)
            print("🎉 Security monitoring demo completed successfully!")
            print("\nKey Features Demonstrated:")
            print("✓ Authentication and authorization event logging")
            print("✓ Data access tracking with sensitivity classification")
            print("✓ Comprehensive audit trail generation")
            print("✓ Security alert management")
            print("✓ Automated anomaly detection")
            print("✓ Multi-framework compliance reporting")
            print("✓ Security dashboard and alerting setup")
            
            # Cleanup demonstration
            print(f"\n📊 Demo Statistics:")
            print(f"  Security Events: {len(self.security_monitor._security_events)}")
            print(f"  Audit Trails: {len(self.security_monitor._audit_trails)}")
            print(f"  Anomalies Detected: {len(self.security_monitor._security_anomalies)}")
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            raise


def main():
    """Main function to run the security monitoring demo."""
    demo = SecurityMonitoringDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main()
