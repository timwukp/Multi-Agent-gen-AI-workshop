"""Setup script for AWS Bedrock Workshop environment."""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status."""
    print(f"\n🔄 {description}...")
    try:
        # Security fix: Use shell=False and split command into list to prevent command injection
        import shlex
        command_list = shlex.split(command)
        result = subprocess.run(command_list, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.10 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version {version.major}.{version.minor} is compatible")
    return True


def setup_environment():
    """Set up the workshop environment."""
    print("🚀 Setting up AWS Bedrock Workshop Environment")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create virtual environment if it doesn't exist
    if not Path(".venv").exists():
        if not run_command("python -m venv .venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Activate virtual environment and install dependencies
    if sys.platform == "win32":
        activate_cmd = ".venv\\Scripts\\activate"
        pip_cmd = ".venv\\Scripts\\pip"
    else:
        activate_cmd = "source .venv/bin/activate"
        pip_cmd = ".venv/bin/pip"
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Create .env file from example if it doesn't exist
    if not Path(".env").exists():
        if Path(".env.example").exists():
            run_command("cp .env.example .env", "Creating .env file from example")
            print("📝 Please edit .env file with your AWS credentials and configuration")
        else:
            print("⚠️  .env.example not found, please create .env file manually")
    else:
        print("✅ .env file already exists")
    
    print("\n🎉 Environment setup completed!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    if sys.platform == "win32":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("2. Configure AWS credentials: aws configure")
    print("3. Edit .env file with your configuration")
    print("4. Verify Bedrock access: python verify_setup.py")
    
    return True


if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)