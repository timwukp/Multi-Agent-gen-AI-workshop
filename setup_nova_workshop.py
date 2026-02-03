"""
Enhanced setup script for AWS Bedrock Workshop with Nova model support.

This script sets up the workshop environment with the latest SDK enhancements:
- sdk-python: Core Python SDK functionality
- bedrock-agentcore-sdk-python: Specialized Bedrock AgentCore integration
- nova-act: Nova model actions and capabilities
"""

import subprocess
import sys
import os
from pathlib import Path
import json


def run_command(command: str, description: str, check_output: bool = False) -> tuple:
    """Run a shell command and return success status and output."""
    print(f"\n🔄 {description}...")
    try:
        import shlex
        command_list = shlex.split(command)
        result = subprocess.run(
            command_list, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout and check_output:
            print(f"Output: {result.stdout}")
        return True, result.stdout if check_output else ""
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False, ""


def check_python_version():
    """Check if Python version is 3.10 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version {version.major}.{version.minor} is compatible")
    return True


def check_aws_cli():
    """Check if AWS CLI is installed and configured."""
    print("\n🔍 Checking AWS CLI...")
    
    # Check if AWS CLI is installed
    success, _ = run_command("aws --version", "Checking AWS CLI installation")
    if not success:
        print("⚠️  AWS CLI not found. Please install it first:")
        print("   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html")
        return False
    
    # Check if AWS CLI is configured
    success, output = run_command("aws sts get-caller-identity", "Checking AWS credentials", check_output=True)
    if success:
        try:
            identity = json.loads(output)
            print(f"✅ AWS configured for account: {identity.get('Account', 'Unknown')}")
            return True
        except json.JSONDecodeError:
            pass
    
    print("⚠️  AWS credentials not configured. Run 'aws configure' first.")
    return False


def setup_virtual_environment():
    """Set up Python virtual environment."""
    print("\n🐍 Setting up virtual environment...")
    
    if not Path(".venv").exists():
        success, _ = run_command("python -m venv .venv", "Creating virtual environment")
        if not success:
            return False
    else:
        print("✅ Virtual environment already exists")
    
    return True


def install_dependencies():
    """Install Python dependencies including enhanced SDK packages."""
    print("\n📦 Installing dependencies...")
    
    # Determine pip path
    if sys.platform == "win32":
        pip_cmd = ".venv\\Scripts\\pip"
    else:
        pip_cmd = ".venv/bin/pip"
    
    # Upgrade pip
    success, _ = run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    if not success:
        return False
    
    # Install standard requirements
    success, _ = run_command(f"{pip_cmd} install -r requirements.txt", "Installing standard dependencies")
    if not success:
        print("⚠️  Some dependencies may not be available from PyPI")
        print("   This is expected for the enhanced SDK packages")
    
    # Try to install enhanced SDK packages (may not be available in public PyPI)
    enhanced_packages = [
        "sdk-python>=1.0.0",
        "bedrock-agentcore-sdk-python>=1.0.0"
    ]
    
    print("\n🚀 Attempting to install enhanced SDK packages...")
    for package in enhanced_packages:
        success, _ = run_command(f"{pip_cmd} install {package}", f"Installing {package}")
        if not success:
            print(f"⚠️  {package} not available - workshop will use fallback implementations")
    
    return True


def setup_environment_file():
    """Set up .env file with Nova configurations."""
    print("\n⚙️  Setting up environment configuration...")
    
    if not Path(".env").exists():
        if Path(".env.example").exists():
            success, _ = run_command("cp .env.example .env", "Creating .env file from example")
            if success:
                print("📝 Please edit .env file with your AWS credentials and configuration")
                print("   Pay special attention to the new Nova model configurations:")
                print("   - NOVA_MODEL_ID")
                print("   - NOVA_LITE_MODEL_ID") 
                print("   - NOVA_MICRO_MODEL_ID")
                print("   - ENABLE_NOVA_MODELS")
                print("   - NOVA_ACT_ENABLED")
            return success
        else:
            print("⚠️  .env.example not found, please create .env file manually")
            return False
    else:
        print("✅ .env file already exists")
        
        # Check if .env has Nova configurations
        with open(".env", "r") as f:
            env_content = f.read()
        
        nova_configs = [
            "NOVA_MODEL_ID",
            "NOVA_LITE_MODEL_ID", 
            "NOVA_MICRO_MODEL_ID",
            "ENABLE_NOVA_MODELS"
        ]
        
        missing_configs = [config for config in nova_configs if config not in env_content]
        if missing_configs:
            print(f"⚠️  Missing Nova configurations in .env: {', '.join(missing_configs)}")
            print("   Please update your .env file with the new configurations from .env.example")
        else:
            print("✅ Nova configurations found in .env")
        
        return True


def verify_setup():
    """Verify the workshop setup."""
    print("\n🧪 Verifying setup...")
    
    # Run basic verification
    success, _ = run_command("python verify_setup.py", "Running basic setup verification")
    if not success:
        return False
    
    # Test Nova agent if possible
    success, _ = run_command("python test_nova_agent.py", "Testing Nova agent functionality")
    if not success:
        print("⚠️  Nova agent test failed - this may be expected if enhanced SDKs are not available")
        print("   The workshop will still work with fallback implementations")
    
    return True


def main():
    """Main setup function."""
    print("🚀 AWS Bedrock Workshop - Enhanced Nova Setup")
    print("=" * 60)
    print("Setting up workshop with latest SDK enhancements:")
    print("- Amazon Nova model support")
    print("- Enhanced AgentCore integration")
    print("- Advanced Python SDK features")
    print("=" * 60)
    
    # Run setup steps
    steps = [
        ("Python Version Check", check_python_version),
        ("AWS CLI Check", check_aws_cli),
        ("Virtual Environment Setup", setup_virtual_environment),
        ("Dependencies Installation", install_dependencies),
        ("Environment Configuration", setup_environment_file),
        ("Setup Verification", verify_setup)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("Please resolve the issues above and run the setup again.")
            return False
    
    print("\n🎉 Enhanced Nova Workshop Setup Completed!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    if sys.platform == "win32":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("2. Edit .env file with your Nova model configurations")
    print("3. Request Nova model access in AWS Console if needed")
    print("4. Run Nova demo: python examples/nova_agent_demo.py")
    print("5. Start with Module 0.5 for Nova features!")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
