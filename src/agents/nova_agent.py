"""Nova-enhanced agent implementation with advanced SDK features."""

import asyncio
from typing import Dict, Any, Optional, AsyncGenerator, List

# Import the enhanced Strands SDK with Nova support
from strands import Agent
from strands.models import BedrockModel

# Import enhanced SDK components
try:
    # Try to import from the enhanced SDK repositories
    from sdk_python import EnhancedClient
    from bedrock_agentcore_sdk_python import AgentCoreClient
    SDK_ENHANCED = True
except ImportError:
    # Fallback to standard implementation
    SDK_ENHANCED = False
    print("Enhanced SDK not available, using standard implementation")

from src.tools.bedrock_knowledge_base import create_knowledge_base_tool
from config import config


class NovaFinancialAgent:
    """Enhanced financial analysis agent using Amazon Nova models and advanced SDK features."""
    
    def __init__(self, 
                 knowledge_base_id: Optional[str] = None,
                 model_type: str = "nova-pro",
                 enable_enhanced_features: bool = True):
        """Initialize the Nova financial analysis agent.
        
        Args:
            knowledge_base_id: Optional Knowledge Base ID
            model_type: Nova model type (nova-pro, nova-lite, nova-micro)
            enable_enhanced_features: Enable enhanced SDK features
        """
        self.knowledge_base_id = knowledge_base_id or config.bedrock_knowledge_base_id
        self.model_type = model_type
        self.enable_enhanced_features = enable_enhanced_features and config.enhanced_features_enabled
        
        # Select appropriate Nova model based on type
        model_id_map = {
            "nova-pro": config.nova_model_id,
            "nova-lite": config.nova_lite_model_id,
            "nova-micro": config.nova_micro_model_id
        }
        
        selected_model_id = model_id_map.get(model_type, config.nova_model_id)
        
        # Create enhanced Bedrock model with Nova-specific configurations
        model_config = {
            "model_id": selected_model_id,
            "region_name": config.bedrock_region,
            "temperature": 0.1,  # Low temperature for factual financial analysis
            "max_tokens": 4000,  # Nova models support larger context
        }
        
        # Add Nova-specific configurations
        if "nova" in selected_model_id.lower():
            model_config.update({
                "top_p": 0.9,
                "top_k": 250,
                "stop_sequences": ["Human:", "Assistant:"],
            })
        
        self.model = BedrockModel(**model_config)
        
        # Initialize enhanced SDK clients if available
        self.enhanced_client = None
        self.agentcore_client = None
        
        if SDK_ENHANCED and self.enable_enhanced_features:
            try:
                self.enhanced_client = EnhancedClient(region=config.aws_region)
                self.agentcore_client = AgentCoreClient(
                    control_endpoint=config.agentcore_control_endpoint,
                    data_endpoint=config.agentcore_data_endpoint
                )
            except Exception as e:
                print(f"Enhanced SDK initialization failed: {e}")
                self.enable_enhanced_features = False
        
        # Create knowledge base tool
        self.kb_tool = create_knowledge_base_tool(self.knowledge_base_id)
        
        # Create enhanced tools list
        tools = [self.kb_tool]
        
        # Add enhanced tools if available
        if self.enable_enhanced_features:
            tools.extend(self._create_enhanced_tools())
        
        # Create Strands agent with Nova optimizations
        self.agent = Agent(
            name=f"NovaFinancialAgent-{model_type}",
            model=self.model,
            tools=tools,
            system_prompt=self._get_nova_system_prompt()
        )
    
    def _create_enhanced_tools(self) -> List[Any]:
        """Create enhanced tools using the advanced SDK features."""
        enhanced_tools = []
        
        # Add Nova-specific action tools if nova-act is enabled
        if config.nova_act_enabled:
            # Placeholder for Nova ACT tools - would be implemented based on actual SDK
            pass
        
        return enhanced_tools
    
    def _get_nova_system_prompt(self) -> str:
        """Get the Nova-optimized system prompt for financial analysis."""
        base_prompt = """You are an advanced financial analysis expert powered by Amazon Nova, specializing in Amazon's business and financial performance.

Your enhanced capabilities include:
1. Advanced reasoning and analysis using Nova's enhanced language understanding
2. Multi-modal analysis capabilities (when available)
3. Improved context retention for complex financial discussions
4. Enhanced mathematical and statistical analysis
5. Superior pattern recognition in financial data

Your role is to:
1. Analyze Amazon's financial data, earnings reports, and business metrics with enhanced accuracy
2. Provide sophisticated, data-driven insights leveraging Nova's advanced reasoning
3. Always cite your sources when providing specific financial figures
4. Explain complex financial concepts with improved clarity and depth
5. Focus on factual analysis rather than investment advice
6. Utilize advanced analytical techniques for deeper insights

When answering questions:
- First search the knowledge base for relevant information
- Apply Nova's enhanced reasoning to provide deeper analysis
- Use specific data points and metrics from the retrieved documents
- Provide comprehensive context for financial figures (comparisons, trends, explanations)
- Always include citations and sources for your information
- If information is not available in the knowledge base, clearly state this limitation
- Leverage Nova's improved mathematical capabilities for complex calculations

Available tools:
- knowledge_base_search: Search Amazon financial documents and reports
"""
        
        # Add enhanced features description if enabled
        if self.enable_enhanced_features:
            base_prompt += """
- enhanced_analysis: Advanced analytical capabilities via enhanced SDK
- agentcore_memory: Persistent memory and context management
"""
        
        base_prompt += f"""
Model Configuration: Using {self.model_type} for optimal performance balance.

Remember to leverage Nova's advanced capabilities for precise, factual, and insightful financial analysis."""
        
        return base_prompt
    
    def _extract_text_from_response(self, response) -> str:
        """Extract text content from various response formats with Nova optimizations."""
        # Enhanced extraction logic for Nova responses
        if isinstance(response, dict):
            if 'content' in response:
                content = response['content']
                if isinstance(content, list) and len(content) > 0:
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
        
        # Handle object responses with Nova-specific attributes
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
        
        # Fallback
        return str(response)
    
    def query(self, question: str) -> str:
        """Process a financial analysis query with Nova enhancements."""
        try:
            # Enhanced input validation
            if not question or not isinstance(question, str):
                return "I apologize, but I need a valid question to provide analysis."
            
            # Apply enhanced preprocessing if available
            if self.enable_enhanced_features and self.enhanced_client:
                try:
                    question = self.enhanced_client.preprocess_query(question)
                except Exception as e:
                    print(f"Enhanced preprocessing failed: {e}")
            
            # Execute query with Nova optimizations
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.agent.invoke_async(question))
                        response = future.result()
                else:
                    response = asyncio.run(self.agent.invoke_async(question))
            except RuntimeError:
                response = asyncio.run(self.agent.invoke_async(question))
            
            # Extract and enhance response
            result = self._extract_text_from_response(response)
            
            # Apply post-processing enhancements if available
            if self.enable_enhanced_features and self.enhanced_client:
                try:
                    result = self.enhanced_client.postprocess_response(result)
                except Exception as e:
                    print(f"Enhanced postprocessing failed: {e}")
            
            return result
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Nova query processing error: {e}")
            return "I apologize, but I encountered an error processing your query. Please try again or contact support if the issue persists."
    
    async def query_async(self, question: str) -> str:
        """Process a financial analysis query asynchronously with Nova enhancements."""
        try:
            if not question or not isinstance(question, str):
                return "I apologize, but I need a valid question to provide analysis."
            
            # Enhanced async processing
            if self.enable_enhanced_features and self.enhanced_client:
                try:
                    question = await self.enhanced_client.preprocess_query_async(question)
                except Exception as e:
                    print(f"Enhanced async preprocessing failed: {e}")
            
            response = await self.agent.invoke_async(question)
            result = self._extract_text_from_response(response)
            
            # Enhanced async post-processing
            if self.enable_enhanced_features and self.enhanced_client:
                try:
                    result = await self.enhanced_client.postprocess_response_async(result)
                except Exception as e:
                    print(f"Enhanced async postprocessing failed: {e}")
            
            return result
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Nova async query processing error: {e}")
            return "I apologize, but I encountered an error processing your query. Please try again or contact support if the issue persists."
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the Nova agent configuration."""
        info = {
            "name": self.agent.name,
            "model_type": self.model_type,
            "model_id": self.model.config.get("model_id"),
            "region": self.model.client.meta.region_name,
            "streaming_enabled": True,
            "temperature": self.model.config.get("temperature"),
            "knowledge_base_id": self.knowledge_base_id,
            "tools": list(self.agent.tool_names),
            "enhanced_features_enabled": self.enable_enhanced_features,
            "sdk_enhanced": SDK_ENHANCED,
            "nova_optimizations": True
        }
        
        if self.enable_enhanced_features:
            info.update({
                "enhanced_client_available": self.enhanced_client is not None,
                "agentcore_client_available": self.agentcore_client is not None,
                "nova_act_enabled": config.nova_act_enabled
            })
        
        return info


def create_nova_agent(model_type: str = "nova-pro", 
                     knowledge_base_id: Optional[str] = None,
                     enable_enhanced_features: bool = True) -> NovaFinancialAgent:
    """Factory function to create a Nova financial analysis agent.
    
    Args:
        model_type: Nova model type (nova-pro, nova-lite, nova-micro)
        knowledge_base_id: Optional Knowledge Base ID
        enable_enhanced_features: Enable enhanced SDK features
        
    Returns:
        Configured NovaFinancialAgent instance
    """
    return NovaFinancialAgent(
        knowledge_base_id=knowledge_base_id,
        model_type=model_type,
        enable_enhanced_features=enable_enhanced_features
    )
