"""Mock implementation of Strands SDK for development purposes.

This module provides mock implementations of the Strands SDK components
to allow development and testing when the actual SDK is not available.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, AsyncGenerator, Callable
from abc import ABC, abstractmethod


class MockBedrockModel:
    """Mock implementation of BedrockModel."""
    
    def __init__(self, model_id: str, region: str, streaming: bool = False, 
                 temperature: float = 0.7, max_tokens: int = 1000):
        self.model_id = model_id
        self.region = region
        self.streaming = streaming
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def invoke(self, prompt: str) -> str:
        """Mock synchronous invocation."""
        return f"Mock response to: {prompt[:50]}..."
    
    async def ainvoke(self, prompt: str) -> str:
        """Mock asynchronous invocation."""
        await asyncio.sleep(0.1)  # Simulate processing time
        return f"Mock async response to: {prompt[:50]}..."
    
    async def astream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Mock streaming response."""
        response = f"Mock streaming response to: {prompt[:50]}..."
        words = response.split()
        for word in words:
            await asyncio.sleep(0.05)  # Simulate streaming delay
            yield word + " "


class MockAgent:
    """Mock implementation of Strands Agent."""
    
    def __init__(self, name: str = "MockAgent", model: MockBedrockModel = None, 
                 tools: List[Callable] = None, system_prompt: str = ""):
        self.name = name
        self.model = model or MockBedrockModel("mock-model", "us-west-2")
        self.tools = tools or []
        self.system_prompt = system_prompt
    
    def invoke(self, query: str) -> str:
        """Mock synchronous invocation with tool usage."""
        # Simulate tool usage
        if self.tools and "search" in query.lower():
            tool_result = self._use_tool(query)
            return f"Based on my search: {tool_result}\n\nAnalysis: This is a mock response analyzing the query: {query[:100]}..."
        
        return f"Mock agent response to: {query[:100]}..."
    
    async def ainvoke(self, query: str) -> str:
        """Mock asynchronous invocation with tool usage."""
        await asyncio.sleep(0.2)  # Simulate processing time
        
        # Simulate tool usage
        if self.tools and "search" in query.lower():
            tool_result = self._use_tool(query)
            return f"Based on my search: {tool_result}\n\nAnalysis: This is a mock async response analyzing the query: {query[:100]}..."
        
        return f"Mock async agent response to: {query[:100]}..."
    
    async def astream(self, query: str) -> AsyncGenerator[str, None]:
        """Mock streaming response with tool usage."""
        # Simulate tool usage first
        if self.tools and "search" in query.lower():
            yield "Searching knowledge base... "
            await asyncio.sleep(0.1)
            tool_result = self._use_tool(query)
            yield f"Found relevant information. "
            await asyncio.sleep(0.1)
        
        # Stream the response
        response = f"This is a mock streaming analysis of your query: {query[:100]}... The agent would provide detailed financial analysis here."
        words = response.split()
        for word in words:
            await asyncio.sleep(0.05)
            yield word + " "
    
    def _use_tool(self, query: str) -> str:
        """Simulate tool usage."""
        if self.tools:
            # Use the first available tool
            tool = self.tools[0]
            try:
                return tool(query, max_results=3)
            except Exception as e:
                return f"Tool error: {e}"
        return "No tools available"


# Mock module structure to match expected imports
class MockStrands:
    """Mock Strands module."""
    
    Agent = MockAgent
    
    class models:
        BedrockModel = MockBedrockModel


# Create mock instances for import
Agent = MockAgent

class models:
    BedrockModel = MockBedrockModel


def create_mock_knowledge_base_tool() -> Callable:
    """Create a mock knowledge base tool for testing."""
    
    def mock_knowledge_base_search(query: str, max_results: int = 5) -> str:
        """Mock knowledge base search function."""
        
        # Simulate different responses based on query content
        if "revenue" in query.lower() or "sales" in query.lower():
            return """
Result 1 (Relevance: 0.892):
Amazon Q1 2025 net sales increased 12% to $143.3 billion in the first quarter. 
Product sales were $54.7 billion and service sales were $88.6 billion.

Result 2 (Relevance: 0.845):
Geographic revenue distribution shows United States at 69%, International at 22%, 
and AWS at 17% of total revenue.
"""
        elif "aws" in query.lower():
            return """
Result 1 (Relevance: 0.923):
AWS net sales were $25.0 billion, up 17% year-over-year in Q1 2025. 
AWS continues to be the leading cloud computing platform.

Result 2 (Relevance: 0.876):
AWS segment sales: $25.0 billion (up 17%) representing strong growth in 
cloud infrastructure services.
"""
        elif "business" in query.lower() or "segment" in query.lower():
            return """
Result 1 (Relevance: 0.901):
Amazon's core business segments include E-commerce and Retail, Amazon Web Services (AWS), 
Digital Content and Advertising, and Devices and Services.

Result 2 (Relevance: 0.834):
Business segment performance: North America segment sales: $82.5 billion (up 8%), 
International segment sales: $31.9 billion (up 10%), AWS segment sales: $25.0 billion (up 17%).
"""
        else:
            return f"""
Result 1 (Relevance: 0.756):
Mock search result for query: {query}. This would contain relevant financial 
information from Amazon's knowledge base.

Result 2 (Relevance: 0.689):
Additional mock result providing context and supporting data for the financial analysis.
"""
    
    # Add metadata
    mock_knowledge_base_search.__name__ = "knowledge_base_search"
    mock_knowledge_base_search.__doc__ = """Mock knowledge base search for testing."""
    
    return mock_knowledge_base_search