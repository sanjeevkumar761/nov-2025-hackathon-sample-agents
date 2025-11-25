/**
 * Type definitions for Creds Inspect API
 */

export interface CredentialFinding {
  type: string;
  value: string;
  position: number;
  line: number;
  context: string;
  detection_method: 'pattern' | 'ai';
  confidence: number;
  severity?: 'high' | 'medium' | 'low';
  is_active?: boolean;
  exposure_scope?: 'public' | 'internal' | 'private' | 'unknown';
}

export interface RiskAssessment {
  overall_risk: 'high' | 'medium' | 'low' | 'unknown';
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  critical_findings: string[];
  compliance_violations?: string[];
}

export interface RemediationAction {
  credential_type: string;
  priority: 'immediate' | 'urgent' | 'normal';
  immediate_actions: string[];
  verification_steps: string[];
  prevention: string[];
  notification_template: string;
  timeline: string;
}

export interface ScanSummary {
  credentials_found: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  overall_risk: 'high' | 'medium' | 'low' | 'unknown';
}

export interface ExecutionTraceStep {
  step: number;
  node: string;
  action: string;
  timestamp: string;
  duration_ms: number;
  status: string;
  details: Record<string, any>;
}

export interface ScanResult {
  scan_id: string;
  metadata: Record<string, any>;
  content_type: string;
  scan_summary: ScanSummary;
  detected_credentials: CredentialFinding[];
  risk_assessment: RiskAssessment;
  remediation_plan: RemediationAction[];
  executive_report: string;
  execution_trace: ExecutionTraceStep[];
  status: string;
  timestamp: string;
}

export interface ScanListItem {
  scan_id: string;
  content_type: string;
  credentials_found: number;
  overall_risk: 'high' | 'medium' | 'low' | 'unknown';
  submitted_at: string;
  status: 'submitted' | 'analyzing' | 'completed' | 'failed';
}

export interface ContentSubmission {
  content: string;
  content_type?: string;
  source_url?: string;
  metadata?: Record<string, any>;
}

export interface ScanSubmissionResponse {
  scan_id: string;
  status: string;
  message: string;
  submitted_at: string;
}

export interface WorkflowNode {
  id: string;
  name: string;
  type: string;
  description: string;
}

export interface WorkflowEdge {
  source: string;
  target: string;
}

export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  workflow_type: string;
  total_nodes: number;
  total_edges: number;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  agent_ready: boolean;
  version: string;
}

export interface StatsResponse {
  total_scans: number;
  completed_scans: number;
  analyzing_scans: number;
  total_credentials_found: number;
  high_risk_findings: number;
  medium_risk_findings: number;
  low_risk_findings: number;
}
