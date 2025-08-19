# AWS Bedrock Workshop: Multi-Agent GenAI Applications

This workshop demonstrates building production-ready multi-agent GenAI applications using Amazon Bedrock AgentCore SDK and Strands Agents SDK.

## Prerequisites

- Python 3.10 or higher
- AWS Account with Bedrock access
- AWS CLI configured

## Quick Start

1. **Environment Setup**
   ```bash
   python setup.py
   ```

2. **Activate Virtual Environment**
   ```bash
   # On macOS/Linux
   source .venv/bin/activate
   
   # On Windows
   .venv\Scripts\activate
   ```

3. **Configure AWS Credentials**
   ```bash
   aws configure
   ```

4. **Edit Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS configuration
   ```

5. **Verify Setup**
   ```bash
   python verify_setup.py
   ```

## Workshop Modules

### Module 0 (M0): Foundation - Single Agent with RAG
- Environment setup and dependencies
- Basic Strands Agent with Bedrock integration
- Knowledge Base setup and RAG implementation

**Quick Start for Module 0:**
```bash
# 1. Set up Knowledge Base
python scripts/setup_knowledge_base.py

# 2. Test the single agent
python test_single_agent.py

# 3. Run interactive demo
python run_single_agent.py --interactive

# 4. Try example queries
python examples/single_agent_demo.py
```

### Module 1 (M1): AgentCore Runtime Integration
- Deploy single agent on Bedrock AgentCore
- Production runtime configuration
- Health monitoring and async tasks

### Module 2 (M2): Multi-Agent System Architecture
- Query Router Agent
- Internet Research Agent
- Knowledge Retrieval Agent
- Summarizer Agent
- Graph-based coordination

### Module 3 (M3): Memory Management
- AgentCore Memory service integration
- Session and long-term memory
- Cross-agent memory sharing

### Module 4 (M4): Identity and Authorization
- AWS Cognito integration
- Role-based access control
- Secure multi-agent operations

### Module 5 (M5): Observability and Monitoring
- OpenTelemetry distributed tracing
- CloudWatch dashboards
- Production monitoring

## Project Structure

```
├── src/
│   ├── agents/          # Agent implementations
│   ├── tools/           # Custom tools
│   └── utils/           # Utility functions
├── tests/               # Test suite
├── data/
│   └── sample_documents/ # Sample financial documents
├── config.py            # Configuration management
├── setup.py             # Environment setup script
├── verify_setup.py      # Setup verification
└── requirements.txt     # Python dependencies
```

## Configuration

Key configuration options in `.env`:

- `AWS_REGION`: AWS region (default: us-west-2)
- `BEDROCK_MODEL_ID`: Bedrock model ID (default: us.amazon.nova-pro-v1:0)
- `BEDROCK_KNOWLEDGE_BASE_ID`: Knowledge Base ID (set after creation)

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   - Run `aws configure` to set up credentials
   - Ensure proper IAM permissions for Bedrock

2. **Bedrock Access Denied**
   - Request model access in AWS Console
   - Verify IAM permissions for Bedrock and Bedrock Runtime

3. **Python Version Issues**
   - Ensure Python 3.10+ is installed
   - Use `python --version` to check

For more help, see the troubleshooting section in each module's documentation.