// API Types

export interface DocumentMetadata {
  filename: string;
  file_size: number;
  upload_date: string;
  source?: string;
  regulator?: string;
  document_type?: string;
}

export interface LRRItem {
  type: 'Law' | 'Rule' | 'Regulation';
  reference: string;
  description: string;
  requirement: string;
  obligated_parties: string[];
  penalties?: string[];
  severity: 'high' | 'medium' | 'low';
}

export interface TaxonomyImpact {
  area: string;
  impact_type: string;
  description: string;
  urgency: 'high' | 'medium' | 'low';
  recommended_action: string;
}

export interface RiskAssessment {
  high_risks: string[];
  medium_risks: string[];
  low_risks: string[];
  overall_risk_level: 'high' | 'medium' | 'low';
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

export interface AnalysisResult {
  document_id: string;
  document_metadata: DocumentMetadata;
  analysis_date: string;
  extracted_sections: any[];
  identified_lrr: LRRItem[];
  categorized_rules: {
    high_priority: LRRItem[];
    medium_priority: LRRItem[];
    low_priority: LRRItem[];
    reporting_requirements: LRRItem[];
    operational_requirements: LRRItem[];
    compliance_deadlines: LRRItem[];
  };
  taxonomy_impacts: TaxonomyImpact[];
  summary: string;
  risk_assessment?: RiskAssessment;
  execution_trace: ExecutionTraceStep[];
}

export interface UploadResponse {
  document_id: string;
  filename: string;
  file_size: number;
  status: string;
  message: string;
  text_length: number;
}

export interface AnalyzeResponse {
  document_id: string;
  status: string;
  message: string;
  summary?: {
    lrr_identified: number;
    taxonomy_impacts: number;
    risk_level: string;
  };
}

export interface DocumentListItem {
  document_id: string;
  filename: string;
  upload_date: string;
  status: string;
}

export interface DocumentInfo {
  document_id: string;
  document_metadata?: DocumentMetadata;
  upload_date: string;
  status: string;
}

export interface WorkflowNode {
  id: string;
  name: string;
  type: string;
  description?: string;
}

export interface WorkflowEdge {
  source: string;
  target: string;
  label?: string;
}

export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  workflow_type: string;
  total_nodes: number;
  total_edges: number;
}
