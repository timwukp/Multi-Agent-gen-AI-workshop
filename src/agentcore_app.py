"""AgentCore Runtime Integration for the Financial Analysis Agent."""

import asyncio
import json
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime

# Import the real Bedrock AgentCore SDK
from bedrock_agentcore import BedrockAgentCoreApp

USING_MOCK_AGENTCORE = False

from src.agents.single_agent import create_financial_agent, FinancialAnalysisAgent, create_enhanced_financial_analysis_agent
from src.agents.finance_graph import create_finance_graph, ResilientFinanceGraph
from src.agents.enhanced_agents import EnhancedStrandsAgent
from src.observability.service import get_observability_service
try:
    from src.memory.memory_graph import create_memory_enabled_graph, MemoryEnabledGraph
    from src.memory.memory_client import create_memory_client, MemoryEnabledClient
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    logger.warning("Memory modules not available")
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instances for reuse
_agent_instance: Optional[FinancialAnalysisAgent] = None
_enhanced_agent_instance: Optional[EnhancedStrandsAgent] = None
_multi_agent_graph: Optional[ResilientFinanceGraph] = None
_observability_service = None
_memory_enabled_graph = None
_memory_client = None

# Security helper functions
def _sanitize_prompt(prompt: str) -> str:
    """Sanitize user prompt to prevent injection attacks."""
    dangerous_patterns = [
        r'ignore\s+previous\s+instructions',
        r'forget\s+everything',
        r'system\s*:',
        r'assistant\s*:',
        r'human\s*:',
        r'<\s*system\s*>',
        r'<\s*/\s*system\s*>',
        r'```\s*system',
        r'```\s*assistant',
    ]
    
    sanitized = prompt
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    # Remove excessive whitespace
    sanitized = ' '.join(sanitized.split())
    
    return sanitized


def _is_valid_user_id(user_id: str) -> bool:
    """Validate user ID format."""
    # Allow alphanumeric, hyphens, underscores, max 64 chars
    pattern = r'^[a-zA-Z0-9_-]{1,64}$'
    return bool(re.match(pattern, user_id))


def _sanitize_error_message(error: Exception) -> str:
    """Sanitize error messages to prevent information disclosure."""
    error_str = str(error).lower()
    
    # Check for sensitive information patterns
    sensitive_patterns = [
        'access denied',
        'unauthorized',
        'invalid credentials',
        'permission denied',
        'authentication failed'
    ]
    
    for pattern in sensitive_patterns:
        if pattern in error_str:
            return "Authentication or authorization error occurred"
    
    return "An error occurred while processing your request"


# Health check utilities
def _check_bedrock_health() -> Dict[str, Any]:
    """Check Bedrock model health."""
    try:
        # Simple health check - create model instance
        from strands.models import BedrockModel
        model = BedrockModel(
            model_id=config.bedrock_model_id,
            region_name=config.bedrock_region
        )
        return {"status": "healthy", "service": "bedrock"}
    except Exception as e:
        logger.error(f"Bedrock health check failed: {e}")
        return {"status": "unhealthy", "service": "bedrock", "error": str(e)}


def _check_knowledge_base_health() -> Dict[str, Any]:
    """Check Knowledge Base health."""
    try:
        if not config.bedrock_knowledge_base_id:
            return {"status": "not_configured", "service": "knowledge_base"}
        
        # Try to create knowledge base tool
        from src.tools.bedrock_knowledge_base import create_knowledge_base_tool
        kb_tool = create_knowledge_base_tool()
        return {"status": "healthy", "service": "knowledge_base"}
    except Exception as e:
        logger.error(f"Knowledge Base health check failed: {e}")
        return {"status": "unhealthy", "service": "knowledge_base", "error": str(e)}


def _check_memory_health() -> Dict[str, Any]:
    """Check Memory service health."""
    try:
        if not config.agentcore_memory_role_arn:
            return {"status": "not_configured", "service": "memory"}
        
        # Try to create memory client
        memory_client = create_memory_client()
        return {"status": "healthy", "service": "memory"}
    except Exception as e:
        logger.error(f"Memory health check failed: {e}")
        return {"status": "unhealthy", "service": "memory", "error": str(e)}


def _check_multi_agent_health() -> Dict[str, Any]:
    """Check Multi-Agent system health."""
    try:
        # Try to create multi-agent graph
        graph = create_finance_graph()
        return {"status": "healthy", "service": "multi_agent"}
    except Exception as e:
        logger.error(f"Multi-Agent health check failed: {e}")
        return {"status": "unhealthy", "service": "multi_agent", "error": str(e)}


# Initialize the AgentCore app
try:
    app = BedrockAgentCoreApp()
    logger.info("✅ BedrockAgentCoreApp initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize BedrockAgentCoreApp: {e}")
    # Create a mock app for development
    class MockAgentCoreApp:
        def entrypoint(self, func):
            return func
        def ping(self, func):
            return func
        def async_task(self, func):
            return func
    
    app = MockAgentCoreApp()
    USING_MOCK_AGENTCORE = True
    logger.warning("⚠️ Using mock AgentCore app for development")


def get_agent_instance() -> FinancialAnalysisAgent:
    """Get or create the global agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = create_financial_agent()
        logger.info("Created new FinancialAnalysisAgent instance")
    return _agent_instance


def get_enhanced_agent_instance() -> EnhancedStrandsAgent:
    """Get or create the global enhanced agent instance with observability."""
    global _enhanced_agent_instance
    if _enhanced_agent_instance is None:
        _enhanced_agent_instance = create_enhanced_financial_analysis_agent()
        logger.info("Created new EnhancedStrandsAgent instance with observability")
    return _enhanced_agent_instance


def get_observability_service_instance():
    """Get or create the global observability service instance."""
    global _observability_service
    if _observability_service is None:
        _observability_service = get_observability_service()
        logger.info("Created new ObservabilityService instance")
    return _observability_service


def get_multi_agent_graph() -> ResilientFinanceGraph:
    """Get or create the global multi-agent graph instance."""
    global _multi_agent_graph
    if _multi_agent_graph is None:
        _multi_agent_graph = create_finance_graph()
        logger.info("Created new ResilientFinanceGraph instance")
    return _multi_agent_graph


def get_memory_enabled_graph():
    """Get or create the global memory-enabled graph instance."""
    global _memory_enabled_graph
    if not MEMORY_AVAILABLE:
        raise RuntimeError("Memory modules not available")
    if _memory_enabled_graph is None:
        _memory_enabled_graph = create_memory_enabled_graph()
        logger.info("Created new MemoryEnabledGraph instance")
    return _memory_enabled_graph


def get_memory_client():
    """Get or create the global memory client instance."""
    global _memory_client
    if not MEMORY_AVAILABLE:
        raise RuntimeError("Memory modules not available")
    if _memory_client is None:
        _memory_client = create_memory_client()
        logger.info("Created new MemoryEnabledClient instance")
    return _memory_client


# AgentCore Entrypoints
@app.entrypoint
def enhanced_financial_analysis_entrypoint(request: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced entrypoint for financial analysis requests with observability.
    
    Expected request format:
    {
        "prompt": "What was Amazon's revenue in Q1 2025?",
        "streaming": false,
        "user_id": "user123",
        "session_id": "session456"
    }
    """
    start_time = datetime.now()
    
    try:
        # Input validation
        if not isinstance(request, dict):
            return {
                "status": "error",
                "error": "Request must be a JSON object",
                "timestamp": start_time.isoformat()
            }
        
        prompt = request.get("prompt", "").strip()
        if not prompt:
            return {
                "status": "error", 
                "error": "Prompt is required",
                "timestamp": start_time.isoformat()
            }
        
        # Length validation
        if len(prompt) > 10000:  # 10KB limit
            return {
                "status": "error",
                "error": "Prompt too long (max 10KB)",
                "timestamp": start_time.isoformat()
            }
        
        # Sanitize prompt
        sanitized_prompt = _sanitize_prompt(prompt)
        
        # Validate user_id if provided
        user_id = request.get("user_id")
        if user_id and not _is_valid_user_id(user_id):
            return {
                "status": "error",
                "error": "Invalid user_id format",
                "timestamp": start_time.isoformat()
            }
        
        # Get enhanced agent and process query
        agent = get_enhanced_agent_instance()
        
        # Build context
        context = {
            "user_id": user_id,
            "session_id": request.get("session_id"),
            "request_timestamp": start_time.isoformat()
        }
        
        # Process query with observability
        result = asyncio.run(agent.process_query(sanitized_prompt, context))
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "success",
            "response": result.get("response", ""),
            "streaming_supported": True,
            "execution_time_ms": execution_time,
            "agent_processing_time_ms": result.get("processing_time_ms", 0),
            "timestamp": end_time.isoformat(),
            "user_id": user_id,
            "session_id": request.get("session_id"),
            "agent_info": {
                "name": result.get("agent_name", "EnhancedFinancialAnalysisAgent"),
                "model": config.bedrock_model_id,
                "knowledge_base": config.bedrock_knowledge_base_id,
                "observability_enabled": True
            },
            "observability": {
                "traced": True,
                "metrics_recorded": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced_financial_analysis_entrypoint: {e}")
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "error",
            "error": _sanitize_error_message(e),
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat(),
            "observability_enabled": True
        }


@app.ping
def health_check() -> str:
    """Health check endpoint with custom business logic."""
    try:
        # Check all service dependencies
        checks = [
            _check_bedrock_health(),
            _check_knowledge_base_health(),
            _check_memory_health(),
            _check_multi_agent_health()
        ]
        
        # Determine overall health
        unhealthy_services = [check for check in checks if check["status"] == "unhealthy"]
        not_configured_services = [check for check in checks if check["status"] == "not_configured"]
        
        if unhealthy_services:
            logger.warning(f"Unhealthy services: {[s['service'] for s in unhealthy_services]}")
            return "UNHEALTHY"
        elif not_configured_services:
            logger.info(f"Services not configured: {[s['service'] for s in not_configured_services]}")
            return "HEALTHY_BUSY"  # Some services not configured but core functionality works
        else:
            logger.info("All services healthy")
            return "HEALTHY"
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return "UNHEALTHY"


# Export the app for deployment
__all__ = ["app", "financial_analysis_entrypoint", "health_check", "process_financial_analysis_async", "batch_financial_analysis"]