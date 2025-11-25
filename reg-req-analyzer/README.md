# Regulatory Requirements Analyzer

AI-powered system for analyzing regulatory documents and extracting Laws, Rules, and Regulations (LRR) using LangGraph and Azure OpenAI.

## 🎯 Problem Statement

Manual review of regulatory documents is:
- ⏰ Time-consuming and labor-intensive
- 📄 Requires processing substantial volumes
- 🔍 Prone to human error
- ⚖️ Introduces compliance risks
- 📊 Causes operational delays

## 💡 Solution

Automated regulatory document analysis using AI to:
- Extract Laws, Rules, and Regulations (LRR)
- Identify taxonomy impacts
- Categorize compliance requirements
- Generate structured summaries
- Highlight key obligations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Next.js Frontend (UI)                      │
│  - Document upload                                           │
│  - Analysis dashboard                                        │
│  - Results visualization                                     │
│  - Compliance tracking                                       │
└───────────────────┬─────────────────────────────────────────┘
                    │ HTTP/REST API
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (API Server)                    │
│  - /api/v1/documents/upload                                 │
│  - /api/v1/documents/analyze                                │
│  - /api/v1/analysis/results/{id}                            │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│         Regulatory Analyzer Agent (LangGraph)               │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  StateGraph Workflow                                 │  │
│  │                                                       │  │
│  │  ┌─────────────┐      ┌─────────────┐              │  │
│  │  │   Extract   │──────▶│   Identify  │              │  │
│  │  │   Content   │      │     LRR     │              │  │
│  │  └─────────────┘      └─────────────┘              │  │
│  │         │                     │                      │  │
│  │         ▼                     ▼                      │  │
│  │  ┌─────────────┐      ┌─────────────┐              │  │
│  │  │  Categorize │──────▶│  Generate   │              │  │
│  │  │    Rules    │      │   Summary   │              │  │
│  │  └─────────────┘      └─────────────┘              │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              Azure OpenAI (GPT-4)                           │
│  - Document understanding                                    │
│  - LRR extraction                                           │
│  - Categorization                                           │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Azure OpenAI account with GPT-4 deployment

### Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt

# Configure .env file
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

python regulatory_api.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentation

- [Backend API Documentation](./backend/README.md)
- [Frontend Guide](./frontend/README.md)
- [Deployment Guide](./DEPLOYMENT.md)

## 🔧 Technology Stack

**Backend:**
- LangGraph - Workflow orchestration
- FastAPI - REST API framework
- Azure OpenAI - GPT-4 for analysis
- PyPDF2/python-docx - Document parsing

**Frontend:**
- Next.js 14 - React framework
- Vite - Build tool
- TypeScript - Type safety
- Tailwind CSS - Styling

## 📝 License

[Your License]
