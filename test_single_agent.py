"""Test script for the basic single agent with RAG."""

import asyncio
import sys
from src.agents.single_agent import create_financial_agent, test_agent_basic, test_agent_streaming
from config import config


def check_configuration():
    """Check if the required configuration is available."""
    print("🔍 Checking Configuration")
    print("=" * 30)
    
    checks = [
        ("AWS Region", config.aws_region),
        ("Bedrock Model ID", config.bedrock_model_id),
        ("Knowledge Base ID", config.bedrock_knowledge_base_id),
    ]
    
    all_good = True
    for check_name, value in checks:
        if value:
            print(f"✅ {check_name}: {value}")
        else:
            print(f"❌ {check_name}: Not configured")
            all_good = False
    
    if not all_good:
        print("\n⚠️  Please ensure all configuration is set in .env file")
        print("Run 'python scripts/setup_knowledge_base.py' to set up Knowledge Base")
        return False
    
    return True


async def test_knowledge_base_tool():
    """Test the knowledge base tool directly."""
    print("\n🧪 Testing Knowledge Base Tool")
    print("=" * 35)
    
    try:
        from src.tools.bedrock_knowledge_base import create_knowledge_base_tool
        
        kb_tool = create_knowledge_base_tool()
        
        test_queries = [
            "Amazon revenue Q1 2025",
            "AWS growth rate",
            "Amazon business segments"
        ]
        
        for query in test_queries:
            print(f"\n📋 Testing query: {query}")
            result = kb_tool(query, max_results=2)
            print(f"Result: {result[:200]}...")
        
        print("✅ Knowledge Base tool test completed")
        return True
        
    except Exception as e:
        print(f"❌ Knowledge Base tool test failed: {e}")
        return False


async def test_sample_queries():
    """Test the agent with sample financial queries."""
    print("\n🧪 Testing Sample Financial Queries")
    print("=" * 40)
    
    try:
        agent = create_financial_agent()
        
        sample_queries = [
            "What was Amazon's total revenue in Q1 2025?",
            "How did AWS perform in the first quarter?",
            "What are Amazon's main business segments?",
            "What is Amazon's operating margin?",
            "How many Prime members does Amazon have?"
        ]
        
        for i, query in enumerate(sample_queries, 1):
            print(f"\n📋 Query {i}: {query}")
            response = await agent.query_async(query)
            print(f"Response: {response[:300]}...")
            
            # Add small delay between queries
            await asyncio.sleep(1)
        
        print("\n✅ Sample queries test completed")
        return True
        
    except Exception as e:
        print(f"❌ Sample queries test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Testing Single Agent with RAG")
    print("=" * 40)
    
    # Check configuration
    if not check_configuration():
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Knowledge Base Tool", test_knowledge_base_tool),
        ("Basic Agent", test_agent_basic),
        ("Sample Queries", test_sample_queries),
        ("Streaming", test_agent_streaming),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔄 Running {test_name} test...")
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary")
    print("=" * 40)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASSED" if results[i] else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    if all(results):
        print("\n🎉 All tests passed! Single agent with RAG is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the configuration and setup.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)