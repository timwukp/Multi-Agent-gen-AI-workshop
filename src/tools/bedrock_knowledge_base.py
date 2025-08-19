"""Custom tool for Bedrock Knowledge Base integration."""

import boto3
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError
from strands import tool
from config import config


class BedrockKnowledgeBaseTool:
    """Tool for retrieving information from Bedrock Knowledge Base."""
    
    def __init__(self, knowledge_base_id: Optional[str] = None):
        """Initialize the Knowledge Base tool.
        
        Args:
            knowledge_base_id: The Knowledge Base ID. If None, uses config.
        """
        self.knowledge_base_id = knowledge_base_id or config.bedrock_knowledge_base_id
        if not self.knowledge_base_id:
            raise ValueError("Knowledge Base ID must be provided or configured in environment")
        
        self.session = boto3.Session(profile_name=config.aws_profile)
        self.bedrock_agent_runtime = self.session.client(
            'bedrock-agent-runtime', 
            region_name=config.aws_region
        )
    
    def retrieve(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents from the Knowledge Base.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of retrieved documents with content and metadata
        """
        try:
            # Input validation
            if not query or not isinstance(query, str):
                return []
            
            # Sanitize query
            query = query.strip()
            if len(query) > 1000:  # Limit query length
                query = query[:1000]
            
            # Limit max_results for security
            max_results = min(max_results, 20)  # Cap at 20 results
            response = self.bedrock_agent_runtime.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            )
            
            results = []
            for result in response['retrievalResults']:
                results.append({
                    'content': result['content']['text'],
                    'score': result['score'],
                    'location': result.get('location', {}),
                    'metadata': result.get('metadata', {})
                })
            
            return results
            
        except ClientError as e:
            print(f"Error retrieving from Knowledge Base: {e}")
            return []
    
    def retrieve_and_generate(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """Retrieve documents and generate a response using Bedrock.
        
        Args:
            query: The user query
            max_results: Maximum number of documents to retrieve
            
        Returns:
            Dictionary with generated response and source citations
        """
        try:
            response = self.bedrock_agent_runtime.retrieve_and_generate(
                input={'text': query},
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': self.knowledge_base_id,
                        'modelArn': f'arn:aws:bedrock:{config.bedrock_region}::foundation-model/{config.bedrock_model_id}',
                        'retrievalConfiguration': {
                            'vectorSearchConfiguration': {
                                'numberOfResults': max_results
                            }
                        }
                    }
                }
            )
            
            return {
                'response': response['output']['text'],
                'citations': response.get('citations', []),
                'session_id': response.get('sessionId')
            }
            
        except ClientError as e:
            print(f"Error in retrieve and generate: {e}")
            return {
                'response': f"I apologize, but I encountered an error while searching the knowledge base: {str(e)}",
                'citations': [],
                'session_id': None
            }


def create_knowledge_base_tool(knowledge_base_id: Optional[str] = None) -> callable:
    """Create a knowledge base tool function for use with Strands agents.
    
    Args:
        knowledge_base_id: Optional Knowledge Base ID
        
    Returns:
        Callable tool function decorated with @tool
    """
    # Check if we can create the real tool or need to use mock
    try:
        kb_tool = BedrockKnowledgeBaseTool(knowledge_base_id)
        use_real_tool = True
    except (ValueError, Exception) as e:
        print(f"⚠️  Using mock knowledge base tool: {e}")
        # Create mock tool with @tool decorator
        @tool
        def mock_knowledge_base_search(query: str, max_results: int = 5) -> str:
            """Mock search of the Amazon financial knowledge base.
            
            Args:
                query: Search query about Amazon financial data
                max_results: Maximum number of results to return
                
            Returns:
                Mock search results
            """
            return f"Mock knowledge base response to: {query}..."
        
        return mock_knowledge_base_search
    
    @tool
    def knowledge_base_search(query: str, max_results: int = 5) -> str:
        """Search the Amazon financial knowledge base.
        
        Args:
            query: Search query about Amazon financial data
            max_results: Maximum number of results to return
            
        Returns:
            Formatted search results with citations
        """
        results = kb_tool.retrieve(query, max_results)
        
        if not results:
            return "No relevant information found in the knowledge base."
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            content = result['content'][:500] + "..." if len(result['content']) > 500 else result['content']
            score = result['score']
            
            formatted_results.append(f"""
Result {i} (Relevance: {score:.3f}):
{content}
""")
        
        return "\n".join(formatted_results)
    
    return knowledge_base_search