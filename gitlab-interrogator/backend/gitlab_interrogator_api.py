"""
GitLab Interrogator FastAPI Server

REST API for AI-powered GitLab Agile workflow automation.

Endpoints:
- Story Creation: POST /api/stories/create, POST /api/stories/bulk
- Sprint Summary: POST /api/sprints/summarize, GET /api/sprints/{id}/velocity
- Release Notes: POST /api/releases/generate, POST /api/releases/publish
- Epic Categorization: POST /api/epics/categorize, POST /api/epics/roadmap
- GitLab Integration: GET /api/gitlab/projects, GET /api/gitlab/milestones
- System: GET /health, GET /workflow/graph
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import gitlab

from gitlab_interrogator_agent import GitLabInterrogatorAgent, create_agent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global agent instance
agent: Optional[GitLabInterrogatorAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the FastAPI app"""
    global agent
    
    logger.info("🚀 Starting GitLab Interrogator API...")
    
    # Initialize agent
    agent = create_agent()
    if not agent:
        logger.error("Failed to initialize GitLab Interrogator Agent")
    else:
        logger.info("✓ GitLab Interrogator Agent initialized successfully")
    
    yield
    
    logger.info("👋 Shutting down GitLab Interrogator API...")


# Create FastAPI app
app = FastAPI(
    title="GitLab Interrogator API",
    description="AI-powered Scrum Master Digital Employee for GitLab workflow automation",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class StoryCreationRequest(BaseModel):
    """Request to create user story from requirements"""
    requirement: str = Field(..., description="Requirements text to convert into user story")
    project_id: int = Field(..., description="GitLab project ID")
    context: Optional[str] = Field(None, description="Additional project context")


class StoryCreationResult(BaseModel):
    """Result of user story creation"""
    task_id: str
    title: str
    description: str
    labels: List[str]
    story_points: int
    gitlab_payload: Dict[str, Any]
    execution_trace: List[Dict[str, Any]]


class BulkStoryRequest(BaseModel):
    """Request to create multiple user stories"""
    requirements: List[str] = Field(..., description="List of requirements to convert")
    project_id: int
    context: Optional[str] = None


class SprintSummaryRequest(BaseModel):
    """Request to summarize sprint"""
    project_id: int
    milestone_id: int = Field(..., description="GitLab milestone ID representing the sprint")


class SprintSummary(BaseModel):
    """Sprint summary result"""
    task_id: str
    milestone_title: str
    assessment: str
    metrics: Dict[str, Any]
    achievements: List[str]
    blockers: List[str]
    recommendations: List[str]
    report_markdown: str
    execution_trace: List[Dict[str, Any]]


class ReleaseNotesRequest(BaseModel):
    """Request to generate release notes"""
    project_id: int
    tag_name: str = Field(..., description="Version/tag name for this release")
    from_tag: Optional[str] = Field(None, description="Previous release tag (for comparison)")
    to_tag: Optional[str] = Field("HEAD", description="Current release reference")
    since: Optional[str] = Field(None, description="ISO date to fetch changes since")


class ReleaseNotes(BaseModel):
    """Release notes result"""
    task_id: str
    version: str
    date: str
    summary: str
    features: List[str]
    fixes: List[str]
    breaking_changes: List[str]
    contributors: List[str]
    markdown: str
    execution_trace: List[Dict[str, Any]]


class EpicCategorizationRequest(BaseModel):
    """Request to categorize epics"""
    project_id: int
    categories: Optional[List[str]] = Field(
        None,
        description="Existing category taxonomy (will use defaults if not provided)"
    )


class EpicCategorization(BaseModel):
    """Epic categorization result"""
    task_id: str
    categorized: Dict[str, List[Dict[str, Any]]]
    taxonomy: List[str]
    new_category_suggestions: List[str]
    markdown: str
    execution_trace: List[Dict[str, Any]]


class GitLabProject(BaseModel):
    """GitLab project info"""
    id: int
    name: str
    description: Optional[str]
    web_url: str
    path_with_namespace: str


class GitLabMilestone(BaseModel):
    """GitLab milestone info"""
    id: int
    iid: int
    title: str
    description: Optional[str]
    state: str
    start_date: Optional[str]
    due_date: Optional[str]
    web_url: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    agent_status: str
    gitlab_connection: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str]
    timestamp: str


# ============================================================================
# STORY CREATION ENDPOINTS
# ============================================================================


@app.post("/api/stories/create", response_model=StoryCreationResult)
async def create_user_story(request: StoryCreationRequest):
    """
    Create a user story from requirements text.
    
    This endpoint uses AI to:
    1. Parse requirements into user story format (As a... I want... So that...)
    2. Generate acceptance criteria (Given/When/Then)
    3. Estimate story points (Fibonacci scale)
    4. Suggest appropriate labels
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        task_id = str(uuid.uuid4())
        
        input_data = {
            'requirement': request.requirement,
            'project_id': request.project_id,
            'context': request.context
        }
        
        logger.info(f"Creating user story for task {task_id}")
        result = agent.process(task_id, 'story_creation', input_data)
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        artifacts = result.get('artifacts', {})
        
        return StoryCreationResult(
            task_id=task_id,
            title=artifacts.get('title', ''),
            description=artifacts.get('description', ''),
            labels=artifacts.get('labels', []),
            story_points=artifacts.get('story_points', 0),
            gitlab_payload=artifacts.get('gitlab_payload', {}),
            execution_trace=result.get('execution_trace', [])
        )
        
    except Exception as e:
        logger.error(f"Story creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stories/bulk")
async def create_bulk_stories(request: BulkStoryRequest):
    """
    Create multiple user stories from a list of requirements.
    
    Processes each requirement independently and returns an array of results.
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        results = []
        
        for requirement in request.requirements:
            task_id = str(uuid.uuid4())
            
            input_data = {
                'requirement': requirement,
                'project_id': request.project_id,
                'context': request.context
            }
            
            result = agent.process(task_id, 'story_creation', input_data)
            
            if not result.get('error'):
                artifacts = result.get('artifacts', {})
                results.append({
                    'task_id': task_id,
                    'requirement': requirement,
                    'title': artifacts.get('title', ''),
                    'story_points': artifacts.get('story_points', 0),
                    'status': 'success'
                })
            else:
                results.append({
                    'task_id': task_id,
                    'requirement': requirement,
                    'status': 'failed',
                    'error': result['error']
                })
        
        return {
            'total': len(request.requirements),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'failed']),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Bulk story creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stories/to-gitlab")
async def create_gitlab_issue(
    task_id: str,
    project_id: int,
    background_tasks: BackgroundTasks
):
    """
    Create a GitLab issue from a generated user story.
    
    Use the task_id from a previous story creation request to create
    an actual issue in GitLab.
    """
    # This would typically retrieve the story from a cache/database
    # and create the GitLab issue using the python-gitlab library
    
    raise HTTPException(
        status_code=501,
        detail="GitLab issue creation not yet implemented. Use the gitlab_payload from /api/stories/create."
    )


# ============================================================================
# SPRINT SUMMARY ENDPOINTS
# ============================================================================


@app.post("/api/sprints/summarize", response_model=SprintSummary)
async def summarize_sprint(request: SprintSummaryRequest):
    """
    Generate comprehensive sprint summary with AI insights.
    
    Analyzes:
    - Velocity and completion rate
    - Completed vs incomplete issues
    - Blockers and risks
    - Team contributions
    - Recommendations for next sprint
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        task_id = str(uuid.uuid4())
        
        input_data = {
            'project_id': request.project_id,
            'milestone_id': request.milestone_id
        }
        
        logger.info(f"Summarizing sprint for task {task_id}")
        result = agent.process(task_id, 'sprint_summary', input_data)
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        insights = result.get('insights', {})
        artifacts = result.get('artifacts', {})
        gitlab_data = result.get('gitlab_data', {})
        
        milestone = gitlab_data.get('milestone', {})
        
        return SprintSummary(
            task_id=task_id,
            milestone_title=milestone.get('title', 'Unknown'),
            assessment=insights.get('assessment', 'Unknown'),
            metrics=insights.get('metrics', {}),
            achievements=insights.get('achievements', []),
            blockers=insights.get('blockers', []),
            recommendations=insights.get('recommendations', []),
            report_markdown=artifacts.get('markdown', ''),
            execution_trace=result.get('execution_trace', [])
        )
        
    except Exception as e:
        logger.error(f"Sprint summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sprints/{milestone_id}/velocity")
async def get_sprint_velocity(milestone_id: int, project_id: int):
    """
    Get historical velocity for a project's sprints.
    
    Returns velocity chart data for the last N sprints.
    """
    if not agent or not agent.gl:
        raise HTTPException(status_code=503, detail="GitLab client not available")
    
    try:
        project = agent.gl.projects.get(project_id)
        milestones = project.milestones.list(all=True)
        
        velocity_data = []
        
        for milestone in milestones[:10]:  # Last 10 sprints
            issues = project.issues.list(milestone=milestone.title, all=True)
            
            # Calculate velocity
            completed_points = 0
            for issue in issues:
                if issue.state == 'closed':
                    # Look for story point labels
                    for label in issue.labels:
                        if label.startswith('sp:'):
                            completed_points += int(label.split(':')[1])
                            break
            
            velocity_data.append({
                'sprint': milestone.title,
                'velocity': completed_points,
                'due_date': milestone.due_date
            })
        
        return {
            'project_id': project_id,
            'velocity_history': velocity_data
        }
        
    except Exception as e:
        logger.error(f"Velocity calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sprints/{milestone_id}/burndown")
async def get_burndown_data(milestone_id: int, project_id: int):
    """
    Get burndown chart data for a sprint.
    
    Returns daily remaining story points throughout the sprint.
    """
    # This would require historical data tracking
    # For now, return a placeholder
    
    raise HTTPException(
        status_code=501,
        detail="Burndown chart requires historical tracking. Consider using GitLab's built-in burndown charts."
    )


# ============================================================================
# RELEASE NOTES ENDPOINTS
# ============================================================================


@app.post("/api/releases/generate", response_model=ReleaseNotes)
async def generate_release_notes(request: ReleaseNotesRequest):
    """
    Generate professional release notes from commits and issues.
    
    Automatically:
    - Categorizes changes (Features, Fixes, Breaking Changes)
    - Extracts issue references
    - Formats in Keep a Changelog style
    - Lists contributors
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        task_id = str(uuid.uuid4())
        
        input_data = {
            'project_id': request.project_id,
            'tag_name': request.tag_name,
            'from_tag': request.from_tag,
            'to_tag': request.to_tag,
            'since': request.since
        }
        
        logger.info(f"Generating release notes for task {task_id}")
        result = agent.process(task_id, 'release_notes', input_data)
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        insights = result.get('insights', {})
        artifacts = result.get('artifacts', {})
        
        return ReleaseNotes(
            task_id=task_id,
            version=artifacts.get('version', request.tag_name),
            date=artifacts.get('date', datetime.now().strftime('%Y-%m-%d')),
            summary=insights.get('summary', ''),
            features=insights.get('features', []),
            fixes=insights.get('fixes', []),
            breaking_changes=insights.get('breaking_changes', []),
            contributors=insights.get('contributors', []),
            markdown=artifacts.get('markdown', ''),
            execution_trace=result.get('execution_trace', [])
        )
        
    except Exception as e:
        logger.error(f"Release notes generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/releases/publish")
async def publish_release_notes(
    task_id: str,
    project_id: int,
    tag_name: str
):
    """
    Publish generated release notes to GitLab as a release.
    
    Creates a GitLab Release object with the generated notes.
    """
    # This would retrieve the release notes and publish to GitLab
    
    raise HTTPException(
        status_code=501,
        detail="GitLab release publishing not yet implemented. Use the markdown from /api/releases/generate."
    )


@app.get("/api/releases/{tag_name}/changelog")
async def get_changelog(tag_name: str, project_id: int):
    """
    Get existing changelog for a release tag.
    
    Retrieves the release notes from GitLab if they exist.
    """
    if not agent or not agent.gl:
        raise HTTPException(status_code=503, detail="GitLab client not available")
    
    try:
        project = agent.gl.projects.get(project_id)
        
        # Try to get the release
        try:
            release = project.releases.get(tag_name)
            return {
                'tag_name': release.tag_name,
                'description': release.description,
                'created_at': release.created_at,
                'released_at': release.released_at
            }
        except:
            raise HTTPException(status_code=404, detail=f"Release {tag_name} not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Changelog retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EPIC CATEGORIZATION ENDPOINTS
# ============================================================================


@app.post("/api/epics/categorize", response_model=EpicCategorization)
async def categorize_epics(request: EpicCategorizationRequest):
    """
    Categorize epics using semantic AI analysis.
    
    Groups epics by themes:
    - Infrastructure, Features, UX/UI, Technical Debt, etc.
    - Suggests new categories based on patterns
    - Provides confidence scores
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        task_id = str(uuid.uuid4())
        
        input_data = {
            'project_id': request.project_id,
            'categories': request.categories
        }
        
        logger.info(f"Categorizing epics for task {task_id}")
        result = agent.process(task_id, 'epic_categorization', input_data)
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        insights = result.get('insights', {})
        artifacts = result.get('artifacts', {})
        
        return EpicCategorization(
            task_id=task_id,
            categorized=insights.get('categorized', {}),
            taxonomy=artifacts.get('taxonomy', []),
            new_category_suggestions=insights.get('new_category_suggestions', []),
            markdown=artifacts.get('markdown', ''),
            execution_trace=result.get('execution_trace', [])
        )
        
    except Exception as e:
        logger.error(f"Epic categorization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/epics/roadmap")
async def generate_epic_roadmap(project_id: int):
    """
    Generate visual roadmap from categorized epics.
    
    Creates timeline data for roadmap visualization.
    """
    # This would generate roadmap visualization data
    
    raise HTTPException(
        status_code=501,
        detail="Roadmap generation coming soon. Use /api/epics/categorize for categorization."
    )


@app.get("/api/epics/taxonomy")
async def get_epic_taxonomy(project_id: int):
    """
    Get the current epic taxonomy/category structure.
    
    Returns existing categories and their usage frequency.
    """
    if not agent or not agent.gl:
        raise HTTPException(status_code=503, detail="GitLab client not available")
    
    try:
        project = agent.gl.projects.get(project_id)
        labels = project.labels.list(all=True)
        
        # Extract category-like labels
        categories = {}
        for label in labels:
            # Look for category patterns (e.g., "category:infrastructure")
            if label.name.startswith('category:'):
                category = label.name.split(':', 1)[1]
                categories[category] = {
                    'name': category,
                    'label': label.name,
                    'color': label.color if hasattr(label, 'color') else None
                }
        
        return {
            'project_id': project_id,
            'categories': list(categories.values()),
            'total': len(categories)
        }
        
    except Exception as e:
        logger.error(f"Taxonomy retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GITLAB INTEGRATION ENDPOINTS
# ============================================================================


@app.get("/api/gitlab/projects", response_model=List[GitLabProject])
async def list_projects(visibility: Optional[str] = None):
    """
    List accessible GitLab projects.
    
    Args:
        visibility: Filter by visibility (public, internal, private)
    """
    if not agent or not agent.gl:
        raise HTTPException(status_code=503, detail="GitLab client not available")
    
    try:
        params = {}
        if visibility:
            params['visibility'] = visibility
        
        projects = agent.gl.projects.list(all=True, **params)
        
        return [
            GitLabProject(
                id=p.id,
                name=p.name,
                description=p.description,
                web_url=p.web_url,
                path_with_namespace=p.path_with_namespace
            )
            for p in projects[:50]  # Limit to 50
        ]
        
    except Exception as e:
        logger.error(f"Project listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gitlab/milestones", response_model=List[GitLabMilestone])
async def list_milestones(project_id: int, state: Optional[str] = None):
    """
    List milestones for a project.
    
    Args:
        project_id: GitLab project ID
        state: Filter by state (active, closed)
    """
    if not agent or not agent.gl:
        raise HTTPException(status_code=503, detail="GitLab client not available")
    
    try:
        project = agent.gl.projects.get(project_id)
        
        params = {}
        if state:
            params['state'] = state
        
        milestones = project.milestones.list(all=True, **params)
        
        return [
            GitLabMilestone(
                id=m.id,
                iid=m.iid,
                title=m.title,
                description=m.description,
                state=m.state,
                start_date=m.start_date if hasattr(m, 'start_date') else None,
                due_date=m.due_date if hasattr(m, 'due_date') else None,
                web_url=m.web_url
            )
            for m in milestones
        ]
        
    except Exception as e:
        logger.error(f"Milestone listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gitlab/issues")
async def list_issues(
    project_id: int,
    state: Optional[str] = None,
    labels: Optional[str] = None,
    milestone: Optional[str] = None,
    limit: int = 50
):
    """
    List issues for a project with filters.
    """
    if not agent or not agent.gl:
        raise HTTPException(status_code=503, detail="GitLab client not available")
    
    try:
        project = agent.gl.projects.get(project_id)
        
        params = {}
        if state:
            params['state'] = state
        if labels:
            params['labels'] = labels
        if milestone:
            params['milestone'] = milestone
        
        issues = project.issues.list(**params)
        
        return {
            'project_id': project_id,
            'issues': [
                {
                    'id': i.id,
                    'iid': i.iid,
                    'title': i.title,
                    'state': i.state,
                    'labels': i.labels,
                    'web_url': i.web_url
                }
                for i in issues[:limit]
            ],
            'total': len(issues)
        }
        
    except Exception as e:
        logger.error(f"Issue listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    agent_status = "healthy" if agent else "unavailable"
    
    gitlab_status = "disconnected"
    if agent and agent.gl:
        try:
            agent.gl.projects.list(per_page=1)
            gitlab_status = "connected"
        except:
            gitlab_status = "authentication_failed"
    
    return HealthResponse(
        status="healthy" if agent else "degraded",
        agent_status=agent_status,
        gitlab_connection=gitlab_status,
        timestamp=datetime.now().isoformat()
    )


@app.get("/workflow/graph")
async def get_workflow_graph():
    """Get workflow structure for visualization"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return agent.get_workflow_graph()


@app.get("/stats")
async def get_usage_stats():
    """Get API usage statistics"""
    # This would retrieve metrics from a database or cache
    
    return {
        "message": "Usage statistics not yet implemented",
        "endpoints": {
            "story_creation": "/api/stories/create",
            "sprint_summary": "/api/sprints/summarize",
            "release_notes": "/api/releases/generate",
            "epic_categorization": "/api/epics/categorize"
        }
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Not Found",
            detail=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred. Check server logs.",
            timestamp=datetime.now().isoformat()
        ).dict()
    )


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"Starting GitLab Interrogator API on {host}:{port}")
    
    uvicorn.run(
        "gitlab_interrogator_api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
