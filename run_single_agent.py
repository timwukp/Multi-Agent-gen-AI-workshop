"""CLI interface for the single agent with RAG."""

import asyncio
import argparse
import sys
from src.agents.single_agent import create_financial_agent
from config import config


async def run_single_query(question: str, streaming: bool = False):
    """Run a single query against the agent."""
    try:
        agent = create_financial_agent()
        
        if streaming:
            print("🤖 Agent response (streaming):")
            async for chunk in agent.query_stream(question):
                print(chunk, end="", flush=True)
            print()  # New line after streaming
        else:
            print("🤖 Agent response:")
            response = await agent.query_async(question)
            print(response)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def run_interactive_mode():
    """Run the agent in interactive mode."""
    print("🎯 Amazon Financial Analysis Agent")
    print("=" * 40)
    print("Ask questions about Amazon's financial performance!")
    print("Commands:")
    print("  'quit' or 'exit' - Exit the program")
    print("  'stream on/off' - Toggle streaming mode")
    print("  'info' - Show agent information")
    print("  'help' - Show this help message")
    
    agent = create_financial_agent()
    streaming_mode = False
    
    # Show agent info
    info = agent.get_agent_info()
    print(f"\n📊 Agent Configuration:")
    print(f"  Model: {info['model_id']}")
    print(f"  Region: {info['region']}")
    print(f"  Knowledge Base: {info['knowledge_base_id']}")
    print(f"  Streaming: {info['streaming_enabled']}")
    
    while True:
        try:
            question = input(f"\n💬 Your question{' (streaming)' if streaming_mode else ''}: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif question.lower() == 'help':
                print("\nCommands:")
                print("  'quit' or 'exit' - Exit the program")
                print("  'stream on/off' - Toggle streaming mode")
                print("  'info' - Show agent information")
                print("  'help' - Show this help message")
                continue
            elif question.lower().startswith('stream'):
                parts = question.lower().split()
                if len(parts) > 1:
                    if parts[1] == 'on':
                        streaming_mode = True
                    elif parts[1] == 'off':
                        streaming_mode = False
                    else:
                        streaming_mode = not streaming_mode
                else:
                    streaming_mode = not streaming_mode
                print(f"🔄 Streaming mode: {'ON' if streaming_mode else 'OFF'}")
                continue
            elif question.lower() == 'info':
                info = agent.get_agent_info()
                print(f"\n📊 Agent Information:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
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


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Amazon Financial Analysis Agent")
    parser.add_argument("--query", "-q", type=str, help="Single query to run")
    parser.add_argument("--stream", "-s", action="store_true", help="Enable streaming mode")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Check configuration
    if not config.bedrock_knowledge_base_id:
        print("❌ Knowledge Base ID not configured")
        print("Please run 'python scripts/setup_knowledge_base.py' first")
        sys.exit(1)
    
    if args.query:
        # Single query mode
        success = asyncio.run(run_single_query(args.query, args.stream))
        sys.exit(0 if success else 1)
    elif args.interactive or not args.query:
        # Interactive mode (default)
        asyncio.run(run_interactive_mode())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()