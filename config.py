"""
Configuration management for AWS Bedrock Workshop.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

# Import observability configuration
from src.observability.config import ObservabilityConfig, create_observability_config


class WorkshopConfig(BaseSettings):
    """Configuration settings for the AWS Bedrock Workshop."""
    
    # AWS Configuration
    aws_region: str = Field(default="us-west-2", env="AWS_REGION")
    aws_profile: Optional[str] = Field(default=None, env="AWS_PROFILE")
    
    # Bedrock Configuration
    bedrock_model_id: str = Field(default="anthropic.claude-3-5-sonnet-20240620-v1:0", env="BEDROCK_MODEL_ID")
    # Nova model support - enhanced with latest Nova models
    nova_model_id: str = Field(default="us.amazon.nova-pro-v1:0", env="NOVA_MODEL_ID")
    nova_lite_model_id: str = Field(default="us.amazon.nova-lite-v1:0", env="NOVA_LITE_MODEL_ID")
    nova_micro_model_id: str = Field(default="us.amazon.nova-micro-v1:0", env="NOVA_MICRO_MODEL_ID")
    bedrock_region: str = Field(default="us-west-2", env="BEDROCK_REGION")
    enable_nova_models: bool = Field(default=True, env="ENABLE_NOVA_MODELS")
    
    # AgentCore Configuration
    agentcore_memory_role_arn: Optional[str] = Field(default=None, env="AGENTCORE_MEMORY_ROLE_ARN")
    agentcore_control_endpoint: Optional[str] = Field(default=None, env="AGENTCORE_CONTROL_ENDPOINT")
    agentcore_data_endpoint: Optional[str] = Field(default=None, env="AGENTCORE_DATA_ENDPOINT")
    
    # Knowledge Base Configuration
    bedrock_knowledge_base_id: Optional[str] = Field(default="IYBUFMUPF9", env="BEDROCK_KNOWLEDGE_BASE_ID")
    bedrock_knowledge_base_data_source_id: Optional[str] = Field(default="3PD2N41KLU", env="BEDROCK_KNOWLEDGE_BASE_DATA_SOURCE_ID")
    
    # Enhanced SDK Configuration
    sdk_python_version: str = Field(default="1.0.0", env="SDK_PYTHON_VERSION")
    agentcore_sdk_version: str = Field(default="1.0.0", env="AGENTCORE_SDK_VERSION")
    nova_act_enabled: bool = Field(default=True, env="NOVA_ACT_ENABLED")
    enhanced_features_enabled: bool = Field(default=True, env="ENHANCED_FEATURES_ENABLED")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global configuration instances
config = WorkshopConfig()
observability_config = create_observability_config()
