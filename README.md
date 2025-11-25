# LangGraph Agents with Azure OpenAI

A collection of LangGraph agents using Azure OpenAI, based on the [Azure Samples reference](https://github.com/Azure-Samples/app-service-agentic-langgraph-foundry-python).

## Available Agents

This repository contains multiple specialized agents:

- **[ASR Data Handshake](./asr-data-handshake/)** - Agent for enriching ASR (Automated Service Request) data
- **[Creds Impact](./creds-impact/)** - Credential inspection and security risk assessment agent
- **[GitLab Interrogator](./gitlab-interrogator/)** - GitLab project analysis, sprint tracking, and release notes generation
- **[Reg Req Analyzer](./reg-req-analyzer/)** - Regulatory requirements analysis and compliance assessment
- **[SmartTech](./smarttech/)** - IT ticket classification and routing agent with execution tracing

Each agent has its own frontend/backend implementation with detailed documentation in their respective directories.

## Getting Started

Each agent has its own setup instructions and documentation:

- **ASR Data Handshake**: See [asr-data-handshake/README.md](./asr-data-handshake/README.md)
- **Creds Impact**: See [creds-impact/README.md](./creds-impact/README.md) and [SETUP_GUIDE.md](./creds-impact/SETUP_GUIDE.md)
- **GitLab Interrogator**: See [gitlab-interrogator/README.md](./gitlab-interrogator/README.md) and [SETUP_GUIDE.md](./gitlab-interrogator/SETUP_GUIDE.md)
- **Reg Req Analyzer**: See [reg-req-analyzer/README.md](./reg-req-analyzer/README.md) and [SETUP_GUIDE.md](./reg-req-analyzer/SETUP_GUIDE.md)
- **SmartTech**: See [smarttech/README.md](./smarttech/README.md) and [QUICKSTART_SMARTTECH.md](./smarttech/docs/QUICKSTART_SMARTTECH.md)

## Common Features

- **Azure OpenAI Integration**: All agents use Azure OpenAI with API key authentication
- **ReAct Agent Pattern**: Implements Reasoning and Acting agent patterns
- **Custom Tools**: Each agent includes specialized tools for its domain
- **Memory Management**: Maintains conversation context using thread IDs
- **Frontend/Backend Architecture**: Modern React/Next.js frontends with Python FastAPI backends
- **Execution Tracing**: Built-in support for monitoring agent execution flow

