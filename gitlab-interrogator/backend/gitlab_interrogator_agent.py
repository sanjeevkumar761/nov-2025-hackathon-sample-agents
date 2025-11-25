"""
GitLab Interrogator Agent

AI-powered Scrum Master Digital Employee for GitLab workflow automation.

Workflow:
1. fetch_gitlab_data - Retrieve project data from GitLab API
2. analyze_agile_metrics - Calculate sprint velocity, completion rates
3. generate_insights - Use GPT-4 for semantic analysis
4. create_artifacts - Format stories, reports, release notes
5. compile_report - Assemble final output
"""

import os
import json
import logging
import time
from typing import TypedDict, Dict, List, Optional, Any, Literal
from datetime import datetime, timedelta
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END
import gitlab

# Load environment variables
load_dotenv()


class GitLabInterrogatorState(TypedDict):
    """State schema for GitLab interrogation workflow"""
    # Input
    task_id: str
    use_case: Literal['story_creation', 'sprint_summary', 'release_notes', 'epic_categorization']
    input_data: Dict[str, Any]
    
    # GitLab configuration
    gitlab_url: str
    gitlab_token: str
    project_id: Optional[int]
    
    # Fetched data
    gitlab_data: Optional[Dict[str, Any]]
    
    # Analysis results
    metrics: Optional[Dict[str, Any]]
    insights: Optional[Dict[str, Any]]
    
    # Generated artifacts
    artifacts: Optional[Dict[str, Any]]
    
    # Final output
    report: Optional[str]
    
    # Metadata
    execution_trace: List[Dict[str, Any]]
    processing_status: str
    error: Optional[str]


class GitLabInterrogatorAgent:
    """
    AI agent for automating GitLab Agile workflows.
    
    Supports 4 use cases:
    1. User Story / Epic Creation
    2. Sprint Summarization
    3. Release Notes Generation
    4. Epic Categorization
    """
    
    def __init__(self):
        """Initialize the GitLab interrogator agent"""
        # Set up logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize Azure OpenAI
        self.logger.info("Initializing Azure OpenAI client...")
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.2")),
            max_tokens=int(os.getenv("MAX_TOKENS", "2000"))
        )
        
        # GitLab configuration
        self.gitlab_url = os.getenv("GITLAB_URL", "https://gitlab.com")
        self.gitlab_token = os.getenv("GITLAB_TOKEN")
        
        # Initialize GitLab client
        if self.gitlab_token:
            self.logger.info(f"Initializing GitLab client for {self.gitlab_url}...")
            self.gl = gitlab.Gitlab(self.gitlab_url, private_token=self.gitlab_token)
            try:
                self.gl.auth()
                self.logger.info("✓ GitLab authentication successful")
            except Exception as e:
                self.logger.warning(f"GitLab authentication failed: {e}")
                self.gl = None
        else:
            self.logger.warning("No GitLab token provided - GitLab features disabled")
            self.gl = None
        
        # Build the workflow
        self.logger.info("Building LangGraph workflow...")
        self.workflow = self._build_workflow()
        self.logger.info("✓ GitLab Interrogator Agent initialized successfully")
    
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(GitLabInterrogatorState)
        
        # Add nodes
        workflow.add_node("fetch_gitlab_data", self._fetch_gitlab_data)
        workflow.add_node("analyze_agile_metrics", self._analyze_agile_metrics)
        workflow.add_node("generate_insights", self._generate_insights)
        workflow.add_node("create_artifacts", self._create_artifacts)
        workflow.add_node("compile_report", self._compile_report)
        
        # Define edges
        workflow.set_entry_point("fetch_gitlab_data")
        workflow.add_edge("fetch_gitlab_data", "analyze_agile_metrics")
        workflow.add_edge("analyze_agile_metrics", "generate_insights")
        workflow.add_edge("generate_insights", "create_artifacts")
        workflow.add_edge("create_artifacts", "compile_report")
        workflow.add_edge("compile_report", END)
        
        return workflow.compile()
    
    def _add_trace_step(self, state: GitLabInterrogatorState, node: str,
                       action: str, details: Dict = None, duration_ms: int = 0):
        """Add execution trace step"""
        state['execution_trace'].append({
            'step': len(state['execution_trace']) + 1,
            'node': node,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'duration_ms': duration_ms,
            'status': 'success',
            'details': details or {}
        })
    
    def _fetch_gitlab_data(self, state: GitLabInterrogatorState) -> GitLabInterrogatorState:
        """
        Node 1: Fetch data from GitLab API
        """
        start_time = time.time()
        self.logger.info(f"Node: Fetching GitLab data for {state['use_case']}...")
        
        try:
            if not self.gl:
                raise Exception("GitLab client not initialized")
            
            use_case = state['use_case']
            input_data = state['input_data']
            project_id = input_data.get('project_id') or state.get('project_id')
            
            if not project_id:
                raise Exception("No project_id provided")
            
            # Get project
            project = self.gl.projects.get(project_id)
            
            gitlab_data = {
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'web_url': project.web_url
                }
            }
            
            # Fetch data based on use case
            if use_case == 'story_creation':
                # For story creation, just need project context
                gitlab_data['epics'] = self._fetch_epics(project)
                gitlab_data['labels'] = [label.name for label in project.labels.list()]
            
            elif use_case == 'sprint_summary':
                # Fetch sprint/milestone data
                milestone_id = input_data.get('milestone_id')
                if milestone_id:
                    milestone = project.milestones.get(milestone_id)
                    gitlab_data['milestone'] = {
                        'id': milestone.id,
                        'title': milestone.title,
                        'start_date': milestone.start_date,
                        'due_date': milestone.due_date,
                        'state': milestone.state
                    }
                    
                    # Fetch issues in milestone
                    issues = project.issues.list(milestone=milestone.title, all=True)
                    gitlab_data['issues'] = [self._format_issue(issue) for issue in issues]
                    
                    # Fetch merge requests
                    mrs = project.mergerequests.list(milestone=milestone.title, all=True)
                    gitlab_data['merge_requests'] = [self._format_mr(mr) for mr in mrs]
            
            elif use_case == 'release_notes':
                # Fetch commits and issues for release
                from_tag = input_data.get('from_tag')
                to_tag = input_data.get('to_tag', 'HEAD')
                
                # Get commits
                commits = project.commits.list(ref_name=to_tag, all=True)
                gitlab_data['commits'] = [self._format_commit(commit) for commit in commits[:100]]
                
                # Get closed issues
                since = input_data.get('since')
                issues = project.issues.list(state='closed', updated_after=since, all=True)
                gitlab_data['closed_issues'] = [self._format_issue(issue) for issue in issues]
                
                # Get merged MRs
                mrs = project.mergerequests.list(state='merged', updated_after=since, all=True)
                gitlab_data['merged_mrs'] = [self._format_mr(mr) for mr in mrs]
            
            elif use_case == 'epic_categorization':
                # Fetch all epics
                gitlab_data['epics'] = self._fetch_epics(project)
                gitlab_data['labels'] = [label.name for label in project.labels.list()]
                
                # Fetch existing categories from input
                gitlab_data['categories'] = input_data.get('categories', [
                    'Infrastructure', 'Features', 'UX/UI', 'Technical Debt',
                    'Performance', 'Security', 'Documentation'
                ])
            
            state['gitlab_data'] = gitlab_data
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='fetch_gitlab_data',
                action=f'Fetched GitLab data for {use_case}',
                details={'project_id': project_id},
                duration_ms=duration
            )
            
            self.logger.info(f"✓ GitLab data fetched successfully")
            
        except Exception as e:
            self.logger.error(f"✗ GitLab data fetch failed: {e}")
            state['error'] = str(e)
            state['gitlab_data'] = {}
        
        return state
    
    def _fetch_epics(self, project) -> List[Dict]:
        """Fetch epics (or use issues with epic label as fallback)"""
        try:
            # GitLab EE has epics, CE uses issues with epic label
            if hasattr(project, 'epics'):
                epics = project.epics.list(all=True)
                return [{
                    'id': epic.id,
                    'title': epic.title,
                    'description': epic.description,
                    'labels': epic.labels,
                    'state': epic.state
                } for epic in epics]
            else:
                # Fallback: use issues with 'epic' label
                issues = project.issues.list(labels=['epic'], all=True)
                return [self._format_issue(issue) for issue in issues]
        except:
            return []
    
    def _format_issue(self, issue) -> Dict:
        """Format GitLab issue for processing"""
        return {
            'id': issue.id,
            'iid': issue.iid,
            'title': issue.title,
            'description': issue.description,
            'state': issue.state,
            'labels': issue.labels,
            'assignees': [a.get('name', '') for a in issue.assignees] if hasattr(issue, 'assignees') else [],
            'created_at': issue.created_at,
            'closed_at': issue.closed_at if hasattr(issue, 'closed_at') else None,
            'web_url': issue.web_url,
            'time_stats': issue.time_stats if hasattr(issue, 'time_stats') else {}
        }
    
    def _format_mr(self, mr) -> Dict:
        """Format GitLab merge request"""
        return {
            'id': mr.id,
            'iid': mr.iid,
            'title': mr.title,
            'description': mr.description,
            'state': mr.state,
            'merged_at': mr.merged_at if hasattr(mr, 'merged_at') else None,
            'author': mr.author.get('name', '') if hasattr(mr, 'author') else '',
            'web_url': mr.web_url
        }
    
    def _format_commit(self, commit) -> Dict:
        """Format GitLab commit"""
        return {
            'id': commit.id,
            'short_id': commit.short_id,
            'title': commit.title,
            'message': commit.message,
            'author_name': commit.author_name,
            'created_at': commit.created_at
        }
    
    def _analyze_agile_metrics(self, state: GitLabInterrogatorState) -> GitLabInterrogatorState:
        """
        Node 2: Analyze Agile metrics
        """
        start_time = time.time()
        self.logger.info("Node: Analyzing Agile metrics...")
        
        try:
            use_case = state['use_case']
            gitlab_data = state['gitlab_data']
            metrics = {}
            
            if use_case == 'sprint_summary':
                issues = gitlab_data.get('issues', [])
                
                # Calculate basic metrics
                total_issues = len(issues)
                completed_issues = len([i for i in issues if i['state'] == 'closed'])
                incomplete_issues = total_issues - completed_issues
                completion_rate = completed_issues / total_issues if total_issues > 0 else 0
                
                # Calculate story points (if tracked in labels or time estimates)
                total_points = 0
                completed_points = 0
                for issue in issues:
                    # Look for story point labels (e.g., "sp:5")
                    points = 0
                    for label in issue.get('labels', []):
                        if label.startswith('sp:'):
                            points = int(label.split(':')[1])
                            break
                    total_points += points
                    if issue['state'] == 'closed':
                        completed_points += points
                
                metrics = {
                    'total_issues': total_issues,
                    'completed_issues': completed_issues,
                    'incomplete_issues': incomplete_issues,
                    'completion_rate': completion_rate,
                    'total_story_points': total_points,
                    'completed_story_points': completed_points,
                    'velocity': completed_points,
                    'merge_requests': len(gitlab_data.get('merge_requests', []))
                }
            
            elif use_case == 'release_notes':
                commits = gitlab_data.get('commits', [])
                closed_issues = gitlab_data.get('closed_issues', [])
                
                # Categorize commits (conventional commits)
                features = []
                fixes = []
                breaking = []
                other = []
                
                for commit in commits:
                    message = commit['title'].lower()
                    if message.startswith('feat:') or message.startswith('feature:'):
                        features.append(commit)
                    elif message.startswith('fix:'):
                        fixes.append(commit)
                    elif message.startswith('break') or 'breaking' in message:
                        breaking.append(commit)
                    else:
                        other.append(commit)
                
                metrics = {
                    'total_commits': len(commits),
                    'features_count': len(features),
                    'fixes_count': len(fixes),
                    'breaking_changes_count': len(breaking),
                    'issues_closed': len(closed_issues),
                    'contributors': list(set([c['author_name'] for c in commits]))
                }
            
            elif use_case == 'epic_categorization':
                epics = gitlab_data.get('epics', [])
                metrics = {
                    'total_epics': len(epics),
                    'states': {},
                    'label_frequency': {}
                }
                
                # Count by state
                for epic in epics:
                    state_val = epic.get('state', 'unknown')
                    metrics['states'][state_val] = metrics['states'].get(state_val, 0) + 1
                    
                    # Count labels
                    for label in epic.get('labels', []):
                        metrics['label_frequency'][label] = metrics['label_frequency'].get(label, 0) + 1
            
            state['metrics'] = metrics
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='analyze_agile_metrics',
                action='Calculated Agile metrics',
                details=metrics,
                duration_ms=duration
            )
            
            self.logger.info("✓ Metrics analysis complete")
            
        except Exception as e:
            self.logger.error(f"✗ Metrics analysis failed: {e}")
            state['metrics'] = {}
        
        return state
    
    def _generate_insights(self, state: GitLabInterrogatorState) -> GitLabInterrogatorState:
        """
        Node 3: Generate AI insights
        """
        start_time = time.time()
        self.logger.info("Node: Generating insights...")
        
        try:
            use_case = state['use_case']
            input_data = state['input_data']
            gitlab_data = state['gitlab_data']
            metrics = state['metrics']
            
            insights = {}
            
            if use_case == 'story_creation':
                insights = self._generate_story_insights(input_data, gitlab_data)
            
            elif use_case == 'sprint_summary':
                insights = self._generate_sprint_insights(gitlab_data, metrics)
            
            elif use_case == 'release_notes':
                insights = self._generate_release_insights(gitlab_data, metrics)
            
            elif use_case == 'epic_categorization':
                insights = self._generate_epic_insights(gitlab_data, metrics)
            
            state['insights'] = insights
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='generate_insights',
                action='Generated AI insights',
                duration_ms=duration
            )
            
            self.logger.info("✓ Insights generated")
            
        except Exception as e:
            self.logger.error(f"✗ Insight generation failed: {e}")
            state['insights'] = {}
        
        return state
    
    def _generate_story_insights(self, input_data: Dict, gitlab_data: Dict) -> Dict:
        """Generate user story from requirements using AI"""
        requirement = input_data.get('requirement', '')
        project_context = gitlab_data.get('project', {})
        
        prompt = f"""
You are an expert Agile coach creating user stories.

Project: {project_context.get('name', 'Unknown')}
Requirement: {requirement}

Create a well-structured user story with:
1. Title (concise, action-oriented)
2. User story (As a... I want... So that...)
3. Acceptance criteria (Given/When/Then format, 3-5 criteria)
4. Story points estimate (Fibonacci: 1, 2, 3, 5, 8, 13)
5. Suggested labels

Return ONLY a JSON object:
{{
  "title": "User Story Title",
  "description": "As a...",
  "acceptance_criteria": ["Given...", "Given..."],
  "story_points": 5,
  "labels": ["feature", "backend"],
  "notes": "Additional context or dependencies"
}}
"""
        
        response = self.llm.invoke([
            {"role": "system", "content": "You are an expert Agile coach."},
            {"role": "user", "content": prompt}
        ])
        
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        
        return json.loads(content)
    
    def _generate_sprint_insights(self, gitlab_data: Dict, metrics: Dict) -> Dict:
        """Generate sprint summary insights using AI"""
        milestone = gitlab_data.get('milestone', {})
        issues = gitlab_data.get('issues', [])
        
        # Get incomplete issues for analysis
        incomplete = [i for i in issues if i['state'] != 'closed']
        
        prompt = f"""
Analyze this sprint and provide insights:

Sprint: {milestone.get('title', 'Unknown')}
Duration: {milestone.get('start_date', '')} to {milestone.get('due_date', '')}

Metrics:
- Completed: {metrics.get('completed_issues', 0)}/{metrics.get('total_issues', 0)} issues
- Velocity: {metrics.get('velocity', 0)} story points
- Completion rate: {metrics.get('completion_rate', 0):.0%}

Incomplete issues: {len(incomplete)}

Provide sprint summary with:
1. Overall assessment (Good/Fair/Needs Improvement)
2. Key achievements (2-3 bullet points)
3. Blockers and risks identified
4. Recommendations for next sprint

Return ONLY a JSON object:
{{
  "assessment": "Good",
  "achievements": ["Achievement 1", "Achievement 2"],
  "blockers": ["Blocker 1"],
  "risks": ["Risk 1"],
  "recommendations": ["Recommendation 1", "Recommendation 2"]
}}
"""
        
        response = self.llm.invoke([
            {"role": "system", "content": "You are a Scrum Master analyzing sprint performance."},
            {"role": "user", "content": prompt}
        ])
        
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        
        result = json.loads(content)
        result['metrics'] = metrics
        return result
    
    def _generate_release_insights(self, gitlab_data: Dict, metrics: Dict) -> Dict:
        """Generate release notes using AI"""
        commits = gitlab_data.get('commits', [])[:50]  # Limit for token size
        closed_issues = gitlab_data.get('closed_issues', [])[:30]
        
        commit_messages = "\n".join([f"- {c['title']}" for c in commits])
        issue_titles = "\n".join([f"- {i['title']}" for i in closed_issues])
        
        prompt = f"""
Generate professional release notes from these changes:

Recent commits:
{commit_messages}

Closed issues:
{issue_titles}

Create release notes with:
1. Features (new capabilities, enhancements)
2. Bug Fixes (resolved issues)
3. Breaking Changes (if any)
4. Notable changes or improvements

Return ONLY a JSON object:
{{
  "features": ["Feature description 1", "Feature description 2"],
  "fixes": ["Bug fix 1", "Bug fix 2"],
  "breaking_changes": [],
  "notable": ["Notable change 1"],
  "summary": "Brief 2-sentence overview of this release"
}}
"""
        
        response = self.llm.invoke([
            {"role": "system", "content": "You are a technical writer creating release notes."},
            {"role": "user", "content": prompt}
        ])
        
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        
        result = json.loads(content)
        result['contributors'] = metrics.get('contributors', [])
        return result
    
    def _generate_epic_insights(self, gitlab_data: Dict, metrics: Dict) -> Dict:
        """Categorize epics using AI"""
        epics = gitlab_data.get('epics', [])
        categories = gitlab_data.get('categories', [])
        
        epic_summaries = []
        for epic in epics[:50]:  # Limit for token size
            epic_summaries.append({
                'id': epic['id'],
                'title': epic['title'],
                'description': (epic.get('description', '') or '')[:200],  # Truncate
                'labels': epic.get('labels', [])
            })
        
        prompt = f"""
Categorize these epics into appropriate themes:

Available categories: {', '.join(categories)}

Epics:
{json.dumps(epic_summaries, indent=2)}

For each epic, determine the best category and provide confidence score (0.0-1.0).

Return ONLY a JSON object:
{{
  "categorized": {{
    "Category Name": [
      {{"id": 1, "title": "Epic Title", "confidence": 0.95, "rationale": "Why this category"}}
    ]
  }},
  "uncategorized": [],
  "new_category_suggestions": ["Suggested Category"]
}}
"""
        
        response = self.llm.invoke([
            {"role": "system", "content": "You are a project manager organizing epics."},
            {"role": "user", "content": prompt}
        ])
        
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        
        return json.loads(content)
    
    def _create_artifacts(self, state: GitLabInterrogatorState) -> GitLabInterrogatorState:
        """
        Node 4: Create formatted artifacts
        """
        start_time = time.time()
        self.logger.info("Node: Creating artifacts...")
        
        try:
            use_case = state['use_case']
            insights = state['insights']
            artifacts = {}
            
            if use_case == 'story_creation':
                artifacts = self._format_user_story(insights)
            
            elif use_case == 'sprint_summary':
                artifacts = self._format_sprint_report(insights)
            
            elif use_case == 'release_notes':
                artifacts = self._format_release_notes(insights, state['input_data'])
            
            elif use_case == 'epic_categorization':
                artifacts = self._format_epic_taxonomy(insights)
            
            state['artifacts'] = artifacts
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='create_artifacts',
                action='Created formatted artifacts',
                duration_ms=duration
            )
            
            self.logger.info("✓ Artifacts created")
            
        except Exception as e:
            self.logger.error(f"✗ Artifact creation failed: {e}")
            state['artifacts'] = {}
        
        return state
    
    def _format_user_story(self, insights: Dict) -> Dict:
        """Format user story for GitLab"""
        description = f"""
{insights.get('description', '')}

## Acceptance Criteria

"""
        for idx, criteria in enumerate(insights.get('acceptance_criteria', []), 1):
            description += f"{idx}. {criteria}\n"
        
        if insights.get('notes'):
            description += f"\n## Notes\n\n{insights['notes']}\n"
        
        return {
            'title': insights.get('title', ''),
            'description': description,
            'labels': insights.get('labels', []),
            'story_points': insights.get('story_points', 0),
            'gitlab_payload': {
                'title': insights.get('title', ''),
                'description': description,
                'labels': ','.join(insights.get('labels', []))
            }
        }
    
    def _format_sprint_report(self, insights: Dict) -> Dict:
        """Format sprint summary report"""
        metrics = insights.get('metrics', {})
        
        report = f"""# Sprint Summary

## Overview
**Assessment:** {insights.get('assessment', 'Unknown')}

## Metrics
- **Completion Rate:** {metrics.get('completion_rate', 0):.0%}
- **Completed:** {metrics.get('completed_issues', 0)}/{metrics.get('total_issues', 0)} issues
- **Velocity:** {metrics.get('velocity', 0)} story points

## Key Achievements
"""
        for achievement in insights.get('achievements', []):
            report += f"- {achievement}\n"
        
        if insights.get('blockers'):
            report += "\n## Blockers\n"
            for blocker in insights['blockers']:
                report += f"- {blocker}\n"
        
        if insights.get('recommendations'):
            report += "\n## Recommendations for Next Sprint\n"
            for rec in insights['recommendations']:
                report += f"- {rec}\n"
        
        return {
            'markdown': report,
            'metrics': metrics,
            'assessment': insights.get('assessment', 'Unknown')
        }
    
    def _format_release_notes(self, insights: Dict, input_data: Dict) -> Dict:
        """Format release notes in Keep a Changelog style"""
        version = input_data.get('tag_name', 'Unreleased')
        date = datetime.now().strftime('%Y-%m-%d')
        
        notes = f"""# Release {version}

**Release Date:** {date}

## Summary
{insights.get('summary', 'This release includes new features and bug fixes.')}

"""
        
        if insights.get('breaking_changes'):
            notes += "## ⚠️ Breaking Changes\n"
            for change in insights['breaking_changes']:
                notes += f"- {change}\n"
            notes += "\n"
        
        if insights.get('features'):
            notes += "## ✨ Features\n"
            for feature in insights['features']:
                notes += f"- {feature}\n"
            notes += "\n"
        
        if insights.get('fixes'):
            notes += "## 🐛 Bug Fixes\n"
            for fix in insights['fixes']:
                notes += f"- {fix}\n"
            notes += "\n"
        
        if insights.get('notable'):
            notes += "## 📝 Notable Changes\n"
            for item in insights['notable']:
                notes += f"- {item}\n"
            notes += "\n"
        
        if insights.get('contributors'):
            notes += f"## 👥 Contributors\n"
            for contributor in insights['contributors'][:10]:
                notes += f"- @{contributor}\n"
        
        return {
            'markdown': notes,
            'version': version,
            'date': date
        }
    
    def _format_epic_taxonomy(self, insights: Dict) -> Dict:
        """Format epic categorization results"""
        categorized = insights.get('categorized', {})
        
        markdown = "# Epic Categorization\n\n"
        
        for category, epics in categorized.items():
            markdown += f"## {category}\n\n"
            for epic in epics:
                confidence_pct = int(epic.get('confidence', 0) * 100)
                markdown += f"- **{epic['title']}** (Confidence: {confidence_pct}%)\n"
                if epic.get('rationale'):
                    markdown += f"  - Rationale: {epic['rationale']}\n"
            markdown += "\n"
        
        if insights.get('new_category_suggestions'):
            markdown += "## Suggested New Categories\n\n"
            for suggestion in insights['new_category_suggestions']:
                markdown += f"- {suggestion}\n"
        
        return {
            'markdown': markdown,
            'categorized': categorized,
            'taxonomy': list(categorized.keys())
        }
    
    def _compile_report(self, state: GitLabInterrogatorState) -> GitLabInterrogatorState:
        """
        Node 5: Compile final report
        """
        start_time = time.time()
        self.logger.info("Node: Compiling report...")
        
        try:
            use_case = state['use_case']
            artifacts = state['artifacts']
            
            # Get the main content (usually markdown)
            report = artifacts.get('markdown', '')
            
            # Add execution metadata
            report += f"\n\n---\n\n*Generated by GitLab Interrogator AI*\n"
            report += f"*Task ID: {state['task_id']}*\n"
            report += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
            
            state['report'] = report
            state['processing_status'] = 'completed'
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='compile_report',
                action='Compiled final report',
                duration_ms=duration
            )
            
            self.logger.info("✓ Report compilation complete")
            
        except Exception as e:
            self.logger.error(f"✗ Report compilation failed: {e}")
            state['report'] = "Error generating report"
            state['processing_status'] = 'failed'
        
        return state
    
    def process(self, task_id: str, use_case: str, input_data: Dict) -> Dict:
        """
        Main entry point for processing GitLab workflows
        
        Args:
            task_id: Unique task identifier
            use_case: One of 'story_creation', 'sprint_summary', 'release_notes', 'epic_categorization'
            input_data: Use case-specific input data
        
        Returns:
            Complete processing results
        """
        self.logger.info(f"Processing task: {task_id} ({use_case})")
        
        # Initialize state
        initial_state = GitLabInterrogatorState(
            task_id=task_id,
            use_case=use_case,
            input_data=input_data,
            gitlab_url=self.gitlab_url,
            gitlab_token=self.gitlab_token,
            project_id=input_data.get('project_id'),
            gitlab_data=None,
            metrics=None,
            insights=None,
            artifacts=None,
            report=None,
            execution_trace=[],
            processing_status='processing',
            error=None
        )
        
        # Execute workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            # Format result
            result = {
                'task_id': task_id,
                'use_case': use_case,
                'status': final_state.get('processing_status', 'completed'),
                'error': final_state.get('error'),
                'metrics': final_state.get('metrics', {}),
                'insights': final_state.get('insights', {}),
                'artifacts': final_state.get('artifacts', {}),
                'report': final_state.get('report', ''),
                'execution_trace': final_state.get('execution_trace', []),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("✓ Task processing complete")
            return result
            
        except Exception as e:
            self.logger.error(f"✗ Task processing failed: {e}")
            raise
    
    def get_workflow_graph(self) -> Dict[str, Any]:
        """Get workflow structure for visualization"""
        nodes = [
            {"id": "fetch_gitlab_data", "name": "Fetch GitLab Data", "type": "node",
             "description": "Retrieve data from GitLab API"},
            {"id": "analyze_agile_metrics", "name": "Analyze Metrics", "type": "node",
             "description": "Calculate sprint velocity, completion rates"},
            {"id": "generate_insights", "name": "Generate Insights", "type": "node",
             "description": "Use AI for semantic analysis"},
            {"id": "create_artifacts", "name": "Create Artifacts", "type": "node",
             "description": "Format stories, reports, release notes"},
            {"id": "compile_report", "name": "Compile Report", "type": "node",
             "description": "Assemble final output"}
        ]
        
        edges = [
            {"source": "fetch_gitlab_data", "target": "analyze_agile_metrics"},
            {"source": "analyze_agile_metrics", "target": "generate_insights"},
            {"source": "generate_insights", "target": "create_artifacts"},
            {"source": "create_artifacts", "target": "compile_report"}
        ]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "workflow_type": "GitLab Agile Automation",
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }


# Initialize agent
def create_agent():
    """Factory function to create agent instance"""
    try:
        return GitLabInterrogatorAgent()
    except Exception as e:
        logging.error(f"Failed to initialize agent: {e}")
        return None
