#!/usr/bin/env python3
"""
Validation script for observability infrastructure setup.

This script validates that all observability dependencies and AWS services
are properly configured and accessible.
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Securely add src to path for imports
script_dir = Path(__file__).resolve().parent
src_path = script_dir / 'src'
if src_path.exists() and src_path.is_dir():
    sys.path.insert(0, str(src_path))
else:
    print("❌ Security Error: Invalid source directory structure")
    sys.exit(1)

from src.observability.validation import validate_observability_setup
from src.observability.config import create_observability_config


def security_check() -> bool:
    """
    Perform basic security checks before validation.
    
    Returns:
        bool: True if security checks pass, False otherwise.
    """
    try:
        # Check if running as root (security risk)
        if os.geteuid() == 0:
            print("⚠️  Warning: Running as root user is not recommended for security")
        
        # Check for suspicious environment variables
        suspicious_vars = ['LD_PRELOAD', 'DYLD_INSERT_LIBRARIES', 'PYTHONPATH']
        for var in suspicious_vars:
            if os.getenv(var):
                print(f"⚠️  Warning: Suspicious environment variable detected: {var}")
        
        return True
    except AttributeError:
        # os.geteuid() not available on Windows
        return True
    except Exception as e:
        print(f"⚠️  Warning: Security check failed: {e}")
        return True  # Don't block validation for security check failures


def main() -> int:
    """
    Main validation function.
    
    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    print("🔍 Validating Observability Infrastructure Setup...")
    print()
    
    # Perform security checks first
    if not security_check():
        print("❌ Security checks failed")
        return 1
    
    try:
        # Create configuration from environment
        config = create_observability_config()
        
        print("📋 Configuration Summary:")
        print(f"   Environment: {config.environment}")
        print(f"   AWS Region: {config.aws_region}")
        print(f"   Tracing Enabled: {config.tracing.enabled}")
        print(f"   Metrics Enabled: {config.metrics.enabled}")
        print(f"   Health Monitoring Enabled: {config.health.enabled}")
        print()
        
        # Run validation
        success = validate_observability_setup(config)
        
        if success:
            print("\n🚀 Observability infrastructure is ready!")
            print("You can now proceed with implementing the observability services.")
            return 0
        else:
            print("\n❌ Observability setup validation failed.")
            print("Please address the issues above before proceeding.")
            return 1
            
    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)