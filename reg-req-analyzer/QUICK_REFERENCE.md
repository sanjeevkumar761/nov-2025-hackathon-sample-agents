# Regulatory Requirements Analyzer - Quick Reference

## 🚀 Quick Start Commands

### Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn regulatory_api:app --reload
```

**URL**: http://localhost:8000  
**Docs**: http://localhost:8000/docs

### Frontend

```powershell
cd frontend
npm run dev
```

**URL**: http://localhost:3000

## 📋 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/documents/upload` | POST | Upload document |
| `/api/v1/documents/analyze` | POST | Start analysis |
| `/api/v1/analysis/{id}` | GET | Get results |
| `/api/v1/documents` | GET | List documents |
| `/api/v1/documents/{id}` | DELETE | Delete document |
| `/api/v1/workflow/graph` | GET | Get workflow |

## 🔄 Workflow Nodes

1. **extract_sections** - Parse document structure
2. **identify_lrr** - Extract Laws, Rules, Regulations
3. **categorize_rules** - Classify by priority & type
4. **assess_taxonomy** - Map to organizational taxonomy
5. **generate_summary** - Create executive summary + risk assessment

## 🎨 UI Components

### Main Page (`page.tsx`)
- Server status indicator
- Document upload
- Analysis dashboard
- Workflow visualization toggle

### DocumentUpload
- Drag-and-drop interface
- Metadata form (source, regulator, type)
- Upload status

### AnalysisResults
- Tabbed interface (LRR, Taxonomy, Risk, Summary)
- Real-time analysis progress
- Results visualization

### DocumentsList
- Document selection
- File metadata display
- Delete functionality

## 🔧 Configuration

### Backend `.env`

```env
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_ENDPOINT=<endpoint>
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
API_PORT=8000
MAX_FILE_SIZE_MB=10
```

### Frontend `.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 TypeScript Types

### Key Interfaces

```typescript
interface LRRItem {
  type: 'Law' | 'Rule' | 'Regulation'
  reference: string
  description: string
  requirement: string
  obligated_parties: string[]
  penalties?: string[]
  severity: 'high' | 'medium' | 'low'
}

interface TaxonomyImpact {
  area: string
  impact_type: string
  description: string
  urgency: 'high' | 'medium' | 'low'
  recommended_action: string
}

interface RiskAssessment {
  high_risks: string[]
  medium_risks: string[]
  low_risks: string[]
  overall_risk_level: 'high' | 'medium' | 'low'
}
```

## 🛠️ Common Commands

### Backend

```powershell
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn regulatory_api:app --reload

# Run tests
pytest tests/ -v

# Check health
curl http://localhost:8000/api/v1/health
```

### Frontend

```powershell
# Install dependencies
npm install

# Development
npm run dev

# Build production
npm run build

# Start production
npm start

# Type check
npm run type-check
```

## 🐛 Troubleshooting

### Backend not starting?

```powershell
# Check venv activated
.\venv\Scripts\Activate.ps1

# Check dependencies
pip list

# Check port
netstat -ano | findstr :8000
```

### Frontend errors?

```powershell
# Clear and reinstall
rm -r node_modules, package-lock.json
npm install

# Restart dev server
npm run dev
```

### API connection issues?

```powershell
# Test backend
curl http://localhost:8000/api/v1/health

# Check environment
cat .env.local
```

## 📦 File Structure

```
reg-req-analyzer/
├── backend/
│   ├── regulatory_analyzer.py  # LangGraph agent
│   ├── regulatory_api.py       # FastAPI server
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── AnalysisResults.tsx
│   │   │   ├── RiskAssessment.tsx
│   │   │   ├── DocumentsList.tsx
│   │   │   └── WorkflowVisualization.tsx
│   │   ├── lib/
│   │   │   └── api.ts
│   │   └── types/
│   │       └── index.ts
│   └── package.json
└── README.md
```

## 🎯 Testing Workflow

1. Start backend: `uvicorn regulatory_api:app --reload`
2. Start frontend: `npm run dev`
3. Open http://localhost:3000
4. Upload test document (PDF/DOCX/TXT)
5. Fill metadata (source, regulator, type)
6. Click "Start Analysis"
7. Wait 30-60 seconds
8. View results in tabs

## 💡 Tips

- **Large documents**: May take 60+ seconds to analyze
- **Temperature**: Lower = more deterministic (set in `regulatory_analyzer.py`)
- **Styling**: Custom Tailwind utilities in `globals.css`
- **API errors**: Check browser DevTools Network tab
- **Backend logs**: Check Uvicorn console output

## 🔗 Quick Links

- Backend Swagger: http://localhost:8000/docs
- Backend ReDoc: http://localhost:8000/redoc
- Frontend: http://localhost:3000
- Setup Guide: `SETUP_GUIDE.md`
- Backend README: `backend/README.md`
- Frontend README: `frontend/README.md`

## 📞 Need Help?

1. Check logs (backend terminal + browser console)
2. Review API documentation
3. Read troubleshooting sections in READMEs
4. Contact development team

---

**Version**: 1.0.0  
**Last Updated**: January 2024
