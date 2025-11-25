// API Response Types
export interface DimensionScore {
  short_description: number
  long_description: number
  categorization: number
  resolution: number
}

export interface TicketAnalysisResponse {
  ticket_id: string
  overall_score: number
  threshold_met: boolean
  quality_status: 'Poor' | 'Fair' | 'Good' | 'Excellent'
  dimension_scores: DimensionScore
  deficiencies: string[]
  recommendations?: string[]
  automation_ready: boolean
}

export interface TicketEnrichmentRequest {
  ticket_id: string
  enrich_dimensions: string[]
  auto_update_snow: boolean
}

export interface TicketEnrichmentResponse {
  ticket_id: string
  enrichment_status: string
  before_score: number
  after_score: number
  improvement: number
  threshold_met: boolean
  quality_status: string
  enriched_data: Record<string, any>
  changes_made: string[]
  execution_time_ms?: number
}

export interface BatchTicketResult {
  ticket_id: string
  status: string
  before_score?: number
  after_score?: number
  improvement?: number
  error?: string
}

export interface BatchEnrichmentResponse {
  batch_id: string
  total_tickets: number
  processed: number
  successful: number
  failed: number
  avg_before_score: number
  avg_after_score: number
  avg_improvement: number
  threshold_met_count: number
  threshold_met_percentage: number
  execution_time_seconds: number
  results: BatchTicketResult[]
}

export interface AnalyticsSummaryResponse {
  period: string
  total_tickets_analyzed: number
  overall_statistics: {
    avg_score: number
    threshold_met: number
    threshold_met_percentage: number
    poor_quality: number
    fair_quality: number
    good_quality: number
    excellent_quality: number
  }
  dimension_breakdown: Record<string, {
    avg_score: number
    common_issues: string[]
  }>
  enrichment_roi?: {
    tickets_enriched: number
    avg_improvement: number
    new_threshold_met: number
    automation_candidates: number
    estimated_hours_saved: number
    cost_savings_usd: number
  }
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'down'
  timestamp: string
  agent_status: string
  snow_connection: string
  azure_openai_status: string
  uptime_seconds: number
}

// UI State Types
export type ModuleTab = 'analyzer' | 'enrichment' | 'batch' | 'analytics'

export interface AppState {
  currentModule: ModuleTab
  selectedTicketId: string
}
