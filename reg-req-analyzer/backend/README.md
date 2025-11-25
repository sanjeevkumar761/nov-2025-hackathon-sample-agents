# Regulatory Requirements Analyzer - Backend

FastAPI backend with LangGraph agent for automated regulatory document analysis.

## Features

- 🤖 5-node LangGraph workflow for sequential analysis
- 📄 Multi-format document parsing (PDF, DOCX, TXT)
- 🔍 AI-powered LRR extraction using GPT-4
- 📊 Taxonomy impact assessment
- ⚠️ Risk assessment with severity categorization
- 🔗 RESTful API with automatic OpenAPI documentation
- 📝 Execution tracing for transparency

## Tech Stack

- **Framework**: FastAPI 0.104+
- **AI**: LangChain, LangGraph, Azure OpenAI GPT-4
- **Document Processing**: PyPDF2, python-docx, BeautifulSoup4
- **ASGI Server**: Uvicorn
- **Environment**: Python 3.9+

## Prerequisites

- Python 3.9 or higher
- Azure OpenAI API access with GPT-4 deployment
- pip or conda for package management

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the `backend/` directory:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# File Upload Settings
MAX_FILE_SIZE_MB=10
UPLOAD_DIR=./uploads

# Optional: Database (for production)
# DATABASE_URL=postgresql://user:pass@localhost/reganalyzer
```

## Running the Server

```bash
# Development mode with auto-reload
uvicorn regulatory_api:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn regulatory_api:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will start at: `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```http
GET /api/v1/health
```

### Upload Document
```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data

file: <binary>
metadata: {"source": "ESMA", "regulator": "EU", "document_type": "regulation"}
```

### Analyze Document
```http
POST /api/v1/documents/analyze
Content-Type: application/json

{
  "document_id": "doc_12345"
}
```

### Get Analysis Results
```http
GET /api/v1/analysis/{document_id}
```

### List Documents
```http
GET /api/v1/documents
```

### Delete Document
```http
DELETE /api/v1/documents/{document_id}
```

### Get Workflow Graph
```http
GET /api/v1/workflow/graph
```

## LangGraph Workflow

The agent uses a 5-node sequential workflow:

```
extract_sections → identify_lrr → categorize_rules → assess_taxonomy → generate_summary
```

### Node Descriptions

1. **extract_sections**: Parses document structure, extracts sections, definitions, effective dates
2. **identify_lrr**: Identifies Laws, Rules, Regulations with severity, obligations, penalties
3. **categorize_rules**: Categorizes by priority (high/medium/low) and type (reporting, operational, deadlines)
4. **assess_taxonomy**: Analyzes organizational taxonomy impacts and recommendations
5. **generate_summary**: Creates executive summary with risk assessment

## Document Processing

### Supported Formats

- **PDF**: Text extraction via PyPDF2
- **DOCX**: Table and paragraph extraction via python-docx
- **TXT**: Direct UTF-8 decoding

### File Size Limits

Default: 10MB per file (configurable via `MAX_FILE_SIZE_MB`)

## Testing

```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest --cov=. --cov-report=html

# Test specific endpoint
pytest tests/test_api.py::test_upload_document -v
```

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload document
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@sample_regulation.pdf" \
  -F 'metadata={"source":"ESMA","regulator":"EU"}'

# Analyze document
curl -X POST "http://localhost:8000/api/v1/documents/analyze" \
  -H "Content-Type: application/json" \
  -d '{"document_id":"doc_12345"}'

# Get results
curl http://localhost:8000/api/v1/analysis/doc_12345
```

## Project Structure

```
backend/
├── regulatory_analyzer.py   # LangGraph agent (600+ lines)
│   ├── RegulatoryState      # State management
│   ├── _extract_sections()  # Node 1
│   ├── _identify_lrr()      # Node 2
│   ├── _categorize_rules()  # Node 3
│   ├── _assess_taxonomy()   # Node 4
│   ├── _generate_summary()  # Node 5
│   ├── analyze_document()   # Main entry point
│   └── get_workflow_graph() # Workflow visualization
├── regulatory_api.py        # FastAPI server (500+ lines)
│   ├── CORS configuration
│   ├── Document upload endpoint
│   ├── Analysis endpoints
│   ├── Document management
│   └── Error handling
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── uploads/                 # Temporary file storage
```

## Configuration

### Adjust GPT-4 Parameters

In `regulatory_analyzer.py`:

```python
llm = AzureChatOpenAI(
    temperature=0.2,  # Lower = more deterministic (0.0-1.0)
    max_tokens=2000,  # Response length limit
    # ... other params
)
```

### Change Workflow Structure

```python
# Add conditional edges
workflow.add_conditional_edges(
    "categorize_rules",
    lambda state: "high_priority" if has_high_priority(state) else "normal",
    {
        "high_priority": "urgent_assessment",
        "normal": "assess_taxonomy"
    }
)
```

## Performance Optimization

### 1. Caching

Add Redis for analysis result caching:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379)

# Cache results
redis_client.setex(f"analysis:{doc_id}", 3600, json.dumps(result))
```

### 2. Async Processing

Use Celery for background analysis:

```python
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379')

@celery_app.task
def analyze_document_task(doc_id):
    return analyze_document(doc_id)
```

### 3. Database Integration

Replace in-memory storage with PostgreSQL:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)
```

## Error Handling

The API includes comprehensive error handling:

- 400: Bad Request (invalid input)
- 404: Document not found
- 413: File too large
- 422: Validation error
- 500: Internal server error
- 503: Azure OpenAI service unavailable

## Security Considerations

### Production Checklist

- [ ] Set strong API keys (rotate regularly)
- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting (e.g., SlowAPI)
- [ ] Add authentication (OAuth2/JWT)
- [ ] Validate file types (MIME type checking)
- [ ] Scan uploaded files for malware
- [ ] Use database instead of in-memory storage
- [ ] Enable audit logging
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure firewall rules

### Example: Add API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Add to endpoints
@app.post("/api/v1/documents/upload", dependencies=[Depends(verify_api_key)])
```

## Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "regulatory_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t reg-analyzer-backend .
docker run -p 8000:8000 --env-file .env reg-analyzer-backend
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reg-analyzer-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: reg-analyzer
  template:
    metadata:
      labels:
        app: reg-analyzer
    spec:
      containers:
      - name: backend
        image: reg-analyzer-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: reg-analyzer-secrets
```

## Monitoring

### Health Checks

```bash
# Kubernetes liveness probe
curl http://localhost:8000/api/v1/health

# Expected response
{"status": "healthy", "timestamp": "2024-01-15T10:30:00Z"}
```

### Logging

Configure structured logging:

```python
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}'
)
```

## Troubleshooting

### Azure OpenAI Connection Issues

```bash
# Test connectivity
curl -X POST "https://your-resource.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-02-15-preview" \
  -H "api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

### PDF Extraction Issues

```python
# Install additional dependencies for complex PDFs
pip install pdfminer.six
```

### Memory Issues with Large Documents

```python
# Increase chunk size for processing
MAX_CHUNK_SIZE = 10000  # characters

# Process in chunks
for i in range(0, len(text), MAX_CHUNK_SIZE):
    chunk = text[i:i+MAX_CHUNK_SIZE]
    process_chunk(chunk)
```

## License

Private - Internal Use Only
