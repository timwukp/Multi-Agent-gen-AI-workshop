"""
Test script for Nova Agent implementation with enhanced SDK features.
"""

import asyncio
import pytest
from typing import Dict, Any

from src.agents.nova_agent import create_nova_agent, NovaFinancialAgent
from config import config


class TestNovaAgent:
    """Test suite for Nova Agent functionality."""
    
    def test_agent_creation(self):
        """Test basic agent creation."""
        print("🧪 Testing Nova Agent Creation")
        
        # Test different model types
        model_types = ["nova-pro", "nova-lite", "nova-micro"]
        
        for model_type in model_types:
            try:
                agent = create_nova_agent(model_type=model_type)
                assert isinstance(agent, NovaFinancialAgent)
                assert agent.model_type == model_type
                print(f"✅ {model_type} agent created successfully")
            except Exception as e:
                print(f"❌ {model_type} agent creation failed: {e}")
                raise
    
    def test_agent_configuration(self):
        """Test agent configuration and info retrieval."""
        print("\n🧪 Testing Agent Configuration")
        
        agent = create_nova_agent(model_type="nova-pro")
        info = agent.get_agent_info()
        
        # Verify required fields
        required_fields = [
            "name", "model_type", "model_id", "region", 
            "streaming_enabled", "temperature", "tools",
            "enhanced_features_enabled", "nova_optimizations"
        ]
        
        for field in required_fields:
            assert field in info, f"Missing required field: {field}"
            print(f"✅ {field}: {info[field]}")
        
        # Verify Nova-specific configurations
        assert "nova" in info["model_id"].lower() or "claude" in info["model_id"].lower()
        assert info["nova_optimizations"] is True
        
        print("✅ Agent configuration test passed")
    
    async def test_synchronous_query(self):
        """Test synchronous query processing."""
        print("\n🧪 Testing Synchronous Query")
        
        agent = create_nova_agent(model_type="nova-pro")
        
        test_questions = [
            "What is Amazon's primary business model?",
            "How does Amazon generate revenue?",
            "What are Amazon's main business segments?"
        ]
        
        for question in test_questions:
            try:
                response = agent.query(question)
                assert isinstance(response, str)
                assert len(response) > 0
                print(f"✅ Query successful: {question[:50]}...")
                print(f"   Response length: {len(response)} characters")
            except Exception as e:
                print(f"❌ Query failed: {question}")
                print(f"   Error: {e}")
                raise
    
    async def test_asynchronous_query(self):
        """Test asynchronous query processing."""
        print("\n🧪 Testing Asynchronous Query")
        
        agent = create_nova_agent(model_type="nova-lite")
        
        question = "Analyze Amazon's financial performance in recent quarters."
        
        try:
            response = await agent.query_async(question)
            assert isinstance(response, str)
            assert len(response) > 0
            print(f"✅ Async query successful")
            print(f"   Response length: {len(response)} characters")
            print(f"   Response preview: {response[:100]}...")
        except Exception as e:
            print(f"❌ Async query failed: {e}")
            raise
    
    async def test_model_comparison(self):
        """Test different Nova models for performance comparison."""
        print("\n🧪 Testing Model Comparison")
        
        models = ["nova-pro", "nova-lite", "nova-micro"]
        question = "What was Amazon's revenue in the last reported quarter?"
        
        results = {}
        
        for model_type in models:
            try:
                agent = create_nova_agent(model_type=model_type)
                import time
                
                start_time = time.time()
                response = await agent.query_async(question)
                end_time = time.time()
                
                results[model_type] = {
                    "success": True,
                    "response_time": end_time - start_time,
                    "response_length": len(response)
                }
                
                print(f"✅ {model_type}: {end_time - start_time:.2f}s, {len(response)} chars")
                
            except Exception as e:
                results[model_type] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ {model_type}: {e}")
        
        # Verify at least one model worked
        successful_models = [m for m, r in results.items() if r.get("success")]
        assert len(successful_models) > 0, "No models worked successfully"
        
        print(f"✅ Model comparison completed: {len(successful_models)}/{len(models)} successful")
        return results
    
    async def test_enhanced_features(self):
        """Test enhanced SDK features if available."""
        print("\n🧪 Testing Enhanced Features")
        
        # Test with enhanced features enabled
        agent_enhanced = create_nova_agent(
            model_type="nova-pro",
            enable_enhanced_features=True
        )
        
        # Test with enhanced features disabled
        agent_basic = create_nova_agent(
            model_type="nova-pro",
            enable_enhanced_features=False
        )
        
        info_enhanced = agent_enhanced.get_agent_info()
        info_basic = agent_basic.get_agent_info()
        
        print(f"Enhanced agent features: {info_enhanced['enhanced_features_enabled']}")
        print(f"Basic agent features: {info_basic['enhanced_features_enabled']}")
        
        # Both should work, but enhanced might have additional capabilities
        question = "What are Amazon's key competitive advantages?"
        
        response_enhanced = await agent_enhanced.query_async(question)
        response_basic = await agent_basic.query_async(question)
        
        assert isinstance(response_enhanced, str) and len(response_enhanced) > 0
        assert isinstance(response_basic, str) and len(response_basic) > 0
        
        print("✅ Enhanced features test completed")
        print(f"   Enhanced response: {len(response_enhanced)} chars")
        print(f"   Basic response: {len(response_basic)} chars")


async def run_all_tests():
    """Run all Nova agent tests."""
    print("🚀 Running Nova Agent Test Suite")
    print("=" * 50)
    
    test_suite = TestNovaAgent()
    
    try:
        # Run synchronous tests
        test_suite.test_agent_creation()
        test_suite.test_agent_configuration()
        
        # Run asynchronous tests
        await test_suite.test_synchronous_query()
        await test_suite.test_asynchronous_query()
        await test_suite.test_model_comparison()
        await test_suite.test_enhanced_features()
        
        print("\n🎉 All Nova Agent tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
