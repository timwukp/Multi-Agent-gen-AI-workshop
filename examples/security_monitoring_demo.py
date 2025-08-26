#!/usr/bin/env python3
"""
Security monitoring demo for AWS Bedrock Workshop.

This script demonstrates the security monitoring capabilities including
event logging, anomaly detection, and compliance reporting.
"""

import asyncio
import sys
import os
import time
from typing import Dict, Any
from datetime import datetime, timezone

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from observability.security import (
    SecurityMonitor, SecurityEvent, SecurityEventType, SecurityLevel,
    AuditTrail, ComplianceFramework, create_security_monitor
)
from observability.config import create_observability_config


class SecureFinancialAgent:
    """
    Financial agent with integrated security monitoring.
    
    Demonstrates how to add security event logging and audit trails
    to existing agent operations.
    """
    
    def __init__(self, name: str = "SecureFinancialAgent"):
        self.name = name
        self.security_monitor = create_security_monitor()
        print(f"✅ {self.name} initialized with security monitoring")
    
    async def authenticate_user(self, user_id: str, credentials: str) -> bool:
        """Simulate user authentication with security logging."""
        print(f"🔐 Authenticating user: {user_id}")
        
        # Simulate authentication logic
        success = len(credentials) > 5  # Simple validation
        
        # Log authentication event
        await self.security_monitor.log_authentication_event(
            user_id=user_id,
            success=success,
            source_ip="192.168.1.100",
            user_agent="BedrocWorkshop-Agent/1.0",
            details={"method": "api_key", "timestamp": datetime.now(timezone.utc).isoformat()}
        )
        
        return success
    
    async def access_financial_data(self, user_id: str, resource: str, is_sensitive: bool = False) -> Dict[str, Any]:
        """Access financial data with audit trail logging."""
        print(f"📄 Accessing {resource} for user: {user_id}")
        
        # Log data access event
        await self.security_monitor.log_data_access_event(
            user_id=user_id,
            resource=resource,
            action="read",
            is_sensitive=is_sensitive,
            source_ip="192.168.1.100",
            details={"query_type": "financial_analysis"}
        )
        
        # Create audit trail
        await self.security_monitor.create_audit_trail(
            user_id=user_id,
            action="data_access",
            resource=resource,
            resource_type="financial_data",
            details={"access_method": "api", "data_classification": "sensitive" if is_sensitive else "internal"}
        )
        
        # Simulate data retrieval
        return {
            "resource": resource,
            "data": f"Financial data for {resource}",
            "access_time": datetime.now(timezone.utc).isoformat(),
            "classification": "sensitive" if is_sensitive else "internal"
        }
    
    async def modify_configuration(self, user_id: str, config_key: str, old_value: Any, new_value: Any) -> bool:
        """Modify configuration with security logging."""
        print(f"⚙️ Modifying configuration: {config_key}")
        
        # Log configuration change
        await self.security_monitor.log_configuration_change(
            user_id=user_id,
            resource=f"config.{config_key}",
            old_value=old_value,
            new_value=new_value,
            source_ip="192.168.1.100"
        )
        
        return True


async def demo_authentication_monitoring():
    """Demonstrate authentication monitoring."""
    print("\n" + "=" * 50)
    print("AUTHENTICATION MONITORING DEMO")
    print("=" * 50)
    
    agent = SecureFinancialAgent("AuthDemo")
    
    # Test successful and failed authentications
    test_cases = [
        ("user123", "valid_password", True),
        ("user456", "short", False),
        ("user789", "another_valid_password", True),
        ("user123", "wrong", False),  # Failed attempt for same user
        ("user123", "wrong2", False),  # Another failed attempt
    ]
    
    for user_id, password, expected in test_cases:
        result = await agent.authenticate_user(user_id, password)
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"   {user_id}: {status}")
        
        # Small delay between attempts
        await asyncio.sleep(0.1)


async def demo_data_access_monitoring():
    """Demonstrate data access monitoring."""
    print("\n" + "=" * 50)
    print("DATA ACCESS MONITORING DEMO")
    print("=" * 50)
    
    agent = SecureFinancialAgent("DataDemo")
    
    # Test different types of data access
    access_scenarios = [
        ("user123", "amazon/revenue/q1_2025", False),
        ("user456", "amazon/financial_statements/2025", True),  # Sensitive
        ("user789", "amazon/public_metrics", False),
        ("user123", "amazon/internal_forecasts", True),  # Sensitive
    ]
    
    for user_id, resource, is_sensitive in access_scenarios:
        result = await agent.access_financial_data(user_id, resource, is_sensitive)
        sensitivity = "🔒 SENSITIVE" if is_sensitive else "📄 REGULAR"
        print(f"   {user_id} accessed {resource}: {sensitivity}")
        
        await asyncio.sleep(0.1)


async def demo_configuration_monitoring():
    """Demonstrate configuration change monitoring."""
    print("\n" + "=" * 50)
    print("CONFIGURATION MONITORING DEMO")
    print("=" * 50)
    
    agent = SecureFinancialAgent("ConfigDemo")
    
    # Test configuration changes
    config_changes = [
        ("admin_user", "max_query_limit", 100, 200),
        ("admin_user", "enable_debug_mode", False, True),
        ("user123", "user_preferences.theme", "light", "dark"),
        ("admin_user", "security_level", "medium", "high"),
    ]
    
    for user_id, config_key, old_val, new_val in config_changes:
        await agent.modify_configuration(user_id, config_key, old_val, new_val)
        print(f"   {user_id} changed {config_key}: {old_val} → {new_val}")
        
        await asyncio.sleep(0.1)


async def demo_anomaly_detection():
    """Demonstrate anomaly detection."""
    print("\n" + "=" * 50)
    print("ANOMALY DETECTION DEMO")
    print("=" * 50)
    
    security_monitor = create_security_monitor()
    
    # Simulate suspicious activity patterns
    print("🔍 Simulating suspicious activity patterns...")
    
    # Multiple failed authentications from same user
    for i in range(6):  # Exceeds threshold of 5
        await security_monitor.log_authentication_event(
            user_id="suspicious_user",
            success=False,
            source_ip="192.168.1.200",
            details={"attempt": i + 1}
        )
    
    # High-frequency requests from single IP
    for i in range(12):  # Exceeds threshold of 10
        await security_monitor.log_data_access_event(
            user_id=f"user_{i % 3}",
            resource="amazon/data",
            action="read",
            source_ip="192.168.1.300",
            details={"request": i + 1}
        )
    
    # Check for anomalies
    anomalies = await security_monitor.detect_anomalies()
    
    print(f"🚨 Detected {len(anomalies)} security anomalies:")
    for anomaly in anomalies:
        print(f"   - {anomaly.anomaly_type}: {anomaly.description} (Confidence: {anomaly.confidence_score:.2f})")


async def demo_compliance_reporting():
    """Demonstrate compliance reporting."""
    print("\n" + "=" * 50)
    print("COMPLIANCE REPORTING DEMO")
    print("=" * 50)
    
    security_monitor = create_security_monitor()
    
    # Generate compliance reports for different frameworks
    frameworks = [ComplianceFramework.SOC2, ComplianceFramework.GDPR, ComplianceFramework.ISO27001]
    
    for framework in frameworks:
        print(f"📄 Generating {framework.value.upper()} compliance report...")
        
        report = await security_monitor.generate_compliance_report(
            framework=framework,
            start_date=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=datetime.now(timezone.utc)
        )
        
        print(f"   Compliance Score: {report.compliance_score:.1%}")
        print(f"   Total Events: {report.total_events}")
        print(f"   Compliant Events: {report.compliant_events}")
        print(f"   Violations: {report.non_compliant_events}")
        
        if report.violations:
            print(f"   Top Violations:")
            for violation in report.violations[:3]:
                print(f"     - {violation.get('type', 'Unknown')}: {violation.get('count', 0)} occurrences")


async def main():
    """Main demo function."""
    print("🚀 Starting Security Monitoring Demo")
    print("This demo shows comprehensive security monitoring capabilities\n")
    
    try:
        # Initialize configuration
        config = create_observability_config()
        print(f"🔒 Security monitoring configured for environment: {config.environment}")
        
        # Run demo sections
        await demo_authentication_monitoring()
        await demo_data_access_monitoring()
        await demo_configuration_monitoring()
        await demo_anomaly_detection()
        await demo_compliance_reporting()
        
        print("\n" + "=" * 60)
        print("🎉 SECURITY MONITORING DEMO COMPLETED!")
        print("=" * 60)
        
        print("\n📋 What was demonstrated:")
        print("   ✅ Authentication event logging with success/failure tracking")
        print("   ✅ Data access monitoring with sensitivity classification")
        print("   ✅ Configuration change audit trails")
        print("   ✅ Real-time anomaly detection with configurable thresholds")
        print("   ✅ Automated compliance reporting for multiple frameworks")
        
        print("\n🔍 Security features:")
        print("   ✅ Input validation and sanitization")
        print("   ✅ Rate limiting and DoS protection")
        print("   ✅ Injection attack prevention")
        print("   ✅ Comprehensive audit trails")
        
        print("\n🚀 Next steps:")
        print("   1. Configure CloudWatch dashboards for security monitoring")
        print("   2. Set up SNS alerts for critical security events")
        print("   3. Integrate with your existing authentication system")
        print("   4. Customize compliance frameworks for your requirements")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)