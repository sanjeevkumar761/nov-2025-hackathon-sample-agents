"""
Regulatory Requirements Analyzer API

FastAPI REST API for regulatory document analysis using LangGraph.

Endpoints:
- POST /api/v1/documents/upload - Upload regulatory document
- POST /api/v1/documents/analyze - Analyze uploaded document
- GET /api/v1/analysis/{document_id} - Get analysis results
- GET /api/v1/workflow/graph - Get workflow structure
- GET /api/v1/health - Health check
"""

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import logging
import os
import aiofiles
from pathlib import Path
import PyPDF2
import docx
from io import BytesIO

from regulatory_analyzer import RegulatoryAnalyzerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Regulatory Requirements Analyzer API",
    description="AI-powered regulatory document analysis system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[RegulatoryAnalyzerAgent] = None

# In-memory storage for analysis results (use database in production)
analysis_results = {}

# Upload directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)


# Pydantic Models
class DocumentMetadata(BaseModel):
    """Document metadata model"""
    filename: str
    file_size: int
    upload_date: str
    source: Optional[str] = None
    regulator: Optional[str] = None
    document_type: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Analysis request model"""
    document_id: str = Field(..., description="Document ID to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "DOC-2024-001"
            }
        }


class LRRItem(BaseModel):
    """Laws, Rules, Regulations item model"""
    type: str
    reference: str
    description: str
    requirement: str
    obligated_parties: List[str]
    penalties: Optional[str]
    severity: str


class TaxonomyImpact(BaseModel):
    """Taxonomy impact model"""
    area: str
    impact_type: str
    description: str
    urgency: str
    recommended_action: str


class RiskAssessment(BaseModel):
    """Risk assessment model"""
    high_risks: List[str]
    medium_risks: List[str]
    low_risks: List[str]
    overall_risk_level: str


class AnalysisResult(BaseModel):
    """Analysis result model"""
    document_id: str
    document_metadata: Dict[str, Any]
    analysis_date: str
    identified_lrr: List[Dict[str, Any]]
    categorized_rules: Dict[str, List[Dict[str, Any]]]
    taxonomy_impacts: List[Dict[str, Any]]
    summary: str
    risk_assessment: Optional[Dict[str, Any]] = None
    execution_trace: List[Dict[str, Any]]
    extracted_sections: Optional[List[Dict[str, Any]]] = []


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    agent_initialized: bool
    version: str


# Helper functions
def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(BytesIO(file_content))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from DOCX: {str(e)}"
        )


def check_agent_ready():
    """Check if agent is initialized"""
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized. Check Azure OpenAI configuration."
        )


# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent
    try:
        logger.info("Initializing Regulatory Analyzer Agent...")
        agent = RegulatoryAnalyzerAgent()
        logger.info("✓ Agent initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize agent: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Regulatory Analyzer API...")


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Regulatory Requirements Analyzer API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/api/docs",
        "endpoints": {
            "upload": "POST /api/v1/documents/upload",
            "analyze": "POST /api/v1/documents/analyze",
            "results": "GET /api/v1/analysis/{document_id}",
            "workflow": "GET /api/v1/workflow/graph",
            "health": "GET /api/v1/health"
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


@app.post("/api/v1/documents/upload", tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    source: Optional[str] = Form(None),
    regulator: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None)
):
    """
    Upload a regulatory document for analysis
    
    Supported formats: PDF, DOCX, TXT
    """
    check_agent_ready()
    
    try:
        # Validate file type
        allowed_extensions = {".pdf", ".docx", ".txt"}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Check file size (default 10MB limit)
        max_size = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "10")) * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {max_size / 1024 / 1024}MB"
            )
        
        # Generate document ID
        document_id = f"DOC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Save file
        file_path = UPLOAD_DIR / f"{document_id}{file_ext}"
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Extract text based on file type
        if file_ext == ".pdf":
            text = extract_text_from_pdf(content)
        elif file_ext == ".docx":
            text = extract_text_from_docx(content)
        else:  # .txt
            text = content.decode('utf-8', errors='ignore')
        
        # Store metadata and text
        metadata = {
            "filename": file.filename,
            "file_size": file_size,
            "upload_date": datetime.now().isoformat(),
            "source": source,
            "regulator": regulator,
            "document_type": document_type,
            "file_path": str(file_path)
        }
        
        analysis_results[document_id] = {
            "document_id": document_id,
            "metadata": metadata,
            "text": text,
            "status": "uploaded",
            "analysis_result": None
        }
        
        logger.info(f"Document uploaded: {document_id} ({file.filename})")
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "file_size": file_size,
            "status": "uploaded",
            "message": "Document uploaded successfully. Use /api/v1/documents/analyze to start analysis.",
            "text_length": len(text)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@app.post("/api/v1/documents/analyze", tags=["Analysis"])
async def analyze_document(request: AnalysisRequest):
    """
    Analyze an uploaded regulatory document
    
    This triggers the LangGraph workflow to extract LRR and assess impacts.
    """
    check_agent_ready()
    
    document_id = request.document_id
    
    # Check if document exists
    if document_id not in analysis_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found. Upload document first."
        )
    
    try:
        doc_data = analysis_results[document_id]
        
        # Check if already analyzed
        if doc_data.get("status") == "analyzed":
            return {
                "document_id": document_id,
                "status": "already_analyzed",
                "message": "Document already analyzed. Use GET /api/v1/analysis/{document_id} to retrieve results."
            }
        
        # Update status
        analysis_results[document_id]["status"] = "analyzing"
        
        logger.info(f"Starting analysis for document: {document_id}")
        
        # Perform analysis
        result = agent.analyze_document(
            document_id=document_id,
            document_text=doc_data["text"],
            metadata=doc_data["metadata"]
        )
        
        # Store result
        analysis_results[document_id]["analysis_result"] = result
        analysis_results[document_id]["status"] = "analyzed"
        
        logger.info(f"✓ Analysis complete for document: {document_id}")
        
        return {
            "document_id": document_id,
            "status": "analyzed",
            "message": "Analysis complete. Use GET /api/v1/analysis/{document_id} to retrieve full results.",
            "summary": {
                "lrr_identified": result['analysis']['lrr_identified'],
                "taxonomy_impacts": result['analysis']['taxonomy_impacts'],
                "risk_level": result.get('risk_assessment', {}).get('overall_risk_level', 'Unknown')
            }
        }
        
    except Exception as e:
        logger.error(f"Analysis failed for {document_id}: {e}")
        analysis_results[document_id]["status"] = "failed"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/api/v1/analysis/{document_id}", response_model=AnalysisResult, tags=["Analysis"])
async def get_analysis_results(document_id: str):
    """
    Get analysis results for a document
    
    Returns complete analysis including LRR, taxonomy impacts, and risk assessment.
    """
    if document_id not in analysis_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    
    doc_data = analysis_results[document_id]
    
    if doc_data["status"] != "analyzed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document not analyzed. Current status: {doc_data['status']}"
        )
    
    # Map the result to match frontend expectations
    result = doc_data["analysis_result"]
    return {
        "document_id": result["document_id"],
        "document_metadata": result["metadata"],
        "analysis_date": result["timestamp"],
        "identified_lrr": result["identified_lrr"],
        "categorized_rules": result["categorized_rules"],
        "taxonomy_impacts": result["taxonomy_impacts"],
        "summary": result.get("compliance_summary", ""),
        "risk_assessment": result.get("risk_assessment"),
        "execution_trace": result["execution_trace"],
        "extracted_sections": result.get("extracted_sections", [])
    }


@app.get("/api/v1/documents", tags=["Documents"])
async def list_documents():
    """List all uploaded documents"""
    documents = []
    for doc_id, data in analysis_results.items():
        documents.append({
            "document_id": doc_id,
            "filename": data["metadata"]["filename"],
            "upload_date": data["metadata"]["upload_date"],
            "status": data["status"]
        })
    
    return {
        "count": len(documents),
        "documents": documents
    }


@app.delete("/api/v1/documents/{document_id}", tags=["Documents"])
async def delete_document(document_id: str):
    """Delete a document and its analysis results"""
    if document_id not in analysis_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    
    # Delete file if exists
    doc_data = analysis_results[document_id]
    file_path = Path(doc_data["metadata"].get("file_path", ""))
    if file_path.exists():
        file_path.unlink()
    
    # Remove from memory
    del analysis_results[document_id]
    
    logger.info(f"Document deleted: {document_id}")
    
    return {
        "document_id": document_id,
        "message": "Document deleted successfully"
    }


@app.get("/api/v1/workflow/graph", tags=["Workflow"])
async def get_workflow_graph():
    """Get the agent workflow graph structure"""
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
    print("Regulatory Requirements Analyzer API")
    print("="*60)
    print("\nStarting server...")
    print("API Documentation: http://localhost:8000/api/docs")
    print("Interactive API: http://localhost:8000/api/redoc")
    print("\nPress CTRL+C to stop the server")
    print("="*60 + "\n")
    
    # Run the server
    uvicorn.run(
        "regulatory_api:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True,
        log_level="info"
    )
