"""Verify AWS Bedrock Workshop setup and configuration."""

import boto3
import sys
from botocore.exceptions import ClientError, NoCredentialsError
from config import config


def check_aws_credentials():
    """Check if AWS credentials are configured."""
    try:
        session = boto3.Session(profile_name=config.aws_profile)
        sts = session.client('sts', region_name=config.aws_region)
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials configured for account: {identity['Account']}")
        print(f"   User/Role: {identity['Arn']}")
        return True
    except NoCredentialsError:
        print("❌ AWS credentials not configured")
        print("   Run: aws configure")
        return False
    except ClientError as e:
        print(f"❌ AWS credentials error: {e}")
        return False


def check_bedrock_access():
    """Check if Bedrock service is accessible and model is available."""
    try:
        session = boto3.Session(profile_name=config.aws_profile)
        bedrock = session.client('bedrock', region_name=config.bedrock_region)
        
        # List available models
        response = bedrock.list_foundation_models()
        available_models = [model['modelId'] for model in response['modelSummaries']]
        
        if config.bedrock_model_id in available_models:
            print(f"✅ Bedrock model {config.bedrock_model_id} is available")
            return True
        else:
            print(f"❌ Bedrock model {config.bedrock_model_id} not available")
            print(f"   Available models: {available_models[:5]}...")  # Show first 5
            return False
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("❌ Access denied to Bedrock service")
            print("   Please ensure you have proper IAM permissions for Bedrock")
        else:
            print(f"❌ Bedrock access error: {e}")
        return False


def check_bedrock_runtime():
    """Check if Bedrock Runtime is accessible for inference."""
    try:
        session = boto3.Session(profile_name=config.aws_profile)
        bedrock_runtime = session.client('bedrock-runtime', region_name=config.bedrock_region)
        
        # Test with a simple inference call
        test_prompt = "Hello, this is a test."
        
        response = bedrock_runtime.invoke_model(
            modelId=config.bedrock_model_id,
            body=f'{{"messages": [{{ "role": "user", "content": "{test_prompt}" }}], "max_tokens": 10}}'
        )
        
        print("✅ Bedrock Runtime accessible - model inference working")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("❌ Access denied to Bedrock Runtime")
            print("   Please ensure you have proper IAM permissions for Bedrock Runtime")
        elif error_code == 'ValidationException':
            print("❌ Model validation error - check model ID and region")
        else:
            print(f"❌ Bedrock Runtime error: {e}")
        return False


def main():
    """Run all verification checks."""
    print("🔍 Verifying AWS Bedrock Workshop Setup")
    print("=" * 45)
    
    checks = [
        ("AWS Credentials", check_aws_credentials),
        ("Bedrock Access", check_bedrock_access),
        ("Bedrock Runtime", check_bedrock_runtime),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 45)
    if all(results):
        print("🎉 All checks passed! Your environment is ready for the workshop.")
        return True
    else:
        print("❌ Some checks failed. Please resolve the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)