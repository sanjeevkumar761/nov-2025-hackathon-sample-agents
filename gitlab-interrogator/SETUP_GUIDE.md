# GitLab Interrogator - Setup Guide

Complete installation and configuration guide for the GitLab Interrogator AI agent.

## Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **GitLab Account** with project access
- **Azure OpenAI** API access (GPT-4)

## 1. Backend Setup

### Install Python Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Azure OpenAI (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# GitLab (Required)
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your-personal-access-token
GITLAB_PROJECT_ID=  # Optional default project

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:5173
```

### Create GitLab Personal Access Token

1. Go to GitLab → **Settings** → **Access Tokens**
2. Create a new token with these scopes:
   - `api` (Full API access)
   - `read_api` (Read-only API access)
   - `read_repository` (Read repository)
3. Copy the token to `GITLAB_TOKEN` in `.env`

### Start Backend Server

```bash
# Make sure virtual environment is activated
python gitlab_interrogator_api.py
```

Backend will be available at `http://localhost:8000`

**Test the backend:**
```bash
curl http://localhost:8000/health
```

## 2. Frontend Setup

### Install Node Dependencies

```bash
cd frontend
npm install
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Start Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 3. Verify Installation

### Health Check

1. Open `http://localhost:3000` in your browser
2. Check the status indicator in the header:
   - **Green checkmark**: System healthy
   - **Yellow warning**: Backend connected, GitLab not configured
   - **Red error**: Backend connection failed

### Test GitLab Integration

1. Click the **Project Selector** dropdown
2. If configured correctly, you should see your GitLab projects
3. Select a project to enable the use cases

### Test Each Use Case

**1. User Story Creation:**
- Select "User Stories" tab
- Enter a requirement like: "Users should be able to reset their password"
- Click "Generate User Story"
- Verify the AI generates a formatted story with acceptance criteria

**2. Sprint Summarization:**
- Select "Sprint Summary" tab
- Choose a milestone/sprint
- Click "Analyze Sprint"
- Verify velocity and metrics are calculated

**3. Release Notes:**
- Select "Release Notes" tab
- Enter a version tag (e.g., "v1.0.0")
- Click "Generate Release Notes"
- Verify formatted release notes appear

**4. Epic Categorization:**
- Select "Epic Categorization" tab
- Click "Categorize Epics"
- Verify epics are grouped by theme

## 4. Troubleshooting

### Backend Won't Start

**Error: "No module named 'gitlab'"**
```bash
pip install python-gitlab==4.4.0
```

**Error: "Azure OpenAI authentication failed"**
- Verify `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` are correct
- Check that your Azure OpenAI resource is deployed

**Error: "GitLab authentication failed"**
- Verify `GITLAB_TOKEN` is valid
- Check token has correct scopes (api, read_api, read_repository)

### Frontend Won't Start

**Error: "Cannot find module 'next'"**
```bash
npm install
```

**Error: "CORS policy blocked"**
- Check `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`
- Restart backend server after changing CORS settings

### No Projects in Dropdown

**Issue: GitLab connection warning shown**
1. Verify `GITLAB_TOKEN` is set in backend `.env`
2. Restart backend server
3. Check browser console for errors

**Issue: Empty project list**
- Verify your GitLab account has access to projects
- Try using `GITLAB_URL=https://gitlab.com` (public GitLab)

### API Returns Errors

**"Agent not initialized"**
- Backend failed to start properly
- Check backend logs for initialization errors
- Verify all required environment variables are set

**"GitLab client not available"**
- GitLab token not configured
- Check `GITLAB_TOKEN` in `.env`

## 5. Production Deployment

### Backend (Example: Azure App Service)

1. **Create App Service** with Python 3.10+ runtime
2. **Set environment variables** in Configuration
3. **Deploy code**:
   ```bash
   az webapp up --name gitlab-interrogator-api --runtime "PYTHON:3.10"
   ```
4. **Update CORS** to include frontend URL

### Frontend (Example: Vercel)

1. **Connect GitHub repository** to Vercel
2. **Set environment variable**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.azurewebsites.net
   ```
3. **Deploy**:
   ```bash
   npm run build
   vercel deploy --prod
   ```

### Security Considerations

- **Never commit `.env` files** to version control
- **Use secrets management** (Azure Key Vault, AWS Secrets Manager)
- **Enable HTTPS** in production
- **Restrict CORS** to your frontend domain only
- **Rotate tokens** regularly

## 6. Usage Tips

### Story Points

The agent uses Fibonacci sequence (1, 2, 3, 5, 8, 13, 21) for story points. You can customize this in backend `.env`:

```env
DEFAULT_STORY_POINTS_SCALE=1,2,3,5,8,13,21
MAX_STORY_POINTS_PER_STORY=13
```

### Sprint Duration

Default sprint duration is 14 days. Change in `.env`:

```env
DEFAULT_SPRINT_DURATION=14
```

### AI Temperature

Control AI creativity (0.0 = deterministic, 1.0 = creative):

```env
AI_TEMPERATURE=0.2
```

### Commit Message Format

For best release notes, use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `break:` or `BREAKING CHANGE:` for breaking changes

Example:
```
feat: add password reset functionality
fix: resolve CORS issue on login endpoint
```

## 7. Next Steps

- **Integrate with CI/CD**: Automate release notes generation
- **Webhook Integration**: Auto-generate stories from issue creation
- **Custom Categories**: Define your own epic taxonomy
- **Historical Analytics**: Track velocity trends over time

## Support

For issues or questions:
- Check backend logs: `tail -f logs/app.log`
- Check frontend console: Open browser DevTools
- Review API documentation: `http://localhost:8000/docs`

---

**Congratulations!** Your GitLab Interrogator is now set up and ready to automate your Agile workflows.
