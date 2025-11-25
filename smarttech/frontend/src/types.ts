// TypeScript types for SmartTech API

export interface Ticket {
  ticket_id: string;
  subject: string;
  description: string;
  category: string;
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  user: string;
  created_at?: string;
}

export interface KBArticle {
  article_id: string;
  title: string;
  avg_resolution_time: string;
  success_rate: number;
  steps_count?: number;
}

export interface ExecutionTraceStep {
  step: number;
  node: string;
  action: string;
  timestamp: string;
  duration_ms: number;
  status: 'success' | 'error';
  error?: string;
  details: {
    [key: string]: any;
  };
}

export interface ClassificationResult {
  ticket_id: string;
  subject: string;
  detected_intent: string;
  confidence: number;
  self_service_eligible: boolean;
  routing: string;
  knowledge_base_articles: KBArticle[];
  analysis: string;
  timestamp: string;
  execution_trace?: ExecutionTraceStep[];
}

export interface BatchClassificationResult {
  results: ClassificationResult[];
  summary: {
    total_tickets: number;
    self_service_eligible: number;
    self_service_percentage: number;
    average_confidence: number;
    routing_distribution: Record<string, number>;
    intent_distribution: Record<string, number>;
  };
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  agent_initialized: boolean;
  version: string;
}

export interface StatsResponse {
  total_classifications: number;
  self_service_count: number;
  self_service_percentage: number;
  intent_distribution: Record<string, number>;
  routing_distribution: Record<string, number>;
}

export interface MockTicketsResponse {
  count: number;
  tickets: Ticket[];
}
