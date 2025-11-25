/**
 * TypeScript type definitions for GitLab Interrogator
 */

// ============================================================================
// User Story Types
// ============================================================================

export interface StoryCreationRequest {
  requirement: string;
  project_id: number;
  context?: string;
}

export interface StoryCreationResult {
  task_id: string;
  title: string;
  description: string;
  labels: string[];
  story_points: number;
  gitlab_payload: {
    title: string;
    description: string;
    labels: string;
  };
  execution_trace: ExecutionTraceStep[];
}

export interface BulkStoryRequest {
  requirements: string[];
  project_id: number;
  context?: string;
}

// ============================================================================
// Sprint Types
// ============================================================================

export interface SprintSummaryRequest {
  project_id: number;
  milestone_id: number;
}

export interface SprintSummary {
  task_id: string;
  milestone_title: string;
  assessment: 'Good' | 'Fair' | 'Needs Improvement';
  metrics: {
    total_issues: number;
    completed_issues: number;
    incomplete_issues: number;
    completion_rate: number;
    total_story_points: number;
    completed_story_points: number;
    velocity: number;
    merge_requests: number;
  };
  achievements: string[];
  blockers: string[];
  recommendations: string[];
  report_markdown: string;
  execution_trace: ExecutionTraceStep[];
}

export interface VelocityData {
  sprint: string;
  velocity: number;
  due_date: string | null;
}

// ============================================================================
// Release Notes Types
// ============================================================================

export interface ReleaseNotesRequest {
  project_id: number;
  tag_name: string;
  from_tag?: string;
  to_tag?: string;
  since?: string;
}

export interface ReleaseNotes {
  task_id: string;
  version: string;
  date: string;
  summary: string;
  features: string[];
  fixes: string[];
  breaking_changes: string[];
  contributors: string[];
  markdown: string;
  execution_trace: ExecutionTraceStep[];
}

// ============================================================================
// Epic Categorization Types
// ============================================================================

export interface EpicCategorizationRequest {
  project_id: number;
  categories?: string[];
}

export interface EpicCategorization {
  task_id: string;
  categorized: {
    [category: string]: Array<{
      id: number;
      title: string;
      confidence: number;
      rationale: string;
    }>;
  };
  taxonomy: string[];
  new_category_suggestions: string[];
  markdown: string;
  execution_trace: ExecutionTraceStep[];
}

// ============================================================================
// GitLab Types
// ============================================================================

export interface GitLabProject {
  id: number;
  name: string;
  description: string | null;
  web_url: string;
  path_with_namespace: string;
}

export interface GitLabMilestone {
  id: number;
  iid: number;
  title: string;
  description: string | null;
  state: string;
  start_date: string | null;
  due_date: string | null;
  web_url: string;
}

export interface GitLabIssue {
  id: number;
  iid: number;
  title: string;
  state: string;
  labels: string[];
  web_url: string;
}

// ============================================================================
// System Types
// ============================================================================

export interface ExecutionTraceStep {
  step: number;
  node: string;
  action: string;
  timestamp: string;
  duration_ms: number;
  status: string;
  details?: any;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'down';
  agent_status: string;
  gitlab_connection: string;
  timestamp: string;
}

export interface WorkflowGraph {
  nodes: Array<{
    id: string;
    name: string;
    type: string;
    description: string;
  }>;
  edges: Array<{
    source: string;
    target: string;
  }>;
  workflow_type: string;
  total_nodes: number;
  total_edges: number;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  timestamp: string;
}

// ============================================================================
// UI State Types
// ============================================================================

export type UseCaseTab = 'story' | 'sprint' | 'release' | 'epic';

export interface AppState {
  selectedProject: GitLabProject | null;
  activeTab: UseCaseTab;
  isLoading: boolean;
  error: string | null;
}
