# Creds Inspect - Quick Reference

Command cheatsheet for daily operations.

## Backend Commands

### Environment Setup
```powershell
# Activate virtual environment
cd backend
.\venv\Scripts\Activate.ps1

# Deactivate
deactivate
```

### Start Backend
```powershell
# Development mode (auto-reload)
python creds_inspect_api.py

# Or with uvicorn directly
uvicorn creds_inspect_api:app --host 0.0.0.0 --port 8000 --reload
```

### Test Backend
```powershell
# Health check
Invoke-RestMethod -Uri http://localhost:8000/health

# Get workflow graph
Invoke-RestMethod -Uri http://localhost:8000/workflow/graph

# List scans
Invoke-RestMethod -Uri http://localhost:8000/scans

# Get stats
Invoke-RestMethod -Uri http://localhost:8000/stats
```

### Update Dependencies
```powershell
pip install -r requirements.txt --upgrade
pip freeze > requirements.txt  # After adding new packages
```

---

## Frontend Commands

### Start Frontend
```powershell
cd frontend

# Development mode (hot reload)
npm run dev

# Production build
npm run build
npm start

# Lint check
npm run lint
```

### Update Dependencies
```powershell
# Update all packages
npm update

# Update specific package
npm install axios@latest

# Clean install
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

---

## API Endpoints Reference

### Health & Info
- `GET /health` - Health check
- `GET /stats` - Overall statistics
- `GET /workflow/graph` - Workflow structure

### Scan Operations
- `POST /scans/submit` - Submit text content
- `POST /scans/upload` - Upload file
- `POST /scans/{id}/analyze` - Start analysis
- `GET /scans/{id}` - Get scan result
- `GET /scans` - List all scans
- `DELETE /scans/{id}` - Delete scan

---

## Common Tasks

### Submit Text for Scanning
```powershell
$body = @{
    content = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
    content_type = "text"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/scans/submit -Method Post -Body $body -ContentType "application/json"
```

### Upload File
```powershell
$file = Get-Item ".\test.txt"
$form = @{
    file = $file
}
Invoke-RestMethod -Uri "http://localhost:8000/scans/upload?content_type=attachment" -Method Post -Form $form
```

### Analyze Scan
```powershell
$scanId = "your-scan-id"
Invoke-RestMethod -Uri "http://localhost:8000/scans/$scanId/analyze" -Method Post
```

### Get Results
```powershell
$scanId = "your-scan-id"
Invoke-RestMethod -Uri "http://localhost:8000/scans/$scanId"
```

---

## Environment Variables

### Backend (.env)
```env
# Required
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173

# Optional
UPLOAD_DIR=./uploads
MAX_CONTENT_SIZE_MB=10
ENABLE_PATTERN_DETECTION=true
ENABLE_AI_DETECTION=true
MIN_CONFIDENCE_THRESHOLD=0.7
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Port Reference
- **Backend API:** 8000
- **Frontend Dev:** 3001
- **Frontend Prod:** 3001
- **OpenAPI Docs:** http://localhost:8000/docs

---

## Debugging

### Backend Logs
```powershell
# Enable debug logging
# In .env: LOG_LEVEL=DEBUG
python creds_inspect_api.py
```

### Frontend Logs
```powershell
# Browser console (F12)
# Check Network tab for API calls
# Check Console for errors
```

### Test Agent Directly
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python

# In Python REPL:
from creds_inspect_agent import create_agent
agent = create_agent()
result = agent.scan_content(
    scan_id="test-123",
    content_text="AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
    content_type="text"
)
print(result)
```

---

## Credential Pattern Examples

### AWS Keys
```
AKIA[0-9A-Z]{16}
```

### GitHub PAT
```
ghp_[0-9a-zA-Z]{36}
```

### Azure Connection String
```
DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...
```

### Generic API Key
```
api_key="abc123xyz456"
apikey: "secret-key-here"
```

### JWT Token
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Maintenance

### Clear Scans
```powershell
# Delete all scans via API
$scans = Invoke-RestMethod -Uri http://localhost:8000/scans
foreach ($scan in $scans) {
    Invoke-RestMethod -Uri "http://localhost:8000/scans/$($scan.scan_id)" -Method Delete
}
```

### Clear Uploads
```powershell
Remove-Item backend/uploads/* -Force
```

### Reset Frontend
```powershell
cd frontend
Remove-Item -Recurse -Force .next
npm run dev
```

---

## Production Deployment

### Backend
```powershell
# Use production WSGI server
pip install gunicorn
gunicorn creds_inspect_api:app --workers 4 --bind 0.0.0.0:8000
```

### Frontend
```powershell
# Build and start
npm run build
npm start

# Or export static
npm run build
npx next export
```

---

## Testing

### Backend Tests
```powershell
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

### Frontend Tests
```powershell
# Run linter
npm run lint

# Type check
npx tsc --noEmit
```

---

## Useful Links
- Backend API Docs: http://localhost:8000/docs
- Frontend Dev: http://localhost:3001
- Azure OpenAI Studio: https://oai.azure.com/
- LangGraph Docs: https://langchain-ai.github.io/langgraph/
