"""Basic single agent implementation with RAG capabilities."""

import asyncio
from typing import Dict, Any, Optional, AsyncGenerator

# Import the real Strands SDK
from strands import Agent
from strands.models import BedrockModel

USING_MOCK = False

from src.tools.bedrock_knowledge_base import create_knowledge_base_tool
from config import config


class FinancialAnalysisAgent:
    """Single agent for Amazon financial analysis with RAG capabilities."""
    
    def __init__(self, knowledge_base_id: Optional[str] = None):
        """Initialize the financial analysis agent.
        
        Args:
            knowledge_base_id: Optional Knowledge Base ID
        """
        self.knowledge_base_id = knowledge_base_id or config.bedrock_knowledge_base_id
        
        # Create Bedrock model with streaming support
        self.model = BedrockModel(
            model_id=config.bedrock_model_id,
            region_name=config.bedrock_region,
            temperature=0.1,  # Low temperature for factual financial analysis
            max_tokens=2000
        )
        
        # Create knowledge base tool
        self.kb_tool = create_knowledge_base_tool(self.knowledge_base_id)
        
        # Create Strands agent
        self.agent = Agent(
            name="FinancialAnalysisAgent",
            model=self.model,
            tools=[self.kb_tool],
            system_prompt=self._get_system_prompt()
        )
    
    def _extract_text_from_response(self, response) -> str:
        """Extract text content from various response formats.
        
        Args:
            response: Response from Strands agent (could be dict, object, or string)
            
        Returns:
            Extracted text content as string
        """
        # Handle dictionary responses (common format)
        if isinstance(response, dict):
            if 'content' in response:
                content = response['content']
                if isinstance(content, list) and len(content) > 0:
                    # Extract text from content list
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            text_parts.append(item['text'])
                        elif isinstance(item, str):
                            text_parts.append(item)
                    return ''.join(text_parts)
                elif isinstance(content, str):
                    return content
            elif 'text' in response:
                return response['text']
            elif 'message' in response:
                return response['message']
        
        # Handle object responses
        if hasattr(response, 'content'):
            content = response.content
            if isinstance(content, list) and len(content) > 0:
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                    elif hasattr(item, 'text'):
                        text_parts.append(item.text)
                    elif isinstance(item, str):
                        text_parts.append(item)
                return ''.join(text_parts)
            elif isinstance(content, str):
                return content
        elif hasattr(response, 'text'):
            return str(response.text)
        elif hasattr(response, 'message'):
            return str(response.message)
        
        # Fallback: convert to string and try to extract from string representation
        response_str = str(response)
        if response_str.startswith("{'role': 'assistant', 'content': ["):
            # Try to parse as eval (unsafe but for debugging)
            try:
                import ast
                parsed = ast.literal_eval(response_str)
                if isinstance(parsed, dict) and 'content' in parsed:
                    content = parsed['content']
                    if isinstance(content, list) and len(content) > 0:
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict) and 'text' in item:
                                text_parts.append(item['text'])
                        return ''.join(text_parts)
            except:
                pass
        
        # Final fallback
        return response_str

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the financial analysis agent."""
        return """You are a financial analysis expert specializing in Amazon's business and financial performance. 

Your role is to:
1. Analyze Amazon's financial data, earnings reports, and business metrics
2. Provide accurate, data-driven insights based on the knowledge base
3. Always cite your sources when providing specific financial figures
4. Explain financial concepts clearly for both technical and non-technical audiences
5. Focus on factual analysis rather than investment advice

When answering questions:
- First search the knowledge base for relevant information
- Use specific data points and metrics from the retrieved documents
- Provide context for financial figures (comparisons, trends, explanations)
- Always include citations and sources for your information
- If information is not available in the knowledge base, clearly state this limitation

Available tools:
- knowledge_base_search: Search Amazon financial documents and reports

Remember to be precise, factual, and always ground your responses in the available data."""
    
    def query(self, question: str) -> str:
        """Process a financial analysis query synchronously.
        
        Args:
            question: User's financial analysis question
            
        Returns:
            Agent's response with analysis and citations
        """
        try:
            # Input validation
            if not question or not isinstance(question, str):
                return "I apologize, but I need a valid question to provide analysis."
            
            # Strands Agent only has async methods, so we need to run async in sync context
            import asyncio
            try:
                # Try to get existing event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an event loop, create a task
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.agent.invoke_async(question))
                        response = future.result()
                else:
                    response = asyncio.run(self.agent.invoke_async(question))
            except RuntimeError:
                # Fallback for event loop issues
                response = asyncio.run(self.agent.invoke_async(question))
            
            # Extract string content from response
            return self._extract_text_from_response(response)
        except Exception as e:
            # Log the full error but return sanitized message
            import logging
            logging.getLogger(__name__).error(f"Query processing error: {e}")
            return "I apologize, but I encountered an error processing your query. Please try again or contact support if the issue persists."
    
    async def query_async(self, question: str) -> str:
        """Process a financial analysis query asynchronously.
        
        Args:
            question: User's financial analysis question
            
        Returns:
            Agent's response with analysis and citations
        """
        try:
            # Input validation
            if not question or not isinstance(question, str):
                return "I apologize, but I need a valid question to provide analysis."
            
            response = await self.agent.invoke_async(question)
            
            # Extract string content from response
            return self._extract_text_from_response(response)
        except Exception as e:
            # Log the full error but return sanitized message
            import logging
            logging.getLogger(__name__).error(f"Async query processing error: {e}")
            return "I apologize, but I encountered an error processing your query. Please try again or contact support if the issue persists."
    
    async def query_stream(self, question: str) -> AsyncGenerator[str, None]:
        """Process a financial analysis query with streaming response.
        
        Args:
            question: User's financial analysis question
            
        Yields:
            Chunks of the agent's response as they are generated
        """
        try:
            async for event in self.agent.stream_async(question):
                # Extract content from Strands streaming events
                if isinstance(event, dict):
                    # Look for content in various event types
                    if 'content' in event:
                        yield event['content']
                    elif 'text' in event:
                        yield event['text']
                    elif 'delta' in event and isinstance(event['delta'], dict):
                        if 'text' in event['delta']:
                            yield event['delta']['text']
                        elif 'content' in event['delta']:
                            yield event['delta']['content']
                    # Skip control events like init_event_loop, start, etc.
                elif isinstance(event, str):
                    yield event
        except Exception as e:
            # Log the full error but return sanitized message
            import logging
            logging.getLogger(__name__).error(f"Streaming query processing error: {e}")
            yield "I apologize, but I encountered an error processing your query. Please try again or contact support if the issue persists."
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent configuration.
        
        Returns:
            Dictionary with agent configuration details
        """
        return {
            "name": self.agent.name,
            "model_id": self.model.config.get("model_id"),
            "region": self.model.client.meta.region_name,
            "streaming_enabled": True,  # Strands supports streaming by default
            "temperature": self.model.config.get("temperature"),
            "knowledge_base_id": self.knowledge_base_id,
            "tools": list(self.agent.tool_names)
        }


def create_financial_agent(knowledge_base_id: Optional[str] = None) -> FinancialAnalysisAgent:
    """Factory function to create a financial analysis agent.
    
    Args:
        knowledge_base_id: Optional Knowledge Base ID
        
    Returns:
        Configured FinancialAnalysisAgent instance
    """
    return FinancialAnalysisAgent(knowledge_base_id)


# Example usage and testing functions
async def test_agent_basic():
    """Test basic agent functionality."""
    print("🧪 Testing Financial Analysis Agent")
    print("=" * 40)
    
    try:
        agent = create_financial_agent()
        print(f"✅ Agent created successfully")
        print(f"Agent info: {agent.get_agent_info()}")
        
        # Test synchronous query
        print("\n📋 Testing synchronous query...")
        question = "What was Amazon's revenue in Q1 2025?"
        response = agent.query(question)
        print(f"Question: {question}")
        print(f"Response: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False


async def test_agent_streaming():
    """Test agent streaming functionality."""
    print("\n🧪 Testing Streaming Response")
    print("=" * 40)
    
    try:
        agent = create_financial_agent()
        question = "Analyze Amazon's business segments and their performance."
        
        print(f"Question: {question}")
        print("Streaming response:")
        
        async for chunk in agent.query_stream(question):
            print(chunk, end="", flush=True)
        
        print("\n✅ Streaming test completed")
        return True
        
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False


async def interactive_demo():
    """Interactive demo of the financial analysis agent."""
    print("\n🎯 Interactive Financial Analysis Demo")
    print("=" * 45)
    print("Ask questions about Amazon's financial performance!")
    print("Type 'quit' to exit, 'stream' to toggle streaming mode")
    
    agent = create_financial_agent()
    streaming_mode = False
    
    while True:
        try:
            question = input("\n💬 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif question.lower() == 'stream':
                streaming_mode = not streaming_mode
                print(f"🔄 Streaming mode: {'ON' if streaming_mode else 'OFF'}")
                continue
            elif not question:
                continue
            
            print(f"\n🤖 Agent response:")
            
            if streaming_mode:
                async for chunk in agent.query_stream(question):
                    print(chunk, end="", flush=True)
                print()  # New line after streaming
            else:
                response = await agent.query_async(question)
                print(response)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_agent_basic())
    asyncio.run(test_agent_streaming())
    
    # Run interactive demo
    asyncio.run(interactive_demo())