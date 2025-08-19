"""Configuration management for AWS Bedrock Workshop."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class WorkshopConfig(BaseSettings):
    """Configuration settings for the AWS Bedrock Workshop."""
    
    # AWS Configuration
    aws_region: str = Field(default="us-west-2", env="AWS_REGION")
    aws_profile: Optional[str] = Field(default=None, env="AWS_PROFILE")
    
    # Bedrock Configuration
    bedrock_model_id: str = Field(default="anthropic.claude-3-5-sonnet-20240620-v1:0", env="BEDROCK_MODEL_ID")
    bedrock_region: str = Field(default="us-west-2", env="BEDROCK_REGION")
    
    # AgentCore Configuration
    agentcore_memory_role_arn: Optional[str] = Field(default=None, env="AGENTCORE_MEMORY_ROLE_ARN")
    agentcore_control_endpoint: Optional[str] = Field(default=None, env="AGENTCORE_CONTROL_ENDPOINT")
    agentcore_data_endpoint: Optional[str] = Field(default=None, env="AGENTCORE_DATA_ENDPOINT")
    
    # Knowledge Base Configuration
    bedrock_knowledge_base_id: Optional[str] = Field(default="IYBUFMUPF9", env="BEDROCK_KNOWLEDGE_BASE_ID")
    bedrock_knowledge_base_data_source_id: Optional[str] = Field(default="3PD2N41KLU", env="BEDROCK_KNOWLEDGE_BASE_DATA_SOURCE_ID")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global configuration instance
config = WorkshopConfig()