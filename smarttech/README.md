# SmartTech TSD Agent

AI-powered support ticket classification system using LangGraph, Azure OpenAI, and React.

## 📁 Project Structure

```
smarttech/
├── backend/                    # Python backend (FastAPI + LangGraph)
│   ├── smarttech_api.py       # REST API server
│   ├── smarttech_ticket_agent.py  # Core LangGraph agent
│   ├── smarttech_api_client.py    # API test client
│   ├── prompts/               # Jinja2 prompt templates
│   │   ├── intent_detection.j2
│   │   ├── base_intent_detection.j2
│   │   ├── intent_detection_urgent.j2
│   │   ├── prompt_config.json
│   │   └── README.md
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   ├── .env                  # Your actual environment variables (not in git)
│   └── test_*.py             # Test scripts
│
├── frontend/                  # React UI (Vite + TypeScript)
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── App.tsx          # Main app component
│   │   ├── api.ts           # API client
│   │   └── types.ts         # TypeScript types
│   ├── package.json
│   └── vite.config.ts
│
└── docs/                     # Documentation
    ├── README_SMARTTECH.md              # Main documentation
    ├── QUICKSTART_SMARTTECH.md          # Quick start guide
    ├── LANGGRAPH_AGENT_TUTORIAL.md      # Step-by-step tutorial
    ├── AGENT_LEARNING_EXERCISES.md      # Learning exercises
    ├── EXECUTION_TRACE_GUIDE.md         # Execution tracing guide
    ├── JINJA2_TEMPLATES.md              # Template system docs
    └── TRACE_QUICKSTART.md              # Tracing quick start
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Azure OpenAI account with GPT-4 deployment

### Backend Setup

```bash
# Navigate to backend
cd smarttech/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Start the API server
python smarttech_api.py
```

The API will be available at http://localhost:8000

API Documentation: http://localhost:8000/docs

### Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd smarttech/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The UI will be available at http://localhost:5173

## 🎯 Features

### Core Capabilities

- ✅ **Intent Detection** - Automatically classifies support tickets into 10+ categories
- ✅ **Self-Service Assessment** - Determines if users can resolve issues themselves
- ✅ **KB Article Recommendations** - Suggests relevant knowledge base articles
- ✅ **Smart Routing** - Routes tickets to appropriate support teams
- ✅ **Execution Tracing** - Provides detailed workflow execution history
- ✅ **Configurable Prompts** - Jinja2 templates for easy prompt customization
- ✅ **Workflow Visualization** - Visual display of agent workflow graph

### Technologies

**Backend:**
- LangGraph 0.2+ - Workflow orchestration
- LangChain - LLM integration
- Azure OpenAI - GPT-4 for reasoning
- FastAPI - REST API framework
- Jinja2 - Template engine

**Frontend:**
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- Lucide React - Icons

## 📚 Documentation

### Getting Started
- [README_SMARTTECH.md](./docs/README_SMARTTECH.md) - Comprehensive overview
- [QUICKSTART_SMARTTECH.md](./docs/QUICKSTART_SMARTTECH.md) - Quick setup guide

### Tutorials
- [LANGGRAPH_AGENT_TUTORIAL.md](./docs/LANGGRAPH_AGENT_TUTORIAL.md) - Complete step-by-step tutorial
- [AGENT_LEARNING_EXERCISES.md](./docs/AGENT_LEARNING_EXERCISES.md) - Hands-on exercises

### Features
- [EXECUTION_TRACE_GUIDE.md](./docs/EXECUTION_TRACE_GUIDE.md) - Execution tracing system
- [JINJA2_TEMPLATES.md](./docs/JINJA2_TEMPLATES.md) - Prompt template system
- [TRACE_QUICKSTART.md](./docs/TRACE_QUICKSTART.md) - Quick tracing guide

## 🔧 Configuration

### Environment Variables

Edit `backend/.env`:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

### Prompt Templates

Customize prompts in `backend/prompts/`:
- `intent_detection.j2` - Main intent detection prompt
- `prompt_config.json` - Intent categories and settings

## 📊 API Endpoints

### Classification
- `POST /api/v1/tickets/classify` - Classify a single ticket
- `POST /api/v1/tickets/batch-classify` - Classify multiple tickets

### Data
- `GET /api/v1/tickets/mock` - Get mock tickets for testing
- `GET /api/v1/kb/articles` - Get knowledge base articles

### Workflow
- `GET /api/v1/workflow/graph` - Get workflow structure
- `GET /api/v1/workflow/mermaid` - Get Mermaid diagram syntax

### System
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - Classification statistics

## 🧪 Testing

### Test the Backend

```bash
cd smarttech/backend

# Test Azure OpenAI connection
python -c "from smarttech_ticket_agent import SmartTechTicketAgent; agent = SmartTechTicketAgent(); print('✓ Agent initialized')"

# Test API client
python smarttech_api_client.py

# Test prompt templates
python test_template_prompt.py

# Test execution trace
python test_execution_trace.py
```

### Test the API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get mock tickets
curl http://localhost:8000/api/v1/tickets/mock

# Classify a ticket
curl -X POST http://localhost:8000/api/v1/tickets/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-001",
    "subject": "Cannot access VPN",
    "description": "Getting connection timeout when trying to connect to VPN",
    "category": "Network",
    "priority": "High",
    "user": "test@smarttech.com"
  }'
```

## 🎨 UI Features

- **Modern Design** - Gradient backgrounds, glassmorphism effects
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Real-time Updates** - Live classification results
- **Statistics Dashboard** - Intent and routing distribution
- **Execution Timeline** - Visual workflow execution trace
- **Workflow Graph** - Interactive agent architecture visualization

## 🔐 Security

- Never commit `.env` files to version control
- Use environment variables for sensitive data
- Implement authentication for production deployment
- Add rate limiting to API endpoints
- Sanitize user inputs
- Use HTTPS in production

## 📈 Performance

- **Caching** - Consider implementing LLM response caching
- **Batch Processing** - Use batch endpoint for multiple tickets
- **Async Processing** - FastAPI supports async operations
- **Database** - Add persistence layer for production
- **Monitoring** - Implement logging and metrics

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Azure Deployment

1. Create Azure App Service for backend
2. Create Azure Static Web App for frontend
3. Configure environment variables in Azure
4. Set up CI/CD pipeline with GitHub Actions

### Environment-Specific Configuration

- **Development** - `.env.development`
- **Staging** - `.env.staging`
- **Production** - `.env.production`

## 🐛 Troubleshooting

### Backend Issues

**Agent not initializing:**
- Check Azure OpenAI credentials in `.env`
- Verify endpoint URL format
- Ensure API key is valid

**Import errors:**
- Activate virtual environment
- Run `pip install -r requirements.txt`

### Frontend Issues

**API connection failed:**
- Ensure backend is running on port 8000
- Check CORS configuration
- Verify API base URL in `frontend/src/api.ts`

**Build errors:**
- Run `npm install` to install dependencies
- Clear node_modules and reinstall if needed

## 📝 Development Workflow

1. **Start Backend**: `cd backend && python smarttech_api.py`
2. **Start Frontend**: `cd frontend && npm run dev`
3. **Make Changes**: Edit files and see live reload
4. **Test Changes**: Use API docs and UI to test
5. **Commit**: Git commit with meaningful messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📜 License

[Your License Here]

## 👥 Authors

SmartTech AI Team

## 🔗 Related Projects

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangChain](https://github.com/langchain-ai/langchain)
- [FastAPI](https://github.com/tiangolo/fastapi)
- [React](https://github.com/facebook/react)

---

**Built with ❤️ using LangGraph and Azure OpenAI**

*Last Updated: November 22, 2025*
