# Creds Inspect Backend

AI-powered credential detection agent using LangGraph and FastAPI.

## Architecture

```
creds_inspect_agent.py    → LangGraph agent (5-node workflow)
creds_inspect_api.py      → FastAPI REST API server
requirements.txt          → Python dependencies
.env                      → Environment configuration
```

## Agent Workflow

The LangGraph agent implements a 5-node sequential workflow:

### 1. Scan Content
- **Purpose:** Parse and extract content structure
- **Input:** Raw text, HTML, or document content
- **Output:** Structured content with sections, code blocks, line counts
- **Processing:**
  - Extract code blocks (markdown and HTML)
  - Identify URL patterns
  - Count lines and characters
  - Detect content type

### 2. Detect Credentials
- **Purpose:** Identify exposed credentials using patterns + AI
- **Methods:**
  - **Pattern Detection:** Regex for known credential formats
  - **AI Detection:** GPT-4 context analysis for passwords/secrets
- **Patterns Detected:**
  - AWS Access Keys: `AKIA[0-9A-Z]{16}`
  - AWS Secret Keys: `aws.*[\'\"][0-9a-zA-Z\/+]{40}[\'\"]`
  - Azure Connection Strings
  - GitHub PAT: `ghp_[0-9a-zA-Z]{36}`
  - GitHub OAuth: `gho_[0-9a-zA-Z]{36}`
  - Generic API Keys
  - Generic Secrets/Passwords
  - JWT Tokens
  - Private Keys (RSA, EC, OpenSSH)
  - Database Connection Strings
  - Slack Tokens
  - Bearer Tokens
- **Output:** List of findings with type, position, context, confidence

### 3. Assess Risk
- **Purpose:** Evaluate severity and exposure impact
- **AI Analysis:**
  - Severity classification (High/Medium/Low)
  - Active vs expired assessment
  - Exposure scope (Public/Internal/Private)
  - Compliance risk evaluation
- **Output:** Risk assessment with counts and critical findings

### 4. Generate Remediation
- **Purpose:** Create actionable remediation plans
- **Guidance:**
  - Immediate actions (revoke, rotate)
  - Verification steps
  - Prevention measures
  - Notification templates
  - Timeline estimates
- **Output:** Prioritized remediation plan

### 5. Create Report
- **Purpose:** Generate executive summary
- **Content:**
  - Key findings overview
  - Security impact assessment
  - Compliance implications
  - Recommended immediate actions
  - Prevention strategy
- **Output:** Executive report text

## API Endpoints

### Health & Monitoring
- `GET /health` - Service health check
- `GET /stats` - Overall statistics (scans, findings, risk levels)
- `GET /workflow/graph` - Workflow structure for visualization

### Scan Submission
- `POST /scans/submit` - Submit text content for scanning
  - Body: `{ content, content_type, source_url?, metadata? }`
  - Returns: `{ scan_id, status, message, submitted_at }`

- `POST /scans/upload` - Upload file for scanning
  - Form: `file` (TXT, PDF, DOC, DOCX, HTML)
  - Query: `content_type` (attachment, confluence_page, etc.)
  - Returns: `{ scan_id, status, message, submitted_at }`

### Analysis
- `POST /scans/{scan_id}/analyze` - Start credential scanning
  - Returns: Complete scan result with all findings

### Results
- `GET /scans/{scan_id}` - Get specific scan result
- `GET /scans?limit=50&offset=0` - List all scans (paginated)
- `DELETE /scans/{scan_id}` - Delete scan and associated data

## Data Models

### ScanResult
```python
{
  "scan_id": str,
  "metadata": dict,
  "content_type": str,
  "scan_summary": {
    "credentials_found": int,
    "high_risk": int,
    "medium_risk": int,
    "low_risk": int,
    "overall_risk": "high" | "medium" | "low"
  },
  "detected_credentials": [CredentialFinding],
  "risk_assessment": RiskAssessment,
  "remediation_plan": [RemediationAction],
  "executive_report": str,
  "execution_trace": [TraceStep],
  "status": str,
  "timestamp": str
}
```

### CredentialFinding
```python
{
  "type": str,              # e.g., "aws_access_key"
  "value": str,             # Preview (first 20 chars)
  "position": int,          # Character position
  "line": int,              # Line number
  "context": str,           # Surrounding text
  "detection_method": str,  # "pattern" or "ai"
  "confidence": float,      # 0.0-1.0
  "severity": str,          # "high" | "medium" | "low"
  "is_active": bool,        # Estimated active status
  "exposure_scope": str     # "public" | "internal" | "private"
}
```

### RemediationAction
```python
{
  "credential_type": str,
  "priority": str,               # "immediate" | "urgent" | "normal"
  "immediate_actions": [str],
  "verification_steps": [str],
  "prevention": [str],
  "notification_template": str,
  "timeline": str
}
```

## Configuration

### Environment Variables

#### Required
```env
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

#### API Settings
```env
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173
```

#### App Settings
```env
LOG_LEVEL=INFO
APP_ENV=development
MAX_CONTENT_SIZE_MB=10
UPLOAD_DIR=./uploads
```

#### Detection Settings
```env
ENABLE_PATTERN_DETECTION=true
ENABLE_AI_DETECTION=true
MIN_CONFIDENCE_THRESHOLD=0.7
```

#### Optional: Confluence Integration
```env
CONFLUENCE_URL=https://your-confluence.com
CONFLUENCE_USERNAME=your-username
CONFLUENCE_API_TOKEN=your-token
```

## Installation

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
Copy-Item .env.example .env
# Edit .env with your credentials

# Test agent
python -c "from creds_inspect_agent import create_agent; agent = create_agent()"

# Start server
python creds_inspect_api.py
```

## Usage Examples

### Python Direct Usage
```python
from creds_inspect_agent import create_agent

# Initialize agent
agent = create_agent()

# Scan content
result = agent.scan_content(
    scan_id="test-001",
    content_text="AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
    content_type="text",
    metadata={"source": "test"}
)

# Access results
print(f"Found {len(result['detected_credentials'])} credentials")
print(f"Risk level: {result['scan_summary']['overall_risk']}")
```

### API Usage (PowerShell)
```powershell
# Submit content
$body = @{
    content = "api_key=abc123xyz456"
    content_type = "configuration"
} | ConvertTo-Json

$submission = Invoke-RestMethod -Uri http://localhost:8000/scans/submit -Method Post -Body $body -ContentType "application/json"

# Start analysis
$result = Invoke-RestMethod -Uri "http://localhost:8000/scans/$($submission.scan_id)/analyze" -Method Post

# View results
$result.scan_summary
$result.detected_credentials
$result.remediation_plan
```

## Storage

Current implementation uses **in-memory storage**:
- `scans_storage`: Dict of scan metadata
- `content_storage`: Dict of scan content

For production, migrate to:
- **PostgreSQL** for scan metadata
- **Blob Storage** for content
- **Redis** for caching

## Document Processing

Supported formats:
- **TXT:** UTF-8 text files
- **PDF:** Extracted via PyPDF2
- **DOC/DOCX:** Extracted via python-docx
- **HTML:** Parsed via BeautifulSoup4

## Security Considerations

1. **API Keys:** Store in `.env`, never commit
2. **CORS:** Restrict to trusted origins only
3. **File Uploads:** Limit size, validate types
4. **Content Storage:** Clear sensitive data after analysis
5. **Azure OpenAI:** Use dedicated endpoint, not shared
6. **Logging:** Don't log credential values

## Performance

- **Pattern Detection:** ~100ms for 10KB content
- **AI Detection:** ~2-5 seconds (GPT-4 API call)
- **Full Scan:** ~10-30 seconds depending on content size
- **Concurrent Scans:** Limited by Azure OpenAI rate limits

## Monitoring

Check logs for:
- Agent initialization status
- Scan processing time
- API errors
- Azure OpenAI connection issues

## Extending the Agent

### Add New Credential Pattern
Edit `creds_inspect_agent.py`:
```python
CREDENTIAL_PATTERNS = {
    # ... existing patterns
    'new_credential_type': r'your_regex_pattern',
}
```

### Add New Workflow Node
```python
def _new_node(self, state: CredsInspectState) -> CredsInspectState:
    # Implementation
    return state

# In _build_workflow():
workflow.add_node("new_node", self._new_node)
workflow.add_edge("previous_node", "new_node")
```

### Customize AI Prompts
Edit prompt templates in each node method for:
- Detection sensitivity
- Risk assessment criteria
- Remediation guidance style
- Report format

## Testing

```powershell
# Unit tests
pytest tests/ -v

# Integration test
python -c "
from creds_inspect_agent import create_agent
agent = create_agent()
result = agent.scan_content(
    scan_id='test',
    content_text='AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE',
    content_type='text'
)
assert len(result['detected_credentials']) > 0
print('✓ Test passed')
"
```

## Dependencies

Core:
- `langchain==0.1.16` - LLM framework
- `langgraph==0.0.40` - Agent workflow
- `langchain-openai==0.1.3` - Azure OpenAI integration
- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server

Document parsing:
- `pypdf2==3.0.1` - PDF extraction
- `python-docx==1.1.0` - Word documents
- `beautifulsoup4==4.12.2` - HTML parsing

Utilities:
- `python-dotenv==1.0.0` - Environment variables
- `pydantic==2.5.0` - Data validation

## API Documentation

Once running, visit:
- **Interactive Docs:** http://localhost:8000/docs
- **OpenAPI Schema:** http://localhost:8000/openapi.json

## Troubleshooting

### Agent fails to initialize
- Check Azure OpenAI credentials
- Verify deployment name matches exactly
- Test endpoint connectivity

### Empty detection results
- Verify GPT-4 deployment is active
- Check API version compatibility
- Review prompt templates

### CORS errors
- Add frontend port to CORS_ORIGINS
- Restart backend after .env changes

### File upload fails
- Check UPLOAD_DIR exists
- Verify file size under MAX_CONTENT_SIZE_MB
- Check file format is supported
