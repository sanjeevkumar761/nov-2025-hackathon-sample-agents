# GitLab Interrogator: AI-Powered Agile Workflow Automation

## Problem Statement

Agile teams face significant manual overhead in GitLab project management:
- 📝 **Manual Story Creation:** Writing user stories and epics is time-consuming
- 📊 **Sprint Analysis:** Summarizing sprint progress requires manual data collection
- 📋 **Release Notes:** Compiling release notes from commits/issues is tedious
- 🏷️ **Epic Organization:** Categorizing and organizing epics lacks consistency
- ⏰ **Time Drain:** Scrum Masters spend hours on reporting instead of coaching
- 🔍 **Inconsistent Quality:** Documentation varies based on who writes it

## Solution

**GitLab Interrogator** is an AI-powered "Scrum Master Digital Employee" that automates four critical Agile workflows using GitLab API integration and LLM intelligence.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               Next.js Frontend (Agile Dashboard)             │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐  │
│  │ Story        │ Sprint       │ Release      │ Epic     │  │
│  │ Creator      │ Analyzer     │ Notes        │ Organizer│  │
│  └──────────────┴──────────────┴──────────────┴──────────┘  │
└───────────────────┬─────────────────────────────────────────┘
                    │ REST API
                    ▼
┌─────────────────────────────────────────────────────────────┐
│           FastAPI Backend (API Gateway)                      │
│  • /api/stories/create                                      │
│  • /api/sprints/summarize                                   │
│  • /api/releases/generate                                   │
│  • /api/epics/categorize                                    │
│  • GitLab API client integration                            │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│        GitLab Interrogator Agent (LangGraph)                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  StateGraph Workflow (5 Nodes)                       │  │
│  │                                                       │  │
│  │  fetch_gitlab_data → analyze_agile_metrics          │  │
│  │     → generate_insights → create_artifacts          │  │
│  │              → compile_report                         │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────┬──────────────────────────────┐
│      GitLab API              │    Azure OpenAI (GPT-4)      │
│  • Issues, MRs, Commits      │  • Story generation          │
│  • Milestones, Labels        │  • Sprint analysis           │
│  • Project metadata          │  • Release notes creation    │
│  • User activity             │  • Epic categorization       │
└──────────────────────────────┴──────────────────────────────┘
```

## Four Core Use Cases

### 1. User Story / Epic Creation
**Purpose:** Generate well-structured user stories and epics from requirements

**Input:**
- Requirement description (text or document)
- Project context
- Acceptance criteria guidelines
- Epic/Story template preferences

**AI Processing:**
- Parse requirements into actionable items
- Generate user story format (As a... I want... So that...)
- Create acceptance criteria
- Estimate story points (Fibonacci scale)
- Suggest sprint assignment
- Generate epic structure with linked stories

**Output:**
- Formatted user stories (Markdown)
- Epic hierarchy
- Acceptance criteria checklist
- Story point estimates
- GitLab issue creation payload

### 2. Sprint Summarization
**Purpose:** Automated sprint retrospective and progress reports

**Input:**
- Sprint milestone ID
- Date range
- Team members
- Project/group ID

**AI Processing:**
- Fetch sprint issues, MRs, commits
- Calculate velocity and completion rate
- Analyze blocked/incomplete items
- Identify patterns and trends
- Generate team performance insights
- Create sprint health metrics

**Output:**
- Sprint summary report
- Velocity chart data
- Burndown analysis
- Team contributions
- Blockers and risks
- Recommendations for next sprint

### 3. Release Notes Generation
**Purpose:** Automatic release documentation from commits and issues

**Input:**
- Version/tag name
- Date range or milestone
- Commit history
- Closed issues/MRs

**AI Processing:**
- Parse commit messages (conventional commits)
- Group by feature/fix/breaking change
- Extract issue references
- Categorize changes
- Generate user-facing descriptions
- Create changelog format

**Output:**
- Structured release notes (Markdown)
- Change categories (Features, Fixes, Breaking)
- Migration guide (if needed)
- Known issues
- Contributor acknowledgments
- GitLab release object payload

### 4. LLM-Based Epic Categorization
**Purpose:** Intelligent epic organization and taxonomy

**Input:**
- List of epics (titles, descriptions, labels)
- Existing taxonomy/categories
- Project goals/themes

**AI Processing:**
- Analyze epic content semantically
- Identify themes and patterns
- Group related epics
- Suggest category hierarchy
- Recommend labels
- Detect dependencies

**Output:**
- Categorized epic structure
- Suggested label taxonomy
- Epic roadmap visualization data
- Dependency graph
- Priority recommendations

## LangGraph Workflow

### 5-Node Sequential Pipeline

```
1. fetch_gitlab_data
   ↓
2. analyze_agile_metrics
   ↓
3. generate_insights
   ↓
4. create_artifacts
   ↓
5. compile_report
```

#### Node 1: Fetch GitLab Data
- Connect to GitLab API using token
- Retrieve relevant data (issues, MRs, commits, milestones)
- Filter by project, date range, milestone
- Extract metadata (labels, assignees, timestamps)
- Cache data for processing

#### Node 2: Analyze Agile Metrics
- Calculate sprint velocity
- Compute completion rates
- Analyze cycle time
- Identify bottlenecks
- Extract team performance data
- Parse commit patterns

#### Node 3: Generate Insights
- Use GPT-4 for semantic analysis
- Generate story descriptions
- Summarize sprint progress
- Create release notes content
- Categorize epics by theme
- Provide recommendations

#### Node 4: Create Artifacts
- Format user stories (Gherkin syntax)
- Structure sprint reports
- Generate changelog (Keep a Changelog format)
- Organize epic hierarchy
- Create visualization data
- Prepare GitLab payloads

#### Node 5: Compile Report
- Assemble final output
- Add executive summary
- Include metrics and charts
- Format for presentation
- Generate actionable items
- Create audit trail

## Technology Stack

### Backend
- **LangGraph 0.2+:** Agentic workflow orchestration
- **LangChain 0.1.16:** LLM framework
- **FastAPI 0.104.1:** Modern async API
- **Azure OpenAI GPT-4:** Natural language processing
- **python-gitlab 4.0+:** GitLab API client
- **Pydantic 2.5:** Data validation

### Frontend
- **Next.js 14.0.4:** React framework
- **TypeScript 5.3.2:** Type safety
- **Tailwind CSS 3.3.6:** Modern styling
- **Chart.js 4.4.0:** Velocity/burndown charts
- **React Query:** Data fetching/caching
- **Lucide React:** Icons

## Key Features

### GitLab Integration
- ✅ OAuth2 authentication
- ✅ Project/Group access
- ✅ Issue management
- ✅ Merge request tracking
- ✅ Milestone queries
- ✅ Commit history
- ✅ Label management
- ✅ Webhook support

### AI Capabilities
- 🤖 Natural language story generation
- 📊 Automated sprint analysis
- 📝 Intelligent release notes
- 🏷️ Semantic epic categorization
- 💡 Recommendation engine
- 🔍 Pattern recognition
- 📈 Predictive insights

### Reporting
- 📄 Markdown export
- 📊 Chart/graph generation
- 📧 Email summaries
- 🔗 GitLab integration
- 📱 Slack/Teams webhooks
- 📥 PDF export

## API Endpoints

### User Story Creation
- `POST /api/stories/create` - Generate user stories from requirements
- `POST /api/stories/bulk` - Batch story creation
- `GET /api/stories/{id}` - Retrieve generated story

### Sprint Analysis
- `POST /api/sprints/summarize` - Analyze sprint completion
- `GET /api/sprints/{milestone_id}` - Get sprint data
- `POST /api/sprints/velocity` - Calculate team velocity

### Release Notes
- `POST /api/releases/generate` - Create release notes
- `GET /api/releases/{tag}` - Get existing release notes
- `POST /api/releases/publish` - Publish to GitLab

### Epic Categorization
- `POST /api/epics/categorize` - Categorize epics by theme
- `POST /api/epics/roadmap` - Generate epic roadmap
- `GET /api/epics/taxonomy` - Get category structure

### GitLab Integration
- `GET /api/gitlab/projects` - List accessible projects
- `GET /api/gitlab/milestones` - List project milestones
- `POST /api/gitlab/webhook` - Webhook endpoint

### System
- `GET /health` - Health check
- `GET /workflow/graph` - Workflow visualization

## Configuration

### Environment Variables

#### Required
```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# GitLab
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your-personal-access-token
GITLAB_PROJECT_ID=12345  # Default project (optional)
```

#### Optional
```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Agile Settings
DEFAULT_STORY_POINTS_SCALE=1,2,3,5,8,13,21
DEFAULT_SPRINT_DURATION=14  # days
ENABLE_AUTO_STORY_CREATION=true

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
EMAIL_NOTIFICATIONS=true
```

## Installation

### Quick Start

**Backend:**
```powershell
cd gitlab-interrogator/backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env with credentials
python gitlab_interrogator_api.py
```

**Frontend:**
```powershell
cd gitlab-interrogator/frontend
npm install
Copy-Item .env.example .env.local
# Edit .env.local
npm run dev
```

**Access:**
- Frontend: http://localhost:3001
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Use Case Examples

### 1. Generate User Story
```json
POST /api/stories/create
{
  "requirement": "Users should be able to export their data in CSV format",
  "project_id": 12345,
  "epic_id": 67890,
  "template": "standard"
}

Response:
{
  "story": {
    "title": "User Data Export to CSV",
    "description": "As a user\nI want to export my data in CSV format\nSo that I can analyze it in Excel or other tools",
    "acceptance_criteria": [
      "Given I am logged in, when I click 'Export', then I see CSV format option",
      "Given I select CSV export, when I confirm, then file downloads within 5 seconds",
      "Given export completes, when I open file, then all my data is included"
    ],
    "story_points": 5,
    "labels": ["feature", "export", "user-experience"]
  }
}
```

### 2. Sprint Summary
```json
POST /api/sprints/summarize
{
  "milestone_id": 123,
  "project_id": 12345
}

Response:
{
  "sprint": "Sprint 42",
  "dates": "2024-11-01 to 2024-11-14",
  "velocity": 45,
  "completion_rate": 0.85,
  "completed_issues": 17,
  "incomplete_issues": 3,
  "blockers": ["API rate limiting", "Dependencies"],
  "recommendations": ["Focus on technical debt", "Add more unit tests"]
}
```

### 3. Release Notes
```json
POST /api/releases/generate
{
  "tag_name": "v2.5.0",
  "from_tag": "v2.4.0",
  "project_id": 12345
}

Response:
{
  "version": "v2.5.0",
  "date": "2024-11-15",
  "features": [
    "Added CSV export functionality",
    "Improved dashboard performance"
  ],
  "fixes": [
    "Fixed login timeout issue",
    "Resolved data sync bug"
  ],
  "breaking_changes": [],
  "contributors": ["@alice", "@bob"]
}
```

### 4. Epic Categorization
```json
POST /api/epics/categorize
{
  "project_id": 12345,
  "epics": [...],
  "categories": ["Infrastructure", "Features", "UX", "Technical Debt"]
}

Response:
{
  "categorized_epics": {
    "Infrastructure": [
      {"id": 1, "title": "Migrate to Kubernetes", "confidence": 0.95}
    ],
    "Features": [
      {"id": 2, "title": "User Dashboard Redesign", "confidence": 0.88}
    ],
    ...
  }
}
```

## Benefits

### For Scrum Masters
- ⏰ Save 10+ hours per sprint on reporting
- 📊 Consistent, data-driven insights
- 🎯 Focus on coaching instead of documentation
- 📈 Better sprint planning with AI recommendations

### For Teams
- 📝 High-quality story templates
- 🔍 Clear acceptance criteria
- 📋 Professional release notes
- 🎨 Well-organized epic structure

### For Stakeholders
- 📊 Real-time sprint visibility
- 📈 Predictable delivery metrics
- 📄 Professional documentation
- ✅ Governance compliance

## Future Enhancements

- [ ] Multi-project analysis
- [ ] Cross-team velocity comparison
- [ ] AI-powered sprint planning
- [ ] Risk prediction models
- [ ] Automated task assignment
- [ ] Integration with Jira migration
- [ ] Custom AI training on team patterns
- [ ] Mobile app

## Documentation

- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Installation instructions
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Command cheatsheet
- [backend/README.md](./backend/README.md) - Backend architecture
- [frontend/README.md](./frontend/README.md) - Frontend guide

## License

Internal use only.

---

**Built with** ❤️ **using LangGraph, FastAPI, Next.js, Azure OpenAI, and GitLab API**
