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

from src.agents.single_agent import create_financial_agent, FinancialAnalysisAgent
from src.agents.finance_graph import create_finance_graph, ResilientFinanceGraph
from src.memory.memory_graph import create_memory_enabled_graph, MemoryEnabledGraph
from src.memory.memory_client import create_memory_client, MemoryEnabledClient
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instances for reuse
_agent_instance: Optional[FinancialAnalysisAgent] = None
_multi_agent_graph: Optional[ResilientFinanceGraph] = None
_memory_enabled_graph: Optional[MemoryEnabledGraph] = None
_memory_client: Optional[MemoryEnabledClient] = None

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


def get_multi_agent_graph() -> ResilientFinanceGraph:
    """Get or create the global multi-agent graph instance."""
    global _multi_agent_graph
    if _multi_agent_graph is None:
        _multi_agent_graph = create_finance_graph()
        logger.info("Created new ResilientFinanceGraph instance")
    return _multi_agent_graph


def get_memory_enabled_graph() -> MemoryEnabledGraph:
    """Get or create the global memory-enabled graph instance."""
    global _memory_enabled_graph
    if _memory_enabled_graph is None:
        _memory_enabled_graph = create_memory_enabled_graph()
        logger.info("Created new MemoryEnabledGraph instance")
    return _memory_enabled_graph


def get_memory_client() -> MemoryEnabledClient:
    """Get or create the global memory client instance."""
    global _memory_client
    if _memory_client is None:
        _memory_client = create_memory_client()
        logger.info("Created new MemoryEnabledClient instance")
    return _memory_client


# AgentCore Entrypoints
@app.entrypoint
def financial_analysis_entrypoint(request: Dict[str, Any]) -> Dict[str, Any]:
    """Main entrypoint for financial analysis requests.
    
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
        
        # Get agent and process query
        agent = get_agent_instance()
        response = agent.query(sanitized_prompt)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "success",
            "response": response,
            "streaming_supported": True,
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat(),
            "user_id": user_id,
            "session_id": request.get("session_id"),
            "agent_info": {
                "name": "FinancialAnalysisAgent",
                "model": config.bedrock_model_id,
                "knowledge_base": config.bedrock_knowledge_base_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error in financial_analysis_entrypoint: {e}")
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "error",
            "error": _sanitize_error_message(e),
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat()
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


# Async Task Processing
@app.async_task
async def process_financial_analysis_async(query_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process financial analysis query asynchronously."""
    start_time = datetime.now()
    
    try:
        prompt = query_data.get("prompt", "").strip()
        user_id = query_data.get("user_id")
        session_id = query_data.get("session_id")
        streaming = query_data.get("streaming", False)
        
        # Input validation
        if not prompt:
            return {
                "status": "error",
                "error": "Prompt is required",
                "timestamp": start_time.isoformat()
            }
        
        # Sanitize prompt
        sanitized_prompt = _sanitize_prompt(prompt)
        
        # Get agent and process query
        agent = get_agent_instance()
        
        if streaming:
            # Collect streaming response
            response_chunks = []
            async for chunk in agent.query_stream(sanitized_prompt):
                response_chunks.append(chunk)
            response = "".join(response_chunks)
        else:
            response = await agent.query_async(sanitized_prompt)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "success",
            "response": response,
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "streaming_used": streaming
        }
        
    except Exception as e:
        logger.error(f"Error in async task: {e}")
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "error",
            "error": _sanitize_error_message(e),
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat()
        }


@app.async_task
async def batch_financial_analysis(batch_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process multiple financial analysis queries in batch."""
    start_time = datetime.now()
    
    try:
        queries = batch_data.get("queries", [])
        if not queries or not isinstance(queries, list):
            return {
                "status": "error",
                "error": "Queries list is required",
                "timestamp": start_time.isoformat()
            }
        
        # Limit batch size
        if len(queries) > 10:
            return {
                "status": "error",
                "error": "Batch size limited to 10 queries",
                "timestamp": start_time.isoformat()
            }
        
        # Process queries
        agent = get_agent_instance()
        results = []
        
        for i, query_data in enumerate(queries):
            try:
                prompt = query_data.get("prompt", "").strip()
                if not prompt:
                    results.append({
                        "query_index": i,
                        "status": "error",
                        "error": "Empty prompt"
                    })
                    continue
                
                # Sanitize and process
                sanitized_prompt = _sanitize_prompt(prompt)
                response = await agent.query_async(sanitized_prompt)
                
                results.append({
                    "query_index": i,
                    "status": "success",
                    "response": response,
                    "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt
                })
                
            except Exception as e:
                logger.error(f"Error processing query {i}: {e}")
                results.append({
                    "query_index": i,
                    "status": "error",
                    "error": _sanitize_error_message(e)
                })
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "success",
            "results": results,
            "total_queries": len(queries),
            "successful_queries": len([r for r in results if r["status"] == "success"]),
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "error",
            "error": _sanitize_error_message(e),
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat()
        }


# Multi-Agent System Entrypoints
@app.entrypoint
def multi_agent_financial_analysis(request: Dict[str, Any]) -> Dict[str, Any]:
    """Multi-agent financial analysis entrypoint."""
    start_time = datetime.now()
    
    try:
        # Input validation
        prompt = request.get("prompt", "").strip()
        if not prompt:
            return {
                "status": "error",
                "error": "Prompt is required",
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
        
        # Get multi-agent graph and process query
        graph = get_multi_agent_graph()
        
        # Create query object
        from src.agents.multi_agent_system import FinancialQuery
        query = FinancialQuery(
            query=sanitized_prompt,
            user_id=user_id,
            session_id=request.get("session_id")
        )
        
        # Process with multi-agent system
        report = asyncio.run(graph.process_financial_query(query))
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "success",
            "report": {
                "query": report.query.__dict__,
                "routing_decision": report.routing_decision,
                "agent_results": [result.__dict__ for result in report.agent_results],
                "final_summary": report.final_summary,
                "agents_involved": report.agents_involved,
                "total_execution_time_ms": report.total_execution_time_ms
            },
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat(),
            "mode": "multi_agent"
        }
        
    except Exception as e:
        logger.error(f"Error in multi_agent_financial_analysis: {e}")
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "error",
            "error": _sanitize_error_message(e),
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat()
        }


# Memory-Enhanced Entrypoints
@app.entrypoint
def memory_enabled_financial_analysis(request: Dict[str, Any]) -> Dict[str, Any]:
    """Memory-enhanced financial analysis entrypoint."""
    start_time = datetime.now()
    
    try:
        # Input validation
        prompt = request.get("prompt", "").strip()
        if not prompt:
            return {
                "status": "error",
                "error": "Prompt is required",
                "timestamp": start_time.isoformat()
            }
        
        user_id = request.get("user_id")
        session_id = request.get("session_id")
        
        if not user_id:
            return {
                "status": "error",
                "error": "user_id is required for memory-enabled analysis",
                "timestamp": start_time.isoformat()
            }
        
        # Validate user_id
        if not _is_valid_user_id(user_id):
            return {
                "status": "error",
                "error": "Invalid user_id format",
                "timestamp": start_time.isoformat()
            }
        
        # Sanitize prompt
        sanitized_prompt = _sanitize_prompt(prompt)
        
        # Get memory-enabled graph and process query
        graph = get_memory_enabled_graph()
        
        # Process with memory context
        report = asyncio.run(graph.process_financial_query(
            query=sanitized_prompt,
            user_id=user_id,
            session_id=session_id
        ))
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "success",
            "report": {
                "query": report.query.__dict__,
                "routing_decision": report.routing_decision,
                "agent_results": [result.__dict__ for result in report.agent_results],
                "final_summary": report.final_summary,
                "agents_involved": report.agents_involved,
                "total_execution_time_ms": report.total_execution_time_ms,
                "memory_context_used": report.routing_decision.get("memory_context_used", False)
            },
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat(),
            "mode": "memory_enabled"
        }
        
    except Exception as e:
        logger.error(f"Error in memory_enabled_financial_analysis: {e}")
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "error",
            "error": _sanitize_error_message(e),
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat()
        }


@app.entrypoint
def memory_management(request: Dict[str, Any]) -> Dict[str, Any]:
    """Memory management operations entrypoint."""
    start_time = datetime.now()
    
    try:
        operation = request.get("operation")
        if not operation:
            return {
                "status": "error",
                "error": "Operation is required",
                "timestamp": start_time.isoformat()
            }
        
        user_id = request.get("user_id")
        if not user_id or not _is_valid_user_id(user_id):
            return {
                "status": "error",
                "error": "Valid user_id is required",
                "timestamp": start_time.isoformat()
            }
        
        # Get memory client
        memory_client = get_memory_client()
        
        if operation == "get_profile":
            # Get user profile from memory
            profile = asyncio.run(memory_client.get_user_profile(user_id))
            return {
                "status": "success",
                "profile": profile,
                "timestamp": datetime.now().isoformat()
            }
        
        elif operation == "save_preference":
            preference_key = request.get("preference_key")
            preference_value = request.get("preference_value")
            
            if not preference_key or preference_value is None:
                return {
                    "status": "error",
                    "error": "preference_key and preference_value are required",
                    "timestamp": start_time.isoformat()
                }
            
            # Save user preference
            asyncio.run(memory_client.save_user_preference(
                user_id=user_id,
                preference_key=preference_key,
                preference_value=preference_value
            ))
            
            return {
                "status": "success",
                "message": "Preference saved successfully",
                "timestamp": datetime.now().isoformat()
            }
        
        elif operation == "get_context":
            query = request.get("query", "")
            session_id = request.get("session_id")
            
            # Retrieve memory context
            context = asyncio.run(memory_client.retrieve_context(
                user_id=user_id,
                session_id=session_id,
                query=query
            ))
            
            return {
                "status": "success",
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
        
        elif operation == "get_status":
            # Get memory service status
            status = asyncio.run(memory_client.get_memory_status())
            return {
                "status": "success",
                "memory_status": status,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {
                "status": "error",
                "error": f"Unknown operation: {operation}",
                "timestamp": start_time.isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error in memory_management: {e}")
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "status": "error",
            "error": _sanitize_error_message(e),
            "execution_time_ms": execution_time,
            "timestamp": end_time.isoformat()
        }


# Export the app for deployment
__all__ = ["app", "financial_analysis_entrypoint", "health_check", "process_financial_analysis_async", "batch_financial_analysis"]