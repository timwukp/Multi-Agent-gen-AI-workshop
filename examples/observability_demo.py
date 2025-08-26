#!/usr/bin/env python3
"""
Observability integration demo for AWS Bedrock Workshop.

This script demonstrates how to integrate the ObservabilityService
with existing agents to enable distributed tracing and metrics collection.
"""

import asyncio
import sys
import os
import time
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from observability import ObservabilityService, trace_operation, get_observability_service
from observability.config import create_observability_config


class EnhancedFinancialAgent:
    """
    Enhanced financial analysis agent with observability integration.
    
    This demonstrates how to add observability to existing agents
    without major code changes.
    """
    
    def __init__(self, name: str = "FinancialAnalysisAgent"):
        self.name = name
        self.observability_service = get_observability_service()
        print(f"✅ {self.name} initialized with observability")
    
    @trace_operation("financial_analysis")
    async def analyze_financial_data(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze financial data with full observability."""
        print(f"🔍 {self.name} analyzing: {query}")
        
        # Simulate knowledge base retrieval
        await self._retrieve_knowledge(query)
        
        # Simulate analysis processing
        await self._process_analysis(query)
        
        # Simulate response generation
        response = await self._generate_response(query)
        
        return {
            "query": query,
            "analysis": response,
            "agent": self.name,
            "timestamp": time.time()
        }
    
    @trace_operation("knowledge_retrieval")
    async def _retrieve_knowledge(self, query: str) -> Dict[str, Any]:
        """Simulate knowledge base retrieval with tracing."""
        # Add custom span attributes
        with self.observability_service.trace_agent_operation(
            self.name, "knowledge_base_query",
            attributes={"query_type": "financial", "query_length": len(query)}
        ) as span:
            # Simulate retrieval time
            await asyncio.sleep(0.1)
            
            span.set_attribute("documents_found", 5)
            span.set_attribute("relevance_score", 0.85)
            
            return {"documents": 5, "relevance": 0.85}
    
    @trace_operation("analysis_processing")
    async def _process_analysis(self, query: str) -> Dict[str, Any]:
        """Simulate analysis processing with tracing."""
        with self.observability_service.trace_agent_operation(
            self.name, "llm_processing",
            attributes={"model": "claude-3-5-sonnet", "query_complexity": "medium"}
        ) as span:
            # Simulate processing time
            await asyncio.sleep(0.2)
            
            span.set_attribute("tokens_processed", 1500)
            span.set_attribute("processing_time_ms", 200)
            
            return {"tokens": 1500, "processing_time": 200}
    
    @trace_operation("response_generation")
    async def _generate_response(self, query: str) -> str:
        """Simulate response generation with tracing."""
        with self.observability_service.trace_agent_operation(
            self.name, "response_formatting",
            attributes={"output_format": "structured", "include_citations": True}
        ) as span:
            # Simulate response generation
            await asyncio.sleep(0.05)
            
            response = f"Financial analysis for: {query}. Based on retrieved documents, the analysis shows positive trends."
            
            span.set_attribute("response_length", len(response))
            span.set_attribute("citations_included", 3)
            
attributes={"output_format": "structured", "include_citations": True}
        ) as span:
            # Simulate response generation
            await asyncio.sleep(0.05)
            
            # Import html module for escaping
            # html.escape() is used to sanitize user input and prevent XSS attacks
            import html
            
            response = f"Financial analysis for: {html.escape(query)}. Based on retrieved documents, the analysis shows positive trends."
            
            span.set_attribute("response_length", len(response))
            span.set_attribute("citations_included", 3)
            
            return response


async def demo_single_agent_observability():
    """Demonstrate observability with a single agent."""
    print("=" * 60)
    print("SINGLE AGENT OBSERVABILITY DEMO")
    print("=" * 60)
    
    agent = EnhancedFinancialAgent("DemoAgent")
    
    # Test queries
    queries = [
        "What is Amazon's revenue growth in Q1 2025?",
        "Analyze Amazon's profitability trends",
        "Compare Amazon's performance to competitors"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        
        start_time = time.time()
        result = await agent.analyze_financial_data(query)
        duration = time.time() - start_time
        
        print(f"✅ Analysis completed in {duration:.2f}s")
        print(f"📊 Result: {result['analysis'][:100]}...")
        
        # Record custom metrics
        agent.observability_service.record_agent_metrics(
            agent_name=agent.name,
            operation="financial_analysis",
            duration_ms=duration * 1000,
            success=True,
            attributes={
                "query_type": "financial",
                "query_number": i,
                "response_length": len(result['analysis'])
            }
        )


async def main():
    """Main demo function."""
    print("🚀 Starting Observability Integration Demo")
    print("This demo shows how to add observability to existing agents\n")
    
    try:
        # Initialize observability
        config = create_observability_config()
        print(f"📊 Observability configured for environment: {config.environment}")
        print(f"🔍 Tracing enabled: {config.tracing.enabled}")
        print(f"📈 Metrics enabled: {config.metrics.enabled}")
        
        # Run single agent demo
        await demo_single_agent_observability()
        
        print("\n" + "=" * 60)
        print("🎉 OBSERVABILITY DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\n📋 What happened:")
        print("   ✅ Distributed traces created for all agent operations")
        print("   ✅ Context propagated across agent boundaries")
        print("   ✅ Custom metrics recorded for performance monitoring")
        print("   ✅ Span attributes added for detailed analysis")
        
        print("\n🔍 To view traces and metrics:")
        print("   1. Check AWS X-Ray console for distributed traces")
        print("   2. View CloudWatch metrics for performance data")
        print("   3. Set up CloudWatch dashboards for monitoring")
        
        print("\n🚀 Next steps:")
        print("   1. Integrate with your existing agents")
        print("   2. Configure CloudWatch alarms")
        print("   3. Set up production monitoring")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)