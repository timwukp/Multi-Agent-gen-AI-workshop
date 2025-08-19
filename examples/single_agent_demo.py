"""Demonstration of the single agent with RAG capabilities."""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.single_agent import create_financial_agent
from config import config


async def demo_basic_queries():
    """Demonstrate basic financial analysis queries."""
    print("🎯 Basic Financial Analysis Queries")
    print("=" * 45)
    
    agent = create_financial_agent()
    
    queries = [
        "What was Amazon's total revenue in Q1 2025?",
        "How did AWS perform compared to other business segments?",
        "What are Amazon's key competitive advantages?",
        "What is Amazon's current market position in cloud computing?",
        "How many Prime members does Amazon have globally?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n📋 Query {i}: {query}")
        print("🤖 Response:")
        
        try:
            response = await agent.query_async(query)
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 60)
        await asyncio.sleep(1)  # Brief pause between queries


async def demo_streaming_response():
    """Demonstrate streaming response capability."""
    print("\n🎯 Streaming Response Demo")
    print("=" * 35)
    
    agent = create_financial_agent()
    
    query = "Provide a comprehensive analysis of Amazon's Q1 2025 financial performance, including revenue breakdown, growth trends, and business segment analysis."
    
    print(f"📋 Query: {query}")
    print("\n🤖 Streaming Response:")
    print("-" * 60)
    
    try:
        async for chunk in agent.query_stream(query):
            print(chunk, end="", flush=True)
        print("\n" + "-" * 60)
    except Exception as e:
        print(f"❌ Streaming error: {e}")


async def demo_agent_capabilities():
    """Demonstrate various agent capabilities."""
    print("\n🎯 Agent Capabilities Demo")
    print("=" * 35)
    
    agent = create_financial_agent()
    
    # Show agent configuration
    info = agent.get_agent_info()
    print("📊 Agent Configuration:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test different types of queries
    test_scenarios = [
        {
            "name": "Specific Financial Metrics",
            "query": "What was Amazon's operating margin in Q1 2025?"
        },
        {
            "name": "Comparative Analysis", 
            "query": "Compare AWS growth rate with Amazon's overall revenue growth."
        },
        {
            "name": "Business Strategy",
            "query": "What are Amazon's main investment areas and strategic priorities?"
        },
        {
            "name": "Market Position",
            "query": "How does Amazon's market share in cloud computing compare to competitors?"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 {scenario['name']}")
        print(f"Query: {scenario['query']}")
        print("🤖 Response:")
        
        try:
            response = await agent.query_async(scenario['query'])
            # Show first 300 characters for demo
            print(response[:300] + "..." if len(response) > 300 else response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
        await asyncio.sleep(0.5)


async def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n🎯 Error Handling Demo")
    print("=" * 30)
    
    agent = create_financial_agent()
    
    # Test with various edge cases
    edge_cases = [
        "",  # Empty query
        "What is the meaning of life?",  # Unrelated query
        "Tell me about Apple's financial performance",  # Different company
        "What will Amazon's stock price be tomorrow?",  # Future prediction
    ]
    
    for i, query in enumerate(edge_cases, 1):
        print(f"\n📋 Edge Case {i}: '{query}'")
        print("🤖 Response:")
        
        try:
            response = await agent.query_async(query)
            print(response[:200] + "..." if len(response) > 200 else response)
        except Exception as e:
            print(f"❌ Error handled: {e}")
        
        print("-" * 40)


async def main():
    """Main demo function."""
    print("🚀 Amazon Financial Analysis Agent Demo")
    print("=" * 50)
    
    # Check if we're using mock implementation
    try:
        from src.agents.single_agent import USING_MOCK
        if USING_MOCK:
            print("⚠️  Running with mock implementation for demonstration")
            print("   Install Strands SDK and configure AWS for full functionality")
    except ImportError:
        pass
    
    print(f"\n📊 Configuration:")
    print(f"  AWS Region: {config.aws_region}")
    print(f"  Bedrock Model: {config.bedrock_model_id}")
    print(f"  Knowledge Base ID: {config.bedrock_knowledge_base_id or 'Not configured'}")
    
    # Run demo sections
    demos = [
        ("Basic Queries", demo_basic_queries),
        ("Streaming Response", demo_streaming_response),
        ("Agent Capabilities", demo_agent_capabilities),
        ("Error Handling", demo_error_handling),
    ]
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n{'='*60}")
            await demo_func()
        except KeyboardInterrupt:
            print(f"\n⏹️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Demo '{demo_name}' failed: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Set up AWS credentials and Bedrock access")
    print("2. Run 'python scripts/setup_knowledge_base.py' to create Knowledge Base")
    print("3. Install Strands SDK for full functionality")
    print("4. Try 'python run_single_agent.py --interactive' for hands-on experience")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)