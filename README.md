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

6. **Validate Observability Setup (Module 5)**
   ```bash
   python validate_observability_setup.py
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
- ✅ OpenTelemetry distributed tracing with AWS X-Ray integration
- ✅ CloudWatch metrics collection and dashboards
- ✅ Comprehensive health monitoring with AWS dependency validation
- ✅ **ENHANCED**: Multi-layer security validation with injection prevention
- ✅ Performance monitoring and optimization
- ✅ Production alerting and incident response
- ✅ Security and compliance monitoring

**Quick Start for Module 5:**
```bash
# 1. Validate observability setup
python validate_observability_setup.py

# 2. Test observability service
python test_observability_service.py

# 3. Test metrics collection
python test_metrics_collector.py

# 4. Run observability demo
python examples/observability_demo.py

# 5. Run metrics demo
python examples/metrics_demo.py

# 6. Test enhanced security validation (NEW)
python test_enhanced_security_validation.py

# 7. Test health monitoring (NEW)
python test_health_monitoring.py

# 8. Run health monitoring demo (NEW)
python examples/health_monitoring_demo.py

# 9. Run security monitoring demo (NEW)
python examples/security_monitoring_demo.py

# 10. Test comprehensive observability suite (NEW)
python test_observability_comprehensive.py
```

## Project Structure

```
├── src/
│   ├── agents/          # Agent implementations
│   ├── tools/           # Custom tools
│   ├── memory/          # Memory management (Module 3)
│   ├── observability/   # Observability infrastructure (Module 5)
│   │   ├── config.py    # Configuration management
│   │   ├── service.py   # OpenTelemetry tracing service
│   │   ├── metrics.py   # CloudWatch metrics collection
│   │   ├── health.py    # Health monitoring
│   │   ├── performance.py # Performance analysis
│   │   ├── security.py  # Security monitoring
│   │   └── dashboards.py # CloudWatch dashboards
│   └── utils/           # Utility functions
├── examples/            # Interactive demos
├── tests/               # Comprehensive test suite
├── data/
│   └── sample_documents/ # Sample financial documents
├── config.py            # Configuration management
├── setup.py             # Environment setup script
├── verify_setup.py      # Setup verification
├── validate_observability_setup.py  # Observability validation
└── requirements.txt     # Python dependencies
```

## Configuration

Key configuration options in `.env`:

### Core Configuration
- `AWS_REGION`: AWS region (default: us-west-2)
- `BEDROCK_MODEL_ID`: Bedrock model ID (default: us.amazon.nova-pro-v1:0)
- `BEDROCK_KNOWLEDGE_BASE_ID`: Knowledge Base ID (set after creation)

### AgentCore Configuration (Modules 1-4)
- `AGENTCORE_MEMORY_ROLE_ARN`: IAM role for AgentCore Memory service
- `AGENTCORE_CONTROL_ENDPOINT`: AgentCore control plane endpoint
- `AGENTCORE_DATA_ENDPOINT`: AgentCore data plane endpoint

### Observability Configuration (Module 5)
- `OBSERVABILITY_TRACING_ENABLED`: Enable OpenTelemetry tracing (default: true)
- `OBSERVABILITY_METRICS_ENABLED`: Enable CloudWatch metrics (default: true)
- `OBSERVABILITY_HEALTH_ENABLED`: Enable health monitoring (default: true)
- `OBSERVABILITY_METRICS_NAMESPACE`: CloudWatch metrics namespace (default: BedrockWorkshop/Agents)
- `OBSERVABILITY_METRICS_FLUSH_INTERVAL_SECONDS`: Metrics flush interval (default: 60)
- `ENVIRONMENT`: Deployment environment (development/staging/production)

## Features

### Production-Ready Observability
- **Distributed Tracing**: OpenTelemetry integration with AWS X-Ray
- **Metrics Collection**: CloudWatch metrics with automated dashboards
- **Health Monitoring**: Multi-dependency health validation
- **Performance Analysis**: Automated bottleneck detection and optimization
- **Security Monitoring**: Input validation, audit trails, and compliance reporting
- **Alerting**: SNS notifications for critical events

### Multi-Agent Architecture
- **Specialized Agents**: Router, Research, Knowledge Retrieval, Summarizer
- **Graph Coordination**: Intelligent workflow orchestration
- **Memory Management**: Persistent context and user preferences
- **Security**: Input validation and injection prevention

### Comprehensive Testing
- **Unit Tests**: Individual component validation
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Load testing and optimization validation
- **Security Tests**: Input validation and security enhancement testing
- **Chaos Engineering**: Resilience and failure recovery testing

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

4. **Observability Setup Issues (Module 5)**
   - Run `python validate_observability_setup.py` to check configuration
   - Ensure AWS credentials have CloudWatch and X-Ray permissions
   - Check `OBSERVABILITY_*` environment variables in `.env`
   - Verify AWS region is valid (enhanced security validation prevents injection attacks)

5. **Metrics Collection Issues**
   - Verify CloudWatch permissions: `cloudwatch:PutMetricData`, `cloudwatch:ListMetrics`
   - Check AWS region configuration matches your setup (must be official AWS region)
   - Run `python test_metrics_collector.py` to validate functionality

6. **Health Monitoring Issues**
   - Verify AWS service permissions: Bedrock, Knowledge Base, Cognito Identity access
   - Check AWS region configuration for all monitored services
   - Run `python test_health_monitoring.py` to validate health checks
   - Review health check timeouts and thresholds in configuration

7. **Security Monitoring Issues**
   - Verify CloudWatch Logs permissions for security event logging
   - Check SNS permissions for security alert notifications
   - Run `python test_security_monitoring.py` to validate security features
   - Review security thresholds and compliance framework configuration

For more help, see the troubleshooting section in each module's documentation.