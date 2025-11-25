# Creds Inspect - Setup Guide

Complete setup instructions for the Creds Inspect credential detection system.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Running the Application](#running-the-application)
- [Verifying Installation](#verifying-installation)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Python 3.11+** with pip and virtual environment support
- **Node.js 18+** with npm
- **Azure OpenAI** account with GPT-4 deployment

### Azure OpenAI Requirements
You need:
1. Azure OpenAI endpoint URL
2. API key
3. GPT-4 deployment name
4. API version (2024-08-01-preview or later)

---

## Backend Setup

### 1. Navigate to Backend Directory
```powershell
cd backend
```

### 2. Create Python Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

This installs:
- LangChain & LangGraph (AI agent framework)
- FastAPI & Uvicorn (API server)
- Azure OpenAI SDK
- Document parsers (PyPDF2, python-docx, BeautifulSoup4)

### 4. Configure Environment Variables

Copy the example file:
```powershell
Copy-Item .env.example .env
```

Edit `.env` with your credentials:
```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173

# App Configuration
LOG_LEVEL=INFO
APP_ENV=development
MAX_CONTENT_SIZE_MB=10
UPLOAD_DIR=./uploads

# Detection Settings
ENABLE_PATTERN_DETECTION=true
ENABLE_AI_DETECTION=true
MIN_CONFIDENCE_THRESHOLD=0.7
```

### 5. Test Backend
```powershell
# Test agent initialization
python -c "from creds_inspect_agent import create_agent; agent = create_agent(); print('✓ Agent initialized')"

# Start API server
python creds_inspect_api.py
```

Expected output:
```
INFO:     Creds Inspect API Server Starting
INFO:     ✓ Agent initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Visit: http://localhost:8000/docs to see API documentation

---

## Frontend Setup

### 1. Navigate to Frontend Directory
```powershell
cd ..\frontend
```

### 2. Install Dependencies
```powershell
npm install
```

This installs:
- Next.js 14 (React framework)
- Tailwind CSS (styling)
- Axios (API client)
- Chart.js (visualizations)
- Lucide React (icons)
- React Dropzone (file uploads)

### 3. Configure Environment

Copy the example file:
```powershell
Copy-Item .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Test Frontend
```powershell
npm run dev
```

Expected output:
```
▲ Next.js 14.0.4
- Local:        http://localhost:3001
- Ready in 2.5s
```

Visit: http://localhost:3001

---

## Running the Application

### Option 1: Run Both Services Manually

**Terminal 1 (Backend):**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python creds_inspect_api.py
```

**Terminal 2 (Frontend):**
```powershell
cd frontend
npm run dev
```

### Option 2: Production Build

**Backend (no changes):**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python creds_inspect_api.py
```

**Frontend (optimized):**
```powershell
cd frontend
npm run build
npm start
```

---

## Verifying Installation

### 1. Backend Health Check
```powershell
# PowerShell
Invoke-RestMethod -Uri http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "agent_ready": true,
  "version": "1.0.0"
}
```

### 2. Frontend Access
Open browser: http://localhost:3001

You should see:
- **Creds Inspect** header with shield icon
- Navigation tabs (New Scan, Results, History)
- Stats overview cards
- Content submission form

### 3. End-to-End Test

1. Click **"Paste Text"** tab
2. Paste sample content with a credential:
```
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```
3. Click **"Scan for Credentials"**
4. Wait for analysis (10-30 seconds)
5. View results:
   - 2 credentials detected
   - High risk level
   - AWS credentials identified
   - Remediation plan provided

---

## Troubleshooting

### Backend Issues

#### Error: "Agent not initialized"
**Cause:** Azure OpenAI credentials incorrect or endpoint unreachable

**Fix:**
1. Verify `.env` file has correct credentials
2. Test Azure OpenAI connection:
```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); from langchain_openai import AzureChatOpenAI; llm = AzureChatOpenAI(azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'), api_key=os.getenv('AZURE_OPENAI_API_KEY'), azure_deployment=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'), api_version=os.getenv('AZURE_OPENAI_API_VERSION')); print(llm.invoke('test'))"
```

#### Error: "Module not found"
**Cause:** Missing dependencies

**Fix:**
```powershell
pip install -r requirements.txt --upgrade
```

#### Port 8000 already in use
**Fix:**
```powershell
# Change port in .env
API_PORT=8001

# Restart backend
```

### Frontend Issues

#### Error: "Cannot connect to API"
**Cause:** Backend not running or wrong API URL

**Fix:**
1. Check backend is running: http://localhost:8000/health
2. Verify `.env.local` has correct API URL
3. Check browser console for CORS errors
4. Restart both services

#### Styling not working
**Cause:** Tailwind CSS not compiled

**Fix:**
```powershell
# Clean and rebuild
Remove-Item -Recurse -Force .next
npm run dev
```

#### Module errors during npm install
**Fix:**
```powershell
# Clear cache and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

### Common Issues

#### CORS Errors
**Cause:** Frontend port not in CORS_ORIGINS

**Fix:** Update `backend/.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173
```
Restart backend.

#### Analysis returns empty results
**Cause:** Azure OpenAI deployment name mismatch

**Fix:** Verify exact deployment name in Azure Portal matches `.env`:
```env
AZURE_OPENAI_DEPLOYMENT_NAME=your-exact-deployment-name
```

#### File upload fails
**Cause:** Upload directory doesn't exist

**Fix:**
```powershell
cd backend
New-Item -ItemType Directory -Path uploads -Force
```

---

## Next Steps

1. **Read the QUICK_REFERENCE.md** for common commands
2. **Review backend/README.md** for API details
3. **Check frontend/README.md** for component documentation
4. **Test with real Confluence content**
5. **Configure Confluence API** for URL scanning (optional)

---

## Support

For issues:
1. Check error logs in terminal
2. Verify environment variables
3. Test API health endpoint
4. Review browser console for frontend errors
5. Ensure Python 3.11+ and Node.js 18+ are installed

For Azure OpenAI issues, verify:
- Deployment is active
- API key is valid
- Endpoint URL is correct
- GPT-4 model is deployed
