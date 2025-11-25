# GitLab Interrogator Backend

AI-powered backend service for GitLab Agile workflow automation.

## Architecture

```
Backend Structure:
├── gitlab_interrogator_agent.py   # LangGraph agent (5-node workflow)
├── gitlab_interrogator_api.py     # FastAPI REST API
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment configuration template
└── README.md                      # This file
```

## LangGraph Agent Workflow

The `GitLabInterrogatorAgent` uses a 5-node sequential workflow:

### Node 1: fetch_gitlab_data
- Connects to GitLab API using `python-gitlab`
- Authenticates with personal access token
- Fetches use-case-specific data:
  - **Story Creation**: Project context, epics, labels
  - **Sprint Summary**: Milestone issues, merge requests, commits
  - **Release Notes**: Commits, closed issues, merged MRs
  - **Epic Categorization**: All epics with descriptions and labels

### Node 2: analyze_agile_metrics
- Calculates sprint metrics:
  - Velocity (completed story points)
  - Completion rate (closed vs total issues)
  - Cycle time (average time to close)
- Parses conventional commits for release categorization
- Counts epic states and label frequency

### Node 3: generate_insights
- Uses Azure OpenAI GPT-4 for semantic analysis
- **Story Creation**: Generates user story format with acceptance criteria
- **Sprint Summary**: Analyzes performance, identifies blockers, provides recommendations
- **Release Notes**: Creates user-facing change descriptions
- **Epic Categorization**: Groups epics by semantic theme with confidence scores

### Node 4: create_artifacts
- Formats outputs for consumption:
  - User stories in Gherkin format (Given/When/Then)
  - Sprint reports with Markdown sections
  - Release notes in Keep a Changelog format
  - Epic taxonomy with category hierarchy

### Node 5: compile_report
- Assembles final output with metadata
- Adds execution trace for transparency
- Includes timestamps and processing status

## FastAPI REST API

### Endpoints by Use Case

**User Story Creation:**
- `POST /api/stories/create` - Generate single user story
- `POST /api/stories/bulk` - Generate multiple stories
- `POST /api/stories/to-gitlab` - Create GitLab issues (placeholder)

**Sprint Summary:**
- `POST /api/sprints/summarize` - Analyze sprint performance
- `GET /api/sprints/{id}/velocity` - Historical velocity data
- `GET /api/sprints/{id}/burndown` - Burndown chart data (placeholder)

**Release Notes:**
- `POST /api/releases/generate` - Generate release notes from commits
- `GET /api/releases/{tag}/changelog` - Get existing changelog
- `POST /api/releases/publish` - Publish to GitLab (placeholder)

**Epic Categorization:**
- `POST /api/epics/categorize` - Semantic epic grouping
- `POST /api/epics/roadmap` - Generate roadmap (placeholder)
- `GET /api/epics/taxonomy` - Get category structure

**GitLab Integration:**
- `GET /api/gitlab/projects` - List accessible projects
- `GET /api/gitlab/milestones` - List project milestones
- `GET /api/gitlab/issues` - Query issues with filters

**System:**
- `GET /health` - Health check (agent + GitLab status)
- `GET /workflow/graph` - Workflow visualization data
- `GET /stats` - Usage statistics (placeholder)

### Request/Response Models

All endpoints use Pydantic models for validation:
- `StoryCreationRequest` / `StoryCreationResult`
- `SprintSummaryRequest` / `SprintSummary`
- `ReleaseNotesRequest` / `ReleaseNotes`
- `EpicCategorizationRequest` / `EpicCategorization`

## GitLab Integration

### python-gitlab Library

The agent uses `python-gitlab==4.4.0` for GitLab API access:

```python
import gitlab

# Initialize client
gl = gitlab.Gitlab('https://gitlab.com', private_token='token')
gl.auth()

# Get project
project = gl.projects.get(project_id)

# Get milestone issues
issues = project.issues.list(milestone='Sprint 1', all=True)

# Get commits
commits = project.commits.list(ref_name='main', all=True)
```

### Required Token Scopes

Personal access token needs:
- `api` - Full API access
- `read_api` - Read-only API access
- `read_repository` - Read repository data

### Rate Limiting

GitLab API has rate limits:
- **Authenticated**: 300 requests per minute per user
- **Unauthenticated**: 10 requests per minute per IP

The agent uses `tenacity` for automatic retry with exponential backoff.

## AI Model Configuration

### Azure OpenAI GPT-4

```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_deployment="gpt-4",
    temperature=0.2,  # Low for consistency
    max_tokens=2000
)
```

### Temperature Settings

- **0.2** (default): Deterministic, consistent outputs
- **0.5-0.7**: More creative, varied phrasing
- **0.8-1.0**: Highly creative (not recommended for structured outputs)

### Prompt Engineering

The agent uses structured prompts for each use case:

**Story Creation:**
```
You are an expert Agile coach creating user stories.

Project: {project_name}
Requirement: {requirement}

Create a well-structured user story with:
1. Title (concise, action-oriented)
2. User story (As a... I want... So that...)
3. Acceptance criteria (Given/When/Then format, 3-5 criteria)
4. Story points estimate (Fibonacci: 1, 2, 3, 5, 8, 13)
5. Suggested labels

Return ONLY a JSON object: {...}
```

**Sprint Summary:**
```
Analyze this sprint and provide insights:

Sprint: {sprint_title}
Duration: {start_date} to {end_date}

Metrics:
- Completed: {completed}/{total} issues
- Velocity: {velocity} story points
- Completion rate: {rate}%

Incomplete issues: {incomplete}

Provide sprint summary with:
1. Overall assessment (Good/Fair/Needs Improvement)
2. Key achievements (2-3 bullet points)
3. Blockers and risks identified
4. Recommendations for next sprint

Return ONLY a JSON object: {...}
```

## Error Handling

### Exception Types

```python
try:
    result = agent.process(task_id, use_case, input_data)
except gitlab.exceptions.GitlabAuthenticationError:
    # GitLab token invalid or expired
except gitlab.exceptions.GitlabGetError:
    # Resource not found (project, milestone, etc.)
except openai.error.RateLimitError:
    # Azure OpenAI rate limit exceeded
except Exception as e:
    # Generic error
```

### Execution Trace

Every operation includes an execution trace for debugging:

```json
{
  "execution_trace": [
    {
      "step": 1,
      "node": "fetch_gitlab_data",
      "action": "Fetched GitLab data for story_creation",
      "timestamp": "2024-01-15T10:30:00",
      "duration_ms": 1250,
      "status": "success",
      "details": {"project_id": 123}
    }
  ]
}
```

## Performance Optimization

### Caching Strategy

Optional caching with configurable TTL:

```env
ENABLE_CACHE=true
CACHE_TTL_SECONDS=3600
```

Cache keys:
- `gitlab:project:{project_id}`
- `gitlab:milestones:{project_id}`
- `gitlab:issues:{project_id}:{filters_hash}`

### Query Optimization

1. **Limit results**: Use `all=True` sparingly
2. **Filter server-side**: Pass filters to GitLab API
3. **Pagination**: Handle large result sets properly
4. **Batch operations**: Use bulk endpoints

### Async Operations

FastAPI uses `async/await` for non-blocking I/O:

```python
@app.post("/api/stories/create")
async def create_user_story(request: StoryCreationRequest):
    # Non-blocking processing
    result = agent.process(...)
    return result
```

## Testing

### Unit Tests

```bash
pytest tests/test_agent.py -v
pytest tests/test_api.py -v
```

### Integration Tests

```bash
# Requires .env with real credentials
pytest tests/integration/ -v
```

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Create story
curl -X POST http://localhost:8000/api/stories/create \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Add password reset",
    "project_id": 123
  }'

# Sprint summary
curl -X POST http://localhost:8000/api/sprints/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 123,
    "milestone_id": 456
  }'
```

## Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "gitlab_interrogator_api.py"]
```

```bash
docker build -t gitlab-interrogator-backend .
docker run -p 8000:8000 --env-file .env gitlab-interrogator-backend
```

### Azure App Service

```bash
az webapp up \
  --name gitlab-interrogator-api \
  --runtime "PYTHON:3.10" \
  --sku B1

az webapp config appsettings set \
  --name gitlab-interrogator-api \
  --settings @.env
```

### Environment Variables

Set all required variables from `.env.example`:
- Azure OpenAI credentials
- GitLab token and URL
- API configuration
- Agile settings

## Monitoring

### Logs

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics

Track key metrics:
- Request count by endpoint
- Average processing time per use case
- Error rate
- GitLab API call count
- Azure OpenAI token usage

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent_status": "healthy" if agent else "unavailable",
        "gitlab_connection": check_gitlab_connection(),
        "timestamp": datetime.now().isoformat()
    }
```

## Development

### Adding New Use Cases

1. **Define state schema** in `GitLabInterrogatorState`
2. **Add node logic** for data fetching/processing
3. **Create prompt template** for AI generation
4. **Add API endpoint** with Pydantic models
5. **Update frontend** with new use case tab

### Extending GitLab Integration

```python
def _fetch_custom_data(self, project) -> Dict:
    """Fetch custom GitLab data"""
    # Add custom queries
    pipelines = project.pipelines.list(all=True)
    deployments = project.deployments.list(all=True)
    
    return {
        'pipelines': [self._format_pipeline(p) for p in pipelines],
        'deployments': [self._format_deployment(d) for d in deployments]
    }
```

## Troubleshooting

**Agent initialization fails:**
- Check Azure OpenAI credentials
- Verify all required environment variables are set
- Review startup logs for specific errors

**GitLab API errors:**
- Verify token is valid and not expired
- Check token has required scopes
- Ensure project ID exists and is accessible

**Slow response times:**
- Enable caching
- Limit query result sizes
- Check network latency to GitLab/Azure

---

For setup instructions, see [../SETUP_GUIDE.md](../SETUP_GUIDE.md)
