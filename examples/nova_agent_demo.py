"""
Nova Agent Demo - Showcasing enhanced SDK capabilities with Amazon Nova models.

This demo demonstrates the enhanced features available with the updated SDK repositories:
- sdk-python: Core Python SDK functionality
- bedrock-agentcore-sdk-python: Specialized Bedrock AgentCore integration
- nova-act: Nova model actions and capabilities
"""

import asyncio
import time
from typing import Dict, Any

from src.agents.nova_agent import create_nova_agent
from config import config


async def demo_nova_models():
    """Demonstrate different Nova model capabilities."""
    print("🚀 Nova Models Comparison Demo")
    print("=" * 50)
    
    models = ["nova-pro", "nova-lite", "nova-micro"]
    test_question = "What was Amazon's revenue growth in Q1 2025 compared to Q1 2024?"
    
    results = {}
    
    for model_type in models:
        print(f"\n🧪 Testing {model_type.upper()} model...")
        try:
            agent = create_nova_agent(model_type=model_type)
            
            # Get agent info
            info = agent.get_agent_info()
            print(f"Model ID: {info['model_id']}")
            print(f"Enhanced Features: {info['enhanced_features_enabled']}")
            
            # Time the response
            start_time = time.time()
            response = await agent.query_async(test_question)
            end_time = time.time()
            
            results[model_type] = {
                "response": response[:200] + "..." if len(response) > 200 else response,
                "response_time": end_time - start_time,
                "model_id": info['model_id'],
                "enhanced": info['enhanced_features_enabled']
            }
            
            print(f"Response time: {end_time - start_time:.2f}s")
            print(f"Response preview: {response[:100]}...")
            
        except Exception as e:
            print(f"❌ Error with {model_type}: {e}")
            results[model_type] = {"error": str(e)}
    
    # Summary comparison
    print(f"\n📊 Nova Models Performance Summary")
    print("=" * 50)
    for model, result in results.items():
        if "error" not in result:
            print(f"{model.upper()}: {result['response_time']:.2f}s - Enhanced: {result['enhanced']}")
        else:
            print(f"{model.upper()}: Error - {result['error']}")
    
    return results


async def demo_enhanced_features():
    """Demonstrate enhanced SDK features."""
    print("\n🔧 Enhanced SDK Features Demo")
    print("=" * 50)
    
    # Create agent with enhanced features
    agent = create_nova_agent(
        model_type="nova-pro",
        enable_enhanced_features=True
    )
    
    info = agent.get_agent_info()
    print(f"Agent: {info['name']}")
    print(f"Enhanced Features Enabled: {info['enhanced_features_enabled']}")
    print(f"SDK Enhanced: {info['sdk_enhanced']}")
    print(f"Nova ACT Enabled: {info.get('nova_act_enabled', False)}")
    
    if info.get('enhanced_client_available'):
        print("✅ Enhanced Client Available")
    else:
        print("⚠️  Enhanced Client Not Available (using fallback)")
    
    if info.get('agentcore_client_available'):
        print("✅ AgentCore Client Available")
    else:
        print("⚠️  AgentCore Client Not Available (using fallback)")
    
    # Test complex financial analysis
    complex_questions = [
        "Analyze Amazon's AWS segment performance and compare it to their retail operations in terms of profitability and growth trends.",
        "What are the key financial metrics that indicate Amazon's competitive position in cloud computing?",
        "How has Amazon's international expansion affected their overall financial performance?"
    ]
    
    print(f"\n🧠 Testing Enhanced Analysis Capabilities")
    print("-" * 40)
    
    for i, question in enumerate(complex_questions, 1):
        print(f"\nQuestion {i}: {question}")
        try:
            response = await agent.query_async(question)
            print(f"Response: {response[:150]}...")
        except Exception as e:
            print(f"❌ Error: {e}")


async def demo_streaming_capabilities():
    """Demonstrate streaming capabilities with Nova models."""
    print("\n🌊 Nova Streaming Demo")
    print("=" * 50)
    
    agent = create_nova_agent(model_type="nova-pro")
    
    question = "Provide a comprehensive analysis of Amazon's business model evolution from an e-commerce company to a diversified technology conglomerate."
    
    print(f"Question: {question}")
    print("\nStreaming Response:")
    print("-" * 40)
    
    try:
        # Note: Streaming implementation would depend on actual SDK capabilities
        response = await agent.query_async(question)
        
        # Simulate streaming by chunking the response
        words = response.split()
        for i in range(0, len(words), 5):
            chunk = " ".join(words[i:i+5])
            print(chunk, end=" ", flush=True)
            await asyncio.sleep(0.1)  # Simulate streaming delay
        
        print("\n\n✅ Streaming demo completed")
        
    except Exception as e:
        print(f"❌ Streaming error: {e}")


async def interactive_nova_demo():
    """Interactive demo allowing users to test Nova capabilities."""
    print("\n🎯 Interactive Nova Agent Demo")
    print("=" * 45)
    print("Commands:")
    print("- 'switch <model>': Switch between nova-pro, nova-lite, nova-micro")
    print("- 'info': Show current agent information")
    print("- 'quit': Exit the demo")
    print("- Ask any financial question about Amazon")
    
    current_model = "nova-pro"
    agent = create_nova_agent(model_type=current_model)
    
    while True:
        try:
            user_input = input(f"\n[{current_model}] Your input: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower().startswith('switch '):
                new_model = user_input.split(' ', 1)[1].strip()
                if new_model in ['nova-pro', 'nova-lite', 'nova-micro']:
                    current_model = new_model
                    agent = create_nova_agent(model_type=current_model)
                    print(f"🔄 Switched to {current_model}")
                else:
                    print("❌ Invalid model. Use: nova-pro, nova-lite, or nova-micro")
            elif user_input.lower() == 'info':
                info = agent.get_agent_info()
                print(f"📋 Agent Info: {info}")
            elif user_input:
                print(f"🤖 {current_model} response:")
                response = await agent.query_async(user_input)
                print(response)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Run all Nova demos."""
    print("🎉 AWS Bedrock Workshop - Nova SDK Enhancement Demo")
    print("=" * 60)
    
    # Run demos
    await demo_nova_models()
    await demo_enhanced_features()
    await demo_streaming_capabilities()
    
    # Ask if user wants interactive demo
    try:
        choice = input("\n🤔 Would you like to try the interactive demo? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            await interactive_nova_demo()
    except KeyboardInterrupt:
        print("\n👋 Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
