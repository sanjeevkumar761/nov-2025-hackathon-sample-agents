"""
Creds Inspect API Server

FastAPI server exposing credential detection endpoints.
"""

import os
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from creds_inspect_agent import create_agent

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Creds Inspect API",
    description="AI-powered credential detection for Confluence content",
    version="1.0.0"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize agent
logger.info("Initializing Creds Inspect Agent...")
agent = create_agent()
if agent is None:
    logger.error("Failed to initialize agent")
else:
    logger.info("✓ Agent initialized successfully")

# In-memory storage (use database in production)
scans_storage: Dict[str, Dict] = {}
content_storage: Dict[str, str] = {}

# Upload directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

# ============================================================================
# Pydantic Models
# ============================================================================

class ContentSubmission(BaseModel):
    """Content submission for scanning"""
    content: str = Field(..., description="Text content to scan")
    content_type: str = Field(default="text", description="Type: confluence_page, attachment, text")
    source_url: Optional[str] = Field(None, description="Source URL if applicable")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ScanSubmissionResponse(BaseModel):
    """Response after content submission"""
    scan_id: str
    status: str
    message: str
    submitted_at: str


class CredentialFinding(BaseModel):
    """Individual credential finding"""
    type: str
    value: str
    position: int
    line: int
    context: str
    detection_method: str
    confidence: float
    severity: Optional[str] = None
    is_active: Optional[bool] = None
    exposure_scope: Optional[str] = None


class RiskAssessment(BaseModel):
    """Risk assessment results"""
    overall_risk: str
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    critical_findings: List[str]
    compliance_violations: Optional[List[str]] = None


class RemediationAction(BaseModel):
    """Remediation action plan"""
    credential_type: str
    priority: str
    immediate_actions: List[str]
    verification_steps: List[str]
    prevention: List[str]
    notification_template: str
    timeline: str


class ScanSummary(BaseModel):
    """Scan summary metrics"""
    credentials_found: int
    high_risk: int
    medium_risk: int
    low_risk: int
    overall_risk: str


class ScanResult(BaseModel):
    """Complete scan result"""
    scan_id: str
    metadata: Dict[str, Any]
    content_type: str
    scan_summary: ScanSummary
    detected_credentials: List[CredentialFinding]
    risk_assessment: RiskAssessment
    remediation_plan: List[RemediationAction]
    executive_report: str
    execution_trace: List[Dict[str, Any]]
    status: str
    timestamp: str


class ScanListItem(BaseModel):
    """Scan list item for GET /scans"""
    scan_id: str
    content_type: str
    credentials_found: int
    overall_risk: str
    submitted_at: str
    status: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    agent_ready: bool
    version: str


class WorkflowGraph(BaseModel):
    """Workflow structure"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    workflow_type: str
    total_nodes: int
    total_edges: int


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": agent is not None,
        "version": "1.0.0"
    }


@app.post("/scans/submit", response_model=ScanSubmissionResponse)
async def submit_content(submission: ContentSubmission):
    """
    Submit content for credential scanning (text-based)
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        
        # Store content
        content_storage[scan_id] = submission.content
        
        # Store scan metadata
        scans_storage[scan_id] = {
            'scan_id': scan_id,
            'content_type': submission.content_type,
            'source_url': submission.source_url,
            'metadata': submission.metadata,
            'submitted_at': datetime.now().isoformat(),
            'status': 'submitted',
            'result': None
        }
        
        logger.info(f"Content submitted: {scan_id}")
        
        return {
            "scan_id": scan_id,
            "status": "submitted",
            "message": "Content submitted successfully. Use /scans/analyze to start scanning.",
            "submitted_at": scans_storage[scan_id]['submitted_at']
        }
        
    except Exception as e:
        logger.error(f"Content submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scans/upload", response_model=ScanSubmissionResponse)
async def upload_file(
    file: UploadFile = File(...),
    content_type: str = Query(default="attachment")
):
    """
    Upload file for credential scanning
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        
        # Save file
        file_path = UPLOAD_DIR / f"{scan_id}_{file.filename}"
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Extract text based on file type
        text_content = extract_text_from_file(file_path)
        
        # Store content
        content_storage[scan_id] = text_content
        
        # Store scan metadata
        scans_storage[scan_id] = {
            'scan_id': scan_id,
            'content_type': content_type,
            'filename': file.filename,
            'file_size': len(content),
            'metadata': {
                'filename': file.filename,
                'file_size': len(content),
                'file_path': str(file_path)
            },
            'submitted_at': datetime.now().isoformat(),
            'status': 'submitted',
            'result': None
        }
        
        logger.info(f"File uploaded: {scan_id} - {file.filename}")
        
        return {
            "scan_id": scan_id,
            "status": "submitted",
            "message": f"File '{file.filename}' uploaded successfully. Use /scans/analyze to start scanning.",
            "submitted_at": scans_storage[scan_id]['submitted_at']
        }
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def extract_text_from_file(file_path: Path) -> str:
    """Extract text from uploaded file"""
    suffix = file_path.suffix.lower()
    
    try:
        if suffix == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif suffix == '.pdf':
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif suffix in ['.doc', '.docx']:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        
        elif suffix in ['.html', '.htm']:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                return soup.get_text()
        
        else:
            # Try as plain text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        return f"[Error extracting text: {e}]"


@app.post("/scans/{scan_id}/analyze", response_model=ScanResult)
async def analyze_content(scan_id: str):
    """
    Start credential scanning analysis for submitted content
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Check if scan exists
    if scan_id not in scans_storage:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan_info = scans_storage[scan_id]
    
    # Check if already analyzed
    if scan_info['status'] == 'completed' and scan_info['result']:
        return scan_info['result']
    
    try:
        # Get content
        content = content_storage.get(scan_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Update status
        scan_info['status'] = 'analyzing'
        
        logger.info(f"Starting analysis: {scan_id}")
        
        # Run analysis
        result = agent.scan_content(
            scan_id=scan_id,
            content_text=content,
            content_type=scan_info['content_type'],
            metadata=scan_info.get('metadata', {})
        )
        
        # Store result
        scan_info['result'] = result
        scan_info['status'] = 'completed'
        scan_info['analyzed_at'] = datetime.now().isoformat()
        
        logger.info(f"Analysis complete: {scan_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        scan_info['status'] = 'failed'
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scans/{scan_id}", response_model=ScanResult)
async def get_scan_result(scan_id: str):
    """
    Get scan result by ID
    """
    if scan_id not in scans_storage:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan_info = scans_storage[scan_id]
    
    if scan_info['status'] != 'completed' or not scan_info['result']:
        raise HTTPException(
            status_code=400,
            detail=f"Scan not completed yet. Status: {scan_info['status']}"
        )
    
    return scan_info['result']


@app.get("/scans", response_model=List[ScanListItem])
async def list_scans(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    List all scans with pagination
    """
    # Sort by submission time (newest first)
    sorted_scans = sorted(
        scans_storage.values(),
        key=lambda x: x['submitted_at'],
        reverse=True
    )
    
    # Apply pagination
    paginated = sorted_scans[offset:offset + limit]
    
    # Format response
    result = []
    for scan in paginated:
        scan_summary = {
            'scan_id': scan['scan_id'],
            'content_type': scan['content_type'],
            'credentials_found': 0,
            'overall_risk': 'unknown',
            'submitted_at': scan['submitted_at'],
            'status': scan['status']
        }
        
        # Add summary if completed
        if scan['result']:
            scan_summary.update({
                'credentials_found': scan['result']['scan_summary']['credentials_found'],
                'overall_risk': scan['result']['scan_summary']['overall_risk']
            })
        
        result.append(scan_summary)
    
    return result


@app.delete("/scans/{scan_id}")
async def delete_scan(scan_id: str):
    """
    Delete scan and associated data
    """
    if scan_id not in scans_storage:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    try:
        # Delete content
        if scan_id in content_storage:
            del content_storage[scan_id]
        
        # Delete uploaded file if exists
        scan_info = scans_storage[scan_id]
        if 'metadata' in scan_info and 'file_path' in scan_info['metadata']:
            file_path = Path(scan_info['metadata']['file_path'])
            if file_path.exists():
                file_path.unlink()
        
        # Delete scan record
        del scans_storage[scan_id]
        
        logger.info(f"Scan deleted: {scan_id}")
        
        return {"message": "Scan deleted successfully", "scan_id": scan_id}
        
    except Exception as e:
        logger.error(f"Scan deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflow/graph", response_model=WorkflowGraph)
async def get_workflow_graph():
    """
    Get workflow structure for visualization
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        graph = agent.get_workflow_graph()
        return graph
    except Exception as e:
        logger.error(f"Failed to get workflow graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """
    Get overall statistics
    """
    total_scans = len(scans_storage)
    completed = sum(1 for s in scans_storage.values() if s['status'] == 'completed')
    analyzing = sum(1 for s in scans_storage.values() if s['status'] == 'analyzing')
    
    # Count risk levels
    high_risk = 0
    medium_risk = 0
    low_risk = 0
    total_credentials = 0
    
    for scan in scans_storage.values():
        if scan['result']:
            summary = scan['result']['scan_summary']
            high_risk += summary['high_risk']
            medium_risk += summary['medium_risk']
            low_risk += summary['low_risk']
            total_credentials += summary['credentials_found']
    
    return {
        "total_scans": total_scans,
        "completed_scans": completed,
        "analyzing_scans": analyzing,
        "total_credentials_found": total_credentials,
        "high_risk_findings": high_risk,
        "medium_risk_findings": medium_risk,
        "low_risk_findings": low_risk
    }


# ============================================================================
# Application Startup
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("=" * 60)
    logger.info("Creds Inspect API Server Starting")
    logger.info("=" * 60)
    logger.info(f"Agent Status: {'Ready' if agent else 'Failed'}")
    logger.info(f"CORS Origins: {cors_origins}")
    logger.info(f"Upload Directory: {UPLOAD_DIR}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Shutting down Creds Inspect API Server...")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "creds_inspect_api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
