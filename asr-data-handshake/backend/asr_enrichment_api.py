"""
ASR Data Enrichment API
========================

FastAPI backend for ServiceNow ticket enrichment.

Provides REST API for:
- Ticket quality analysis
- AI-powered enrichment
- Batch processing
- Quality analytics
- ServiceNow integration
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from asr_enrichment_agent import ASREnrichmentAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent instance
agent: Optional[ASREnrichmentAgent] = None


# ===========================
# Pydantic Models
# ===========================

# Ticket Analysis Models
class TicketAnalysisRequest(BaseModel):
    ticket_id: str = Field(..., description="ServiceNow ticket ID")
    include_recommendations: bool = Field(True, description="Include improvement recommendations")

class DimensionScore(BaseModel):
    short_description: float
    long_description: float
    categorization: float
    resolution: float

class TicketAnalysisResponse(BaseModel):
    ticket_id: str
    overall_score: float
    threshold_met: bool
    quality_status: str  # Poor/Fair/Good/Excellent
    dimension_scores: DimensionScore
    deficiencies: List[str]
    recommendations: Optional[List[str]] = None
    automation_ready: bool

# Ticket Enrichment Models
class TicketEnrichmentRequest(BaseModel):
    ticket_id: str = Field(..., description="ServiceNow ticket ID")
    enrich_dimensions: List[str] = Field(
        ['short_desc', 'long_desc', 'categorization'],
        description="Dimensions to enrich"
    )
    auto_update_snow: bool = Field(False, description="Automatically update ticket in ServiceNow")

class TicketEnrichmentResponse(BaseModel):
    ticket_id: str
    enrichment_status: str  # completed/failed
    before_score: float
    after_score: float
    improvement: float
    threshold_met: bool
    quality_status: str
    enriched_data: Dict[str, Any]
    changes_made: List[str]
    execution_time_ms: Optional[int] = None

# Batch Enrichment Models
class BatchEnrichmentRequest(BaseModel):
    ticket_ids: Optional[List[str]] = Field(None, description="Specific ticket IDs to enrich")
    filters: Optional[Dict[str, Any]] = Field(None, description="Query filters")
    limit: int = Field(1000, description="Maximum tickets to process")
    auto_update_snow: bool = Field(False, description="Auto-update ServiceNow")

class BatchTicketResult(BaseModel):
    ticket_id: str
    status: str  # success/failed
    before_score: Optional[float] = None
    after_score: Optional[float] = None
    improvement: Optional[float] = None
    error: Optional[str] = None

class BatchEnrichmentResponse(BaseModel):
    batch_id: str
    total_tickets: int
    processed: int
    successful: int
    failed: int
    avg_before_score: float
    avg_after_score: float
    avg_improvement: float
    threshold_met_count: int
    threshold_met_percentage: float
    execution_time_seconds: int
    results: List[BatchTicketResult]

# Quality Scoring Models
class QualityScoreRequest(BaseModel):
    ticket_data: Dict[str, Any] = Field(..., description="Ticket data to score")

class QualityScoreResponse(BaseModel):
    overall_score: float
    quality_status: str
    threshold_met: bool
    dimension_scores: DimensionScore
    automation_ready: bool

# Analytics Models
class AnalyticsSummaryResponse(BaseModel):
    period: str
    total_tickets_analyzed: int
    overall_statistics: Dict[str, Any]
    dimension_breakdown: Dict[str, Any]
    enrichment_roi: Optional[Dict[str, Any]] = None

class QualityTrendPoint(BaseModel):
    date: str
    avg_score: float
    threshold_met_percentage: float
    tickets_analyzed: int

class QualityTrendsResponse(BaseModel):
    period: str
    trend_data: List[QualityTrendPoint]
    overall_improvement: float

# ServiceNow Integration Models
class SNOWAssignmentGroup(BaseModel):
    sys_id: str
    name: str
    description: Optional[str] = None

class SNOWCategory(BaseModel):
    category: str
    subcategories: List[str]

# Health Check Models
class HealthResponse(BaseModel):
    status: str  # healthy/degraded/down
    timestamp: str
    agent_status: str
    snow_connection: str
    azure_openai_status: str
    uptime_seconds: int

# Error Response Model
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    ticket_id: Optional[str] = None


# ===========================
# Lifespan Management
# ===========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent on startup"""
    global agent
    
    logger.info("Initializing ASR Enrichment Agent...")
    
    try:
        agent = ASREnrichmentAgent()
        logger.info("Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        agent = None
    
    yield
    
    logger.info("Shutting down ASR Enrichment API")


# ===========================
# FastAPI Application
# ===========================

app = FastAPI(
    title="ASR Data Enrichment API",
    description="AI-powered ServiceNow ticket enrichment for automation enablement",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track startup time
startup_time = datetime.now()


# ===========================
# Health & System Endpoints
# ===========================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and connectivity"""
    
    # Check agent status
    agent_ok = agent is not None
    
    # Check ServiceNow connection (TODO: implement actual check)
    snow_ok = True
    
    # Check Azure OpenAI (TODO: implement actual check)
    azure_ok = True
    
    # Determine overall status
    if agent_ok and snow_ok and azure_ok:
        status = "healthy"
    elif agent_ok:
        status = "degraded"
    else:
        status = "down"
    
    uptime = int((datetime.now() - startup_time).total_seconds())
    
    return HealthResponse(
        status=status,
        timestamp=datetime.now().isoformat(),
        agent_status="initialized" if agent_ok else "not_initialized",
        snow_connection="connected" if snow_ok else "disconnected",
        azure_openai_status="connected" if azure_ok else "disconnected",
        uptime_seconds=uptime
    )


@app.get("/workflow/graph")
async def get_workflow_graph():
    """Get workflow visualization"""
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "nodes": [
            {"id": "fetch_ticket_data", "label": "Fetch Ticket Data", "type": "data"},
            {"id": "assess_quality", "label": "Assess Quality", "type": "analysis"},
            {"id": "enrich_content", "label": "Enrich Content", "type": "ai"},
            {"id": "categorize_route", "label": "Categorize & Route", "type": "ai"},
            {"id": "validate_output", "label": "Validate Output", "type": "validation"}
        ],
        "edges": [
            {"from": "fetch_ticket_data", "to": "assess_quality"},
            {"from": "assess_quality", "to": "enrich_content"},
            {"from": "enrich_content", "to": "categorize_route"},
            {"from": "categorize_route", "to": "validate_output"}
        ],
        "description": "5-node sequential workflow for ticket enrichment"
    }


@app.get("/stats")
async def get_statistics():
    """Get processing statistics"""
    
    # TODO: Implement actual statistics tracking
    return {
        "tickets_processed_today": 0,
        "tickets_processed_total": 0,
        "avg_processing_time_ms": 0,
        "success_rate": 0.0,
        "avg_quality_improvement": 0.0
    }


# ===========================
# Ticket Analysis Endpoints
# ===========================

@app.post("/api/tickets/analyze", response_model=TicketAnalysisResponse)
async def analyze_ticket(request: TicketAnalysisRequest):
    """Analyze ticket quality without enrichment"""
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    logger.info(f"Analyzing ticket {request.ticket_id}")
    
    try:
        # Process ticket (analysis only)
        result = agent.process(
            ticket_id=request.ticket_id,
            operation='analyze',
            enrich_dimensions=[]
        )
        
        return TicketAnalysisResponse(
            ticket_id=request.ticket_id,
            overall_score=result['before_score'],
            threshold_met=result['threshold_met'],
            quality_status=result['quality_status'],
            dimension_scores=DimensionScore(**result['dimension_scores']['before']),
            deficiencies=result.get('deficiencies', []),
            recommendations=result.get('recommendations', []) if request.include_recommendations else None,
            automation_ready=result['threshold_met']
        )
    
    except Exception as e:
        logger.error(f"Error analyzing ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Retrieve ticket with quality metrics"""
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Fetch and analyze ticket
        result = agent.process(
            ticket_id=ticket_id,
            operation='analyze',
            enrich_dimensions=[]
        )
        
        return {
            "ticket_id": ticket_id,
            "ticket_data": result.get('enriched_data', {}),
            "quality_score": result['before_score'],
            "quality_status": result['quality_status'],
            "threshold_met": result['threshold_met']
        }
    
    except Exception as e:
        logger.error(f"Error retrieving ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tickets/compare")
async def compare_tickets(ticket_id_1: str, ticket_id_2: str):
    """Compare quality scores of two tickets"""
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result1 = agent.process(ticket_id=ticket_id_1, operation='analyze', enrich_dimensions=[])
        result2 = agent.process(ticket_id=ticket_id_2, operation='analyze', enrich_dimensions=[])
        
        return {
            "ticket_1": {
                "ticket_id": ticket_id_1,
                "overall_score": result1['before_score'],
                "dimension_scores": result1['dimension_scores']['before']
            },
            "ticket_2": {
                "ticket_id": ticket_id_2,
                "overall_score": result2['before_score'],
                "dimension_scores": result2['dimension_scores']['before']
            },
            "difference": result1['before_score'] - result2['before_score']
        }
    
    except Exception as e:
        logger.error(f"Error comparing tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Ticket Enrichment Endpoints
# ===========================

@app.post("/api/tickets/enrich", response_model=TicketEnrichmentResponse)
async def enrich_ticket(request: TicketEnrichmentRequest):
    """Enrich a single ticket"""
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    logger.info(f"Enriching ticket {request.ticket_id}")
    
    start_time = datetime.now()
    
    try:
        result = agent.process(
            ticket_id=request.ticket_id,
            operation='enrich',
            enrich_dimensions=request.enrich_dimensions,
            auto_update_snow=request.auto_update_snow
        )
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return TicketEnrichmentResponse(
            ticket_id=request.ticket_id,
            enrichment_status=result['enrichment_status'],
            before_score=result['before_score'],
            after_score=result['after_score'],
            improvement=result['improvement'],
            threshold_met=result['threshold_met'],
            quality_status=result['quality_status'],
            enriched_data=result['enriched_data'],
            changes_made=result['changes_made'],
            execution_time_ms=execution_time
        )
    
    except Exception as e:
        logger.error(f"Error enriching ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tickets/batch", response_model=BatchEnrichmentResponse)
async def enrich_batch(request: BatchEnrichmentRequest, background_tasks: BackgroundTasks):
    """Batch enrich multiple tickets"""
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"Starting batch enrichment {batch_id}")
    
    start_time = datetime.now()
    
    # Get ticket IDs to process
    if request.ticket_ids:
        ticket_ids = request.ticket_ids[:request.limit]
    else:
        # TODO: Query ServiceNow with filters
        ticket_ids = []
    
    # Process tickets
    results = []
    successful = 0
    failed = 0
    total_before = 0.0
    total_after = 0.0
    threshold_met = 0
    
    for ticket_id in ticket_ids:
        try:
            result = agent.process(
                ticket_id=ticket_id,
                operation='enrich',
                enrich_dimensions=request.filters.get('enrich_dimensions', ['short_desc', 'long_desc', 'categorization']) if request.filters else ['short_desc', 'long_desc', 'categorization'],
                auto_update_snow=request.auto_update_snow
            )
            
            results.append(BatchTicketResult(
                ticket_id=ticket_id,
                status='success',
                before_score=result['before_score'],
                after_score=result['after_score'],
                improvement=result['improvement']
            ))
            
            successful += 1
            total_before += result['before_score']
            total_after += result['after_score']
            
            if result['threshold_met']:
                threshold_met += 1
        
        except Exception as e:
            logger.error(f"Error processing ticket {ticket_id}: {str(e)}")
            results.append(BatchTicketResult(
                ticket_id=ticket_id,
                status='failed',
                error=str(e)
            ))
            failed += 1
    
    execution_time = int((datetime.now() - start_time).total_seconds())
    
    total_processed = successful + failed
    avg_before = total_before / successful if successful > 0 else 0.0
    avg_after = total_after / successful if successful > 0 else 0.0
    avg_improvement = avg_after - avg_before
    threshold_percentage = (threshold_met / successful * 100) if successful > 0 else 0.0
    
    return BatchEnrichmentResponse(
        batch_id=batch_id,
        total_tickets=len(ticket_ids),
        processed=total_processed,
        successful=successful,
        failed=failed,
        avg_before_score=avg_before,
        avg_after_score=avg_after,
        avg_improvement=avg_improvement,
        threshold_met_count=threshold_met,
        threshold_met_percentage=threshold_percentage,
        execution_time_seconds=execution_time,
        results=results
    )


@app.put("/api/tickets/{ticket_id}/update")
async def update_ticket_in_snow(ticket_id: str, enriched_data: Dict[str, Any]):
    """Update ticket in ServiceNow with enriched data"""
    
    # TODO: Implement ServiceNow update
    return {
        "ticket_id": ticket_id,
        "update_status": "success",
        "message": "Ticket updated in ServiceNow"
    }


# ===========================
# Quality Scoring Endpoints
# ===========================

@app.post("/api/quality/score", response_model=QualityScoreResponse)
async def score_ticket_quality(request: QualityScoreRequest):
    """Score ticket quality without enrichment"""
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Calculate quality scores directly
        scores = agent._calculate_quality_score(request.ticket_data)
        
        quality_status = agent._get_quality_status(scores['overall'])
        threshold_met = scores['overall'] >= agent.quality_threshold
        
        return QualityScoreResponse(
            overall_score=scores['overall'],
            quality_status=quality_status,
            threshold_met=threshold_met,
            dimension_scores=DimensionScore(
                short_description=scores['short_description'],
                long_description=scores['long_description'],
                categorization=scores['categorization'],
                resolution=scores['resolution']
            ),
            automation_ready=threshold_met
        )
    
    except Exception as e:
        logger.error(f"Error scoring ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/quality/threshold")
async def check_threshold(ticket_id: str):
    """Check if ticket meets automation threshold"""
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = agent.process(
            ticket_id=ticket_id,
            operation='analyze',
            enrich_dimensions=[]
        )
        
        return {
            "ticket_id": ticket_id,
            "overall_score": result['before_score'],
            "threshold": agent.quality_threshold,
            "threshold_met": result['threshold_met'],
            "automation_ready": result['threshold_met']
        }
    
    except Exception as e:
        logger.error(f"Error checking threshold: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quality/validate")
async def validate_enrichment(ticket_id: str, original_data: Dict[str, Any], enriched_data: Dict[str, Any]):
    """Validate enrichment improvements"""
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        before_scores = agent._calculate_quality_score(original_data)
        after_scores = agent._calculate_quality_score(enriched_data)
        
        return {
            "ticket_id": ticket_id,
            "validation_status": "passed" if after_scores['overall'] > before_scores['overall'] else "failed",
            "before_score": before_scores['overall'],
            "after_score": after_scores['overall'],
            "improvement": after_scores['overall'] - before_scores['overall'],
            "dimension_improvements": {
                "short_description": after_scores['short_description'] - before_scores['short_description'],
                "long_description": after_scores['long_description'] - before_scores['long_description'],
                "categorization": after_scores['categorization'] - before_scores['categorization'],
                "resolution": after_scores['resolution'] - before_scores['resolution']
            }
        }
    
    except Exception as e:
        logger.error(f"Error validating enrichment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Analytics Endpoints
# ===========================

@app.get("/api/analytics/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    date_range: str = Query('last_30_days', description="Date range (last_7_days, last_30_days, last_90_days)")
):
    """Get overall quality analytics summary"""
    
    # TODO: Implement actual analytics from database
    # For now, return mock data
    
    return AnalyticsSummaryResponse(
        period="2024-10-23 to 2024-11-22",
        total_tickets_analyzed=25000,
        overall_statistics={
            "avg_score": 31.2,
            "threshold_met": 650,
            "threshold_met_percentage": 2.6,
            "poor_quality": 21500,
            "fair_quality": 2850,
            "good_quality": 550,
            "excellent_quality": 100
        },
        dimension_breakdown={
            "short_description": {
                "avg_score": 42.1,
                "common_issues": ["Missing system name (68%)", "Too vague (54%)", "Non-actionable (47%)"]
            },
            "long_description": {
                "avg_score": 18.7,
                "common_issues": ["Missing repro steps (89%)", "No error details (82%)", "Incomplete context (76%)"]
            },
            "categorization": {
                "avg_score": 38.5,
                "common_issues": ["No assignment group (72%)", "Wrong category (58%)", "Missing priority (34%)"]
            },
            "resolution": {
                "avg_score": 12.3,
                "common_issues": ["No resolution notes (91%)", "Vague resolution (7%)", "Missing root cause (94%)"]
            }
        },
        enrichment_roi={
            "tickets_enriched": 5200,
            "avg_improvement": 57.3,
            "new_threshold_met": 5015,
            "automation_candidates": 5015,
            "estimated_hours_saved": 15045,
            "cost_savings_usd": 1504500
        }
    )


@app.get("/api/analytics/trends", response_model=QualityTrendsResponse)
async def get_quality_trends(
    date_range: str = Query('last_30_days', description="Date range")
):
    """Get quality trends over time"""
    
    # TODO: Implement actual trend analysis
    return QualityTrendsResponse(
        period="2024-10-23 to 2024-11-22",
        trend_data=[],
        overall_improvement=0.0
    )


@app.get("/api/analytics/groups")
async def get_quality_by_group():
    """Get quality breakdown by assignment group"""
    
    # TODO: Implement actual group analysis
    return {
        "groups": []
    }


@app.get("/api/analytics/categories")
async def get_quality_by_category():
    """Get quality breakdown by category"""
    
    # TODO: Implement actual category analysis
    return {
        "categories": []
    }


# ===========================
# ServiceNow Integration Endpoints
# ===========================

@app.get("/api/snow/groups")
async def list_assignment_groups():
    """List ServiceNow assignment groups"""
    
    # TODO: Implement ServiceNow API call
    return {
        "groups": [
            {"sys_id": "1", "name": "Platform Engineering", "description": "Platform and infrastructure"},
            {"sys_id": "2", "name": "Application Support", "description": "Application support team"},
            {"sys_id": "3", "name": "Network Operations", "description": "Network and connectivity"},
            {"sys_id": "4", "name": "Database Team", "description": "Database administration"},
            {"sys_id": "5", "name": "Security Operations", "description": "Security and compliance"}
        ]
    }


@app.get("/api/snow/categories")
async def list_categories():
    """List ServiceNow categories and subcategories"""
    
    # TODO: Implement ServiceNow API call
    return {
        "categories": [
            {
                "category": "Software",
                "subcategories": ["Application", "Authentication Service", "API Gateway", "Database"]
            },
            {
                "category": "Hardware",
                "subcategories": ["Server", "Storage", "Network Device"]
            },
            {
                "category": "Network",
                "subcategories": ["Connectivity", "VPN", "Load Balancer", "Firewall"]
            },
            {
                "category": "Security",
                "subcategories": ["Access Control", "Vulnerability", "Malware"]
            }
        ]
    }


@app.get("/api/snow/knowledge")
async def search_knowledge_base(query: str):
    """Search ServiceNow knowledge base"""
    
    # TODO: Implement ServiceNow knowledge search
    return {
        "articles": []
    }


@app.post("/api/snow/create")
async def create_ticket_in_snow(ticket_data: Dict[str, Any]):
    """Create new ticket in ServiceNow"""
    
    # TODO: Implement ServiceNow ticket creation
    return {
        "ticket_id": "INC0025000",
        "status": "created",
        "message": "Ticket created in ServiceNow"
    }


# ===========================
# Run Server
# ===========================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', '8000'))
    
    logger.info(f"Starting ASR Data Enrichment API on {host}:{port}")
    
    uvicorn.run(
        "asr_enrichment_api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
