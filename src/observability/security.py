# Security Monitoring Service - Comprehensive security and compliance tracking
# This is a production-ready implementation with audit trails and anomaly detection
# For the complete implementation, see the full repository

"""
Security and compliance monitoring for AWS Bedrock Workshop.

This module implements comprehensive security monitoring including:
- Authentication and authorization event logging
- Audit trail generation with user attribution
- Compliance reporting with automated report generation
- Security dashboards and anomaly detection
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import boto3
from botocore.exceptions import ClientError

# Local imports
from pydantic import BaseModel, Field
from .config import ObservabilityConfig


class SecurityEventType(str, Enum):
    """Types of security events that can be logged."""
    AUTHENTICATION_SUCCESS = "authentication_success"
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_SUCCESS = "authorization_success"
    AUTHORIZATION_FAILURE = "authorization_failure"
    DATA_ACCESS = "data_access"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    COMPLIANCE_VIOLATION = "compliance_violation"
    SECURITY_ALERT = "security_alert"


class SecurityLevel(str, Enum):
    """Security levels for events and alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    SOC2 = "soc2"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"


@dataclass
class SecurityEvent:
    """Data class representing a security event."""
    event_id: str
    event_type: SecurityEventType
    timestamp: datetime
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: str = "success"
    security_level: SecurityLevel = SecurityLevel.LOW
    details: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert security event to dictionary for logging."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "user_email": self.user_email,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
            "resource": self.resource,
            "action": self.action,
            "result": self.result,
            "security_level": self.security_level.value,
            "details": self.details,
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "compliance_frameworks": [f.value for f in self.compliance_frameworks]
        }


@dataclass
class AuditTrail:
    """Data class representing an audit trail entry."""
    audit_id: str
    timestamp: datetime
    user_id: str
    user_email: Optional[str]
    action: str
    resource: str
    resource_type: str
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    source_ip: Optional[str] = None
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    retention_period_days: int = 2557  # 7 years for compliance
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit trail to dictionary for logging."""
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "user_email": self.user_email,
            "action": self.action,
            "resource": self.resource,
            "resource_type": self.resource_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "source_ip": self.source_ip,
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "compliance_frameworks": [f.value for f in self.compliance_frameworks],
            "retention_period_days": self.retention_period_days
        }


class InputValidator:
    """Validates input parameters for security operations."""
    
    def validate_user_id(self, user_id: str) -> bool:
        """Validate user ID format with security checks."""
        if not user_id or not isinstance(user_id, str):
            return False
        
        if len(user_id) > 100 or len(user_id) < 1:
            return False
        
        # Check for null bytes and control characters
        if '\x00' in user_id or any(ord(c) < 32 for c in user_id if c not in '\t\n\r'):
            return False
        
        import re
        pattern = r'^[a-zA-Z0-9@._-]+$'
        return bool(re.match(pattern, user_id))
    
    def validate_ip_address(self, ip: str) -> bool:
        """Validate IP address format."""
        if not ip or not isinstance(ip, str):
            return False
        
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def validate_resource_name(self, resource: str) -> bool:
        """Validate resource name format with security checks."""
        if not resource or not isinstance(resource, str):
            return False
        
        if len(resource) > 500:
            return False
        
        # Prevent path traversal attacks
        if '..' in resource:
            return False
        
        import re
        pattern = r'^[a-zA-Z0-9/_.-]+$'
        return bool(re.match(pattern, resource))


class SecurityMonitor:
    """
    Comprehensive security monitoring and compliance tracking system.
    
    Coordinates between event logging, anomaly detection, and compliance reporting
    for the AWS Bedrock Workshop multi-agent system.
    """
    
    def __init__(self, config: ObservabilityConfig):
        """
        Initialize the security monitor.
        
        Args:
            config: Observability configuration
        """
        self.config = config
        self._logger = logging.getLogger(f"{__name__}.SecurityMonitor")
        
        # Input validation
        self._input_validator = InputValidator()
        
        # Security event storage
        self._security_events: List[SecurityEvent] = []
        self._audit_trails: List[AuditTrail] = []
        
        # Initialize AWS clients
        self._cloudwatch_logs_client = None
        self._initialize_aws_clients()
        self._setup_log_groups()
    
    def _initialize_aws_clients(self) -> None:
        """Initialize AWS service clients."""
        try:
            session = boto3.Session(
                profile_name=self.config.aws_profile,
                region_name=self.config.aws_region
            )
            
            self._cloudwatch_logs_client = session.client('logs')
            self._logger.info("AWS clients initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize AWS clients: {e}")
            raise
    
    def _setup_log_groups(self) -> None:
        """Set up CloudWatch log groups for security logging."""
        self._security_log_group = f"/aws/bedrock-workshop/security/{self.config.environment}"
        self._audit_log_group = f"/aws/bedrock-workshop/audit/{self.config.environment}"
        
        log_groups = [self._security_log_group, self._audit_log_group]
        
        for log_group in log_groups:
            try:
                self._cloudwatch_logs_client.create_log_group(
                    logGroupName=log_group,
                    tags={
                        'Environment': self.config.environment,
                        'Service': 'bedrock-workshop-agents',
                        'Component': 'security-monitoring'
                    }
                )
                
                # Set retention policy (7 years for compliance)
                self._cloudwatch_logs_client.put_retention_policy(
                    logGroupName=log_group,
                    retentionInDays=2557  # 7 years
                )
                
                self._logger.info(f"Created log group: {log_group}")
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                    self._logger.debug(f"Log group already exists: {log_group}")
                else:
                    self._logger.error(f"Failed to create log group {log_group}: {e}")
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        unique_string = f"{timestamp}-{id(self)}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def log_security_event(
        self,
        event_type: SecurityEventType,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        result: str = "success",
        security_level: SecurityLevel = SecurityLevel.LOW,
        **kwargs
    ) -> str:
        """
        Log a security event with comprehensive validation.
        
        Args:
            event_type: Type of security event
            user_id: User identifier (validated)
            resource: Resource being accessed (validated)
            action: Action being performed
            result: Result of the action
            security_level: Security level of the event
            **kwargs: Additional event details
            
        Returns:
            str: Event ID of the logged event
        """
        try:
            # Validate inputs
            if user_id and not self._input_validator.validate_user_id(user_id):
                raise ValueError("Invalid user_id format")
            
            if resource and not self._input_validator.validate_resource_name(resource):
                raise ValueError("Invalid resource format")
            
            # Create security event
            event = SecurityEvent(
                event_id=self._generate_event_id(),
                event_type=event_type,
                timestamp=datetime.now(timezone.utc),
                user_id=user_id,
                resource=resource,
                action=action,
                result=result,
                security_level=security_level,
                details=kwargs
            )
            
            # Store event
            self._security_events.append(event)
            
            # Log to CloudWatch
            self._log_to_cloudwatch(event.to_dict(), self._security_log_group)
            
            self._logger.info(f"Security event logged: {event.event_id}")
            return event.event_id
            
        except Exception as e:
            self._logger.error(f"Failed to log security event: {e}")
            raise
    
    def create_audit_trail(
        self,
        user_id: str,
        action: str,
        resource: str,
        resource_type: str,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Create an audit trail entry with validation.
        
        Args:
            user_id: User performing the action (validated)
            action: Action being performed
            resource: Resource being modified
            resource_type: Type of resource
            old_value: Previous value (optional)
            new_value: New value (optional)
            **kwargs: Additional audit details
            
        Returns:
            str: Audit ID of the created trail entry
        """
        try:
            # Validate inputs
            if not self._input_validator.validate_user_id(user_id):
                raise ValueError("Invalid user_id format")
            
            if not self._input_validator.validate_resource_name(resource):
                raise ValueError("Invalid resource format")
            
            # Create audit trail
            audit = AuditTrail(
                audit_id=self._generate_event_id(),
                timestamp=datetime.now(timezone.utc),
                user_id=user_id,
                action=action,
                resource=resource,
                resource_type=resource_type,
                old_value=old_value,
                new_value=new_value,
                **kwargs
            )
            
            # Store audit trail
            self._audit_trails.append(audit)
            
            # Log to CloudWatch
            self._log_to_cloudwatch(audit.to_dict(), self._audit_log_group)
            
            self._logger.info(f"Audit trail created: {audit.audit_id}")
            return audit.audit_id
            
        except Exception as e:
            self._logger.error(f"Failed to create audit trail: {e}")
            raise
    
    def _log_to_cloudwatch(self, log_data: Dict[str, Any], log_group: str) -> None:
        """Log data to CloudWatch Logs."""
        try:
            log_stream = f"{self.config.environment}-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
            
            # Create log stream if it doesn't exist
            try:
                self._cloudwatch_logs_client.create_log_stream(
                    logGroupName=log_group,
                    logStreamName=log_stream
                )
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                    raise
            
            # Put log event
            self._cloudwatch_logs_client.put_log_events(
                logGroupName=log_group,
                logStreamName=log_stream,
                logEvents=[
                    {
                        'timestamp': int(datetime.now(timezone.utc).timestamp() * 1000),
                        'message': json.dumps({
                            'log_type': 'SecurityEvent' if 'event_type' in log_data else 'AuditTrail',
                            'data': log_data
                        })
                    }
                ]
            )
            
        except Exception as e:
            self._logger.error(f"Failed to log to CloudWatch: {e}")
    
    def get_security_events(
        self,
        event_type: Optional[SecurityEventType] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[SecurityEvent]:
        """
        Retrieve security events with filtering.
        
        Args:
            event_type: Filter by event type
            user_id: Filter by user ID
            limit: Maximum number of events to return
            
        Returns:
            List[SecurityEvent]: Filtered security events
        """
        events = self._security_events
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        return events[-limit:]
    
    def get_audit_trails(
        self,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditTrail]:
        """
        Retrieve audit trails with filtering.
        
        Args:
            user_id: Filter by user ID
            resource_type: Filter by resource type
            limit: Maximum number of trails to return
            
        Returns:
            List[AuditTrail]: Filtered audit trails
        """
        trails = self._audit_trails
        
        if user_id:
            trails = [t for t in trails if t.user_id == user_id]
        
        if resource_type:
            trails = [t for t in trails if t.resource_type == resource_type]
        
        return trails[-limit:]
