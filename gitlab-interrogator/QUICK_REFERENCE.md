# GitLab Interrogator - Quick Reference

Fast reference for common tasks and API endpoints.

## Quick Commands

### Backend

```bash
# Start backend
cd backend
python gitlab_interrogator_api.py

# Test health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

### Frontend

```bash
# Start frontend
cd frontend
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## API Endpoints

### User Story Creation

**Create Single Story**
```bash
POST /api/stories/create
{
  "requirement": "Users should be able to reset their password",
  "project_id": 123,
  "context": "Authentication module"
}
```

**Create Bulk Stories**
```bash
POST /api/stories/bulk
{
  "requirements": ["Requirement 1", "Requirement 2"],
  "project_id": 123
}
```

### Sprint Summary

**Summarize Sprint**
```bash
POST /api/sprints/summarize
{
  "project_id": 123,
  "milestone_id": 456
}
```

**Get Velocity History**
```bash
GET /api/sprints/456/velocity?project_id=123
```

### Release Notes

**Generate Release Notes**
```bash
POST /api/releases/generate
{
  "project_id": 123,
  "tag_name": "v1.2.0",
  "since": "2024-01-01"
}
```

**Get Existing Changelog**
```bash
GET /api/releases/v1.2.0/changelog?project_id=123
```

### Epic Categorization

**Categorize Epics**
```bash
POST /api/epics/categorize
{
  "project_id": 123,
  "categories": ["Infrastructure", "Features", "Technical Debt"]
}
```

**Get Taxonomy**
```bash
GET /api/epics/taxonomy?project_id=123
```

### GitLab Integration

**List Projects**
```bash
GET /api/gitlab/projects
GET /api/gitlab/projects?visibility=public
```

**List Milestones**
```bash
GET /api/gitlab/milestones?project_id=123
GET /api/gitlab/milestones?project_id=123&state=active
```

**List Issues**
```bash
GET /api/gitlab/issues?project_id=123&state=opened&limit=50
```

### System

**Health Check**
```bash
GET /health
```

**Workflow Graph**
```bash
GET /workflow/graph
```

## Environment Variables

### Backend (.env)

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# GitLab
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_PROJECT_ID=123

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Agile Settings
DEFAULT_STORY_POINTS_SCALE=1,2,3,5,8,13,21
DEFAULT_SPRINT_DURATION=14
MAX_STORY_POINTS_PER_STORY=13

# AI Behavior
AI_TEMPERATURE=0.2
MAX_TOKENS=2000
```

### Frontend (.env)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_GITLAB_INTEGRATION=true
```

## Common Issues & Solutions

### "GitLab authentication failed"

**Solution:**
1. Create personal access token: GitLab → Settings → Access Tokens
2. Scopes: `api`, `read_api`, `read_repository`
3. Copy token to `GITLAB_TOKEN` in backend `.env`
4. Restart backend

### "CORS policy blocked"

**Solution:**
1. Add frontend URL to `CORS_ORIGINS` in backend `.env`
2. Restart backend server

### "Agent not initialized"

**Solution:**
1. Check Azure OpenAI credentials
2. Verify all required environment variables are set
3. Review backend startup logs

### Empty project list

**Solution:**
1. Verify GitLab token has project access
2. Check token scopes include `api` and `read_api`
3. Try accessing GitLab API manually:
   ```bash
   curl --header "PRIVATE-TOKEN: your-token" \
        "https://gitlab.com/api/v4/projects"
   ```

## Python Code Examples

### Direct Agent Usage

```python
from gitlab_interrogator_agent import create_agent

# Initialize agent
agent = create_agent()

# Create user story
result = agent.process(
    task_id="task-001",
    use_case="story_creation",
    input_data={
        "requirement": "Users should be able to reset password",
        "project_id": 123
    }
)

print(result['artifacts']['title'])
print(result['artifacts']['story_points'])
```

### Custom GitLab Queries

```python
import gitlab

gl = gitlab.Gitlab('https://gitlab.com', private_token='your-token')
gl.auth()

# Get project
project = gl.projects.get(123)

# Get issues
issues = project.issues.list(state='opened', labels=['bug'])

# Get milestone
milestone = project.milestones.get(456)
milestone_issues = project.issues.list(milestone=milestone.title)
```

## JavaScript/TypeScript Examples

### API Client Usage

```typescript
import { api } from '@/lib/api';

// Create user story
const result = await api.createUserStory({
  requirement: "Add email notifications",
  project_id: 123,
  context: "Notification system"
});

console.log(result.title);
console.log(result.story_points);

// Summarize sprint
const summary = await api.summarizeSprint({
  project_id: 123,
  milestone_id: 456
});

console.log(summary.assessment); // 'Good' | 'Fair' | 'Needs Improvement'
console.log(summary.metrics.velocity);
```

### React Query Integration

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';

// Fetch projects
const { data: projects } = useQuery({
  queryKey: ['projects'],
  queryFn: () => api.listProjects()
});

// Create story
const createStory = useMutation({
  mutationFn: api.createUserStory,
  onSuccess: (data) => {
    console.log('Story created:', data.title);
  }
});

createStory.mutate({
  requirement: "Add dark mode",
  project_id: 123
});
```

## Workflow Nodes

The agent uses a 5-node LangGraph workflow:

1. **fetch_gitlab_data** - Retrieve project data from GitLab API
2. **analyze_agile_metrics** - Calculate velocity, completion rates
3. **generate_insights** - Use GPT-4 for semantic analysis
4. **create_artifacts** - Format stories, reports, release notes
5. **compile_report** - Assemble final output

## Story Point Estimation Guide

The AI uses this heuristic:

| Points | Complexity | Time Estimate |
|--------|------------|---------------|
| 1      | Trivial    | < 2 hours     |
| 2      | Simple     | 2-4 hours     |
| 3      | Moderate   | 4-8 hours     |
| 5      | Complex    | 1-2 days      |
| 8      | Very Complex | 2-3 days    |
| 13     | Epic-level | 3-5 days      |
| 21     | Too large  | Split needed  |

## Conventional Commit Format

For best release notes generation:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructure
- `test:` Tests
- `chore:` Maintenance

**Example:**
```
feat: add password reset endpoint

Implements email-based password reset with secure tokens
that expire after 1 hour.

Closes #123
```

## Performance Tips

1. **Limit issue queries** to recent items (last 100)
2. **Use caching** for repeated queries
3. **Batch story creation** with `/api/stories/bulk`
4. **Filter by milestone** for sprint analysis
5. **Use date ranges** for release notes

## Security Best Practices

- ✅ Never commit `.env` files
- ✅ Use environment variables for secrets
- ✅ Rotate GitLab tokens every 90 days
- ✅ Restrict CORS to specific domains in production
- ✅ Enable HTTPS for API endpoints
- ✅ Use read-only tokens where possible

## Useful GitLab API Commands

```bash
# List projects
curl --header "PRIVATE-TOKEN: your-token" \
     "https://gitlab.com/api/v4/projects"

# Get project details
curl --header "PRIVATE-TOKEN: your-token" \
     "https://gitlab.com/api/v4/projects/123"

# List milestones
curl --header "PRIVATE-TOKEN: your-token" \
     "https://gitlab.com/api/v4/projects/123/milestones"

# List issues
curl --header "PRIVATE-TOKEN: your-token" \
     "https://gitlab.com/api/v4/projects/123/issues?state=opened"

# Get commits
curl --header "PRIVATE-TOKEN: your-token" \
     "https://gitlab.com/api/v4/projects/123/repository/commits"
```

---

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)
