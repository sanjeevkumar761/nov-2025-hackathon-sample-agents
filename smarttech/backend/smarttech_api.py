"""
SmartTech TSD Ticket Classification API

FastAPI REST API for the SmartTech AI-enabled ticket classification agent.

Endpoints:
- POST /api/v1/tickets/classify - Classify a single ticket
- POST /api/v1/tickets/batch-classify - Classify multiple tickets
- GET /api/v1/tickets/mock - Get mock ticket data
- GET /api/v1/kb/articles - Get all KB articles
- GET /api/v1/kb/articles/{article_id} - Get specific KB article
- GET /api/v1/health - Health check
- GET /api/v1/stats - Get classification statistics
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import logging

# Import the SmartTech agent
from smarttech_ticket_agent import (
    SmartTechTicketAgent,
    MOCK_TSD_TICKETS,
    KNOWLEDGE_BASE
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SmartTech TSD Ticket Classification API",
    description="AI-powered ticket classification system for SmartTech helpdesk",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance (initialized on startup)
agent: Optional[SmartTechTicketAgent] = None

# Statistics tracking
classification_stats = {
    "total_classifications": 0,
    "self_service_count": 0,
    "intents": {},
    "routing": {}
}


# Pydantic Models for API
class TicketRequest(BaseModel):
    """Request model for ticket classification"""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    subject: str = Field(..., description="Ticket subject/title", min_length=1)
    description: str = Field(..., description="Detailed ticket description", min_length=1)
    category: str = Field(..., description="Ticket category")
    priority: str = Field(..., description="Ticket priority (Low, Medium, High, Critical)")
    user: str = Field(..., description="User email or identifier")
    created_at: Optional[str] = Field(default=None, description="Ticket creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "TSD-2024-999",
                "subject": "Cannot access email",
                "description": "I'm unable to login to my email account. Getting authentication errors.",
                "category": "Email",
                "priority": "High",
                "user": "john.doe@smarttech.com",
                "created_at": "2024-11-22 10:00:00"
            }
        }


class BatchTicketRequest(BaseModel):
    """Request model for batch ticket classification"""
    tickets: List[TicketRequest] = Field(..., description="List of tickets to classify")

    class Config:
        json_schema_extra = {
            "example": {
                "tickets": [
                    {
                        "ticket_id": "TSD-2024-101",
                        "subject": "Password reset needed",
                        "description": "My password expired and I need to reset it",
                        "category": "Account",
                        "priority": "High",
                        "user": "user1@smarttech.com",
                        "created_at": "2024-11-22 09:00:00"
                    },
                    {
                        "ticket_id": "TSD-2024-102",
                        "subject": "VPN connection issues",
                        "description": "Cannot connect to VPN from home",
                        "category": "Network",
                        "priority": "Medium",
                        "user": "user2@smarttech.com",
                        "created_at": "2024-11-22 09:15:00"
                    }
                ]
            }
        }


class KBArticle(BaseModel):
    """Knowledge base article model"""
    article_id: str
    title: str
    avg_resolution_time: str
    success_rate: int
    steps_count: Optional[int] = None


class ExecutionTraceStep(BaseModel):
    """Execution trace step model"""
    step: int
    node: str
    action: str
    timestamp: str
    duration_ms: int
    status: str
    error: Optional[str] = None
    details: Dict[str, Any]


class ClassificationResult(BaseModel):
    """Response model for ticket classification"""
    ticket_id: str
    subject: str
    detected_intent: str
    confidence: float
    self_service_eligible: bool
    routing: str
    knowledge_base_articles: List[KBArticle]
    analysis: str
    execution_trace: Optional[List[ExecutionTraceStep]] = Field(default=None, description="Detailed workflow execution trace")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class BatchClassificationResult(BaseModel):
    """Response model for batch classification"""
    results: List[ClassificationResult]
    summary: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    agent_initialized: bool
    version: str


class StatsResponse(BaseModel):
    """Statistics response"""
    total_classifications: int
    self_service_count: int
    self_service_percentage: float
    intent_distribution: Dict[str, int]
    routing_distribution: Dict[str, int]


# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent
    try:
        logger.info("Initializing SmartTech Ticket Agent...")
        agent = SmartTechTicketAgent()
        logger.info("✓ Agent initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize agent: {e}")
        # Agent will be None, endpoints will return 503


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down SmartTech API...")


# Helper Functions
def update_statistics(result: Dict[str, Any]):
    """Update global statistics"""
    classification_stats["total_classifications"] += 1
    
    if result.get("self_service_eligible", False):
        classification_stats["self_service_count"] += 1
    
    intent = result.get("detected_intent", "unknown")
    classification_stats["intents"][intent] = classification_stats["intents"].get(intent, 0) + 1
    
    routing = result.get("routing", "UNKNOWN")
    classification_stats["routing"][routing] = classification_stats["routing"].get(routing, 0) + 1


def check_agent_ready():
    """Check if agent is initialized"""
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized. Check Azure OpenAI configuration."
        )


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "SmartTech TSD Ticket Classification API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/api/docs",
        "endpoints": {
            "classify": "POST /api/v1/tickets/classify",
            "batch_classify": "POST /api/v1/tickets/batch-classify",
            "mock_tickets": "GET /api/v1/tickets/mock",
            "kb_articles": "GET /api/v1/kb/articles",
            "health": "GET /api/v1/health",
            "stats": "GET /api/v1/stats"
        }
    }


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if agent is not None else "degraded",
        timestamp=datetime.now().isoformat(),
        agent_initialized=agent is not None,
        version="1.0.0"
    )


@app.post("/api/v1/tickets/classify", response_model=ClassificationResult, tags=["Classification"])
async def classify_ticket(ticket: TicketRequest):
    """
    Classify a single ticket and provide recommendations
    
    Args:
        ticket: Ticket information including subject, description, etc.
    
    Returns:
        Classification result with intent, confidence, routing, and KB articles
    """
    check_agent_ready()
    
    try:
        # Convert Pydantic model to dict
        ticket_dict = ticket.model_dump()
        
        # Set default created_at if not provided
        if not ticket_dict.get("created_at"):
            ticket_dict["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Classify the ticket
        logger.info(f"Classifying ticket: {ticket.ticket_id}")
        result = agent.classify_ticket(ticket_dict)
        
        # Update statistics
        update_statistics(result)
        
        # Convert to response model
        return ClassificationResult(**result)
        
    except Exception as e:
        logger.error(f"Error classifying ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}"
        )


@app.post("/api/v1/tickets/batch-classify", response_model=BatchClassificationResult, tags=["Classification"])
async def batch_classify_tickets(batch_request: BatchTicketRequest):
    """
    Classify multiple tickets in a single request
    
    Args:
        batch_request: List of tickets to classify
    
    Returns:
        Batch classification results with summary statistics
    """
    check_agent_ready()
    
    try:
        # Convert tickets to dicts
        tickets = []
        for ticket in batch_request.tickets:
            ticket_dict = ticket.model_dump()
            if not ticket_dict.get("created_at"):
                ticket_dict["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            tickets.append(ticket_dict)
        
        # Classify all tickets
        logger.info(f"Batch classifying {len(tickets)} tickets")
        results = agent.batch_classify_tickets(tickets)
        
        # Update statistics
        for result in results:
            update_statistics(result)
        
        # Generate summary
        summary = agent.generate_summary_statistics(results)
        
        # Convert to response models
        classification_results = [ClassificationResult(**r) for r in results]
        
        return BatchClassificationResult(
            results=classification_results,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error in batch classification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch classification failed: {str(e)}"
        )


@app.get("/api/v1/tickets/mock", tags=["Mock Data"])
async def get_mock_tickets():
    """
    Get all mock TSD tickets for testing
    
    Returns:
        List of mock tickets
    """
    return {
        "count": len(MOCK_TSD_TICKETS),
        "tickets": MOCK_TSD_TICKETS
    }


@app.get("/api/v1/tickets/mock/{ticket_id}", tags=["Mock Data"])
async def get_mock_ticket_by_id(ticket_id: str):
    """
    Get a specific mock ticket by ID
    
    Args:
        ticket_id: The ticket ID (e.g., TSD-2024-001)
    
    Returns:
        Mock ticket data
    """
    for ticket in MOCK_TSD_TICKETS:
        if ticket["ticket_id"] == ticket_id:
            return ticket
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Ticket {ticket_id} not found"
    )


@app.get("/api/v1/kb/articles", tags=["Knowledge Base"])
async def get_kb_articles():
    """
    Get all knowledge base articles
    
    Returns:
        Dictionary of all KB articles
    """
    return {
        "count": len(KNOWLEDGE_BASE),
        "articles": KNOWLEDGE_BASE
    }


@app.get("/api/v1/kb/articles/{article_id}", tags=["Knowledge Base"])
async def get_kb_article(article_id: str):
    """
    Get a specific knowledge base article
    
    Args:
        article_id: The article ID (e.g., KB-001)
    
    Returns:
        KB article details
    """
    for kb_key, article in KNOWLEDGE_BASE.items():
        if article["article_id"] == article_id:
            return article
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Article {article_id} not found"
    )


@app.get("/api/v1/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_statistics():
    """
    Get classification statistics since server startup
    
    Returns:
        Statistics about classifications performed
    """
    total = classification_stats["total_classifications"]
    self_service = classification_stats["self_service_count"]
    
    return StatsResponse(
        total_classifications=total,
        self_service_count=self_service,
        self_service_percentage=(self_service / total * 100) if total > 0 else 0,
        intent_distribution=classification_stats["intents"],
        routing_distribution=classification_stats["routing"]
    )


@app.delete("/api/v1/stats", tags=["Statistics"])
async def reset_statistics():
    """
    Reset classification statistics
    
    Returns:
        Confirmation message
    """
    global classification_stats
    classification_stats = {
        "total_classifications": 0,
        "self_service_count": 0,
        "intents": {},
        "routing": {}
    }
    
    return {
        "message": "Statistics reset successfully",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/workflow/graph", tags=["Workflow"])
async def get_workflow_graph():
    """
    Get the agent workflow graph structure
    
    Returns:
        Workflow graph with nodes and edges
    """
    check_agent_ready()
    
    try:
        graph_data = agent.get_workflow_graph()
        return graph_data
    except Exception as e:
        logger.error(f"Error getting workflow graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve workflow graph: {str(e)}"
        )


@app.get("/api/v1/workflow/mermaid", tags=["Workflow"])
async def get_workflow_mermaid():
    """
    Get the workflow graph as Mermaid diagram syntax
    
    Returns:
        Mermaid diagram syntax as plain text
    """
    check_agent_ready()
    
    try:
        mermaid_syntax = agent.get_workflow_mermaid()
        if mermaid_syntax:
            return {
                "mermaid": mermaid_syntax,
                "format": "mermaid",
                "description": "Copy this syntax to visualize at mermaid.live"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate Mermaid diagram"
            )
    except Exception as e:
        logger.error(f"Error getting Mermaid diagram: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve Mermaid diagram: {str(e)}"
        )


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "type": type(exc).__name__
        }
    )


# Main entry point
if __name__ == "__main__":
    print("\n" + "="*60)
    print("SmartTech TSD Ticket Classification API")
    print("="*60)
    print("\nStarting server...")
    print("API Documentation: http://localhost:8000/api/docs")
    print("Interactive API: http://localhost:8000/api/redoc")
    print("\nPress CTRL+C to stop the server")
    print("="*60 + "\n")
    
    # Run the server
    uvicorn.run(
        "smarttech_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
