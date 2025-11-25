# Creds Inspect - AI-Powered Credential Scanner

AI agent for detecting and remediating exposed credentials in Confluence pages and attachments using LangGraph and Azure OpenAI.

## 🎯 Problem Statement

Credentials stored in collaboration platforms create significant security and regulatory risks:
- 🔐 **Security Risk**: API keys, tokens, passwords exposed in wikis
- 📄 **Scattered Storage**: Credentials in pages, comments, attachments
- ⏰ **Slow Detection**: Manual scanning is time-consuming
- 🔍 **Inconsistent Triage**: Human triage varies in quality
- ⚠️ **Compliance Issues**: Regulatory violations from exposed secrets

## 💡 Solution

AI-powered credential scanning with:
- 🤖 Automated detection across Confluence content
- 🎯 AI-based risk assessment and triage
- 📊 Remediation guidance and prioritization
- 🔄 Continuous monitoring capability
- 📈 Executive reporting

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Next.js Frontend (UI)                      │
│  - Content submission (URLs, files, text)                   │
│  - Credential detection dashboard                            │
│  - Risk visualization                                        │
│  - Remediation tracking                                      │
└───────────────────┬─────────────────────────────────────────┘
                    │ HTTP/REST API
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (API Server)                    │
│  - /api/v1/scans/submit                                     │
│  - /api/v1/scans/analyze                                    │
│  - /api/v1/results/{scan_id}                                │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│         Creds Inspect Agent (LangGraph)                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  StateGraph Workflow                                 │  │
│  │                                                       │  │
│  │  scan_content → detect_credentials → assess_risk    │  │
│  │       → generate_remediation → create_report         │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              Azure OpenAI (GPT-4)                           │
│  - Pattern recognition                                       │
│  - Risk assessment                                          │
│  - Remediation guidance                                     │
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

python creds_inspect_api.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 🔄 LangGraph Workflow

### 5-Node Sequential Pipeline

1. **scan_content** - Extract and parse Confluence content
2. **detect_credentials** - Identify credentials using AI + patterns
3. **assess_risk** - Evaluate severity and exposure
4. **generate_remediation** - Create action plans
5. **create_report** - Executive summary with prioritization

## 🎨 Features

### Credential Detection
- API keys (AWS, Azure, GitHub, etc.)
- Passwords and secrets
- Tokens (JWT, OAuth, PAT)
- Database connection strings
- Private keys (SSH, PGP)
- Certificates

### Risk Assessment
- Exposure severity (High/Medium/Low)
- Validity check (active vs expired)
- Scope analysis (public vs private)
- Impact assessment
- Compliance risk rating

### Remediation Guidance
- Immediate actions (revoke, rotate)
- Prevention measures
- Alternative secure storage
- Policy recommendations
- Notification templates

## 📊 Detection Capabilities

| Credential Type | Detection Method | Risk Level |
|----------------|------------------|------------|
| AWS Keys | Pattern + AI | High |
| Azure Tokens | Pattern + AI | High |
| GitHub PAT | Pattern + AI | High |
| Passwords | AI Context | Medium-High |
| API Keys | Pattern + AI | High |
| SSH Keys | Pattern | High |
| DB Strings | Pattern + AI | High |

## 🔧 Technology Stack

**Backend:**
- LangGraph - Workflow orchestration
- FastAPI - REST API framework
- Azure OpenAI - GPT-4 for analysis
- BeautifulSoup - HTML parsing
- PyPDF2/python-docx - Document parsing

**Frontend:**
- Next.js 14 - React framework
- TypeScript - Type safety
- Tailwind CSS - Modern styling
- Chart.js - Risk visualization

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/scans/submit` | Submit content for scanning |
| POST | `/api/v1/scans/analyze` | Start credential analysis |
| GET | `/api/v1/results/{scan_id}` | Get scan results |
| GET | `/api/v1/scans` | List all scans |
| DELETE | `/api/v1/scans/{scan_id}` | Delete scan |
| GET | `/api/v1/workflow/graph` | Get workflow structure |

## 🎯 Use Cases

1. **Confluence Page Scanning**: Scan wiki pages for exposed credentials
2. **Attachment Analysis**: Extract and scan PDFs, Word docs, text files
3. **Bulk Scanning**: Process multiple pages/spaces
4. **Continuous Monitoring**: Schedule regular scans
5. **Incident Response**: Quick triage of reported exposures

## 📈 Metrics & Reporting

- Total credentials found
- Risk distribution (High/Medium/Low)
- Remediation status tracking
- Time to remediation
- Recurrence analysis
- Compliance dashboard

## 🔒 Security Features

- No credential storage (scan only)
- Encrypted API communication
- Audit logging
- Role-based access control
- Secure credential handling

## 📚 Documentation

- [Backend Documentation](./backend/README.md)
- [Frontend Documentation](./frontend/README.md)
- [Setup Guide](./SETUP_GUIDE.md)
- [API Reference](http://localhost:8000/docs)

## 🎉 Future Enhancements

- [ ] Direct Confluence API integration
- [ ] Slack/Teams notifications
- [ ] Automated credential revocation
- [ ] Historical trend analysis
- [ ] Custom detection rules
- [ ] Multi-platform support (Jira, SharePoint)
- [ ] Browser extension
- [ ] CLI tool

## 📞 Support

For issues or questions, contact the security team.

---

**Built with** ❤️ **using LangGraph, FastAPI, Next.js, and Azure OpenAI GPT-4**
