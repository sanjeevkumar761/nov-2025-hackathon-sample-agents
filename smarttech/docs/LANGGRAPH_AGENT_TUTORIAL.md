# Building AI Agents with LangGraph: A Step-by-Step Tutorial

A comprehensive, hands-on tutorial for building production-ready AI agents using LangGraph, Azure OpenAI, and FastAPI.

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Architecture Overview](#architecture-overview)
4. [Part 1: Setting Up Your Environment](#part-1-setting-up-your-environment)
5. [Part 2: Creating Your First LangGraph Agent](#part-2-creating-your-first-langgraph-agent)
6. [Part 3: Building the Workflow](#part-3-building-the-workflow)
7. [Part 4: Adding State Management](#part-4-adding-state-management)
8. [Part 5: Implementing Workflow Nodes](#part-5-implementing-workflow-nodes)
9. [Part 6: Building the REST API](#part-6-building-the-rest-api)
10. [Part 7: Creating the UI](#part-7-creating-the-ui)
11. [Part 8: Advanced Features](#part-8-advanced-features)
12. [Part 9: Testing & Deployment](#part-9-testing--deployment)
13. [Best Practices](#best-practices)
14. [Troubleshooting](#troubleshooting)

---

## 📖 Introduction

### What You'll Build

In this tutorial, you'll build a **SmartTech TSD Agent** - an AI-powered support ticket classification system that:
- Automatically detects user intent from support tickets
- Determines if issues can be self-serviced
- Recommends relevant knowledge base articles
- Routes tickets to appropriate support teams
- Provides detailed execution traces for transparency

### What is LangGraph?

LangGraph is a library for building stateful, multi-actor applications with LLMs. It extends LangChain with:
- **State Management**: Track complex state across workflow steps
- **Graph-based Workflows**: Define nodes (actions) and edges (transitions)
- **Cyclic Graphs**: Support loops and conditional branching
- **Persistence**: Save and restore workflow state
- **Streaming**: Stream intermediate results in real-time

### Why LangGraph for Agents?

Traditional LLM applications are stateless - each call is independent. Agents need:
- **Memory**: Remember previous steps and decisions
- **Multi-step Reasoning**: Break complex tasks into subtasks
- **Tool Use**: Call external APIs and functions
- **Error Recovery**: Handle failures gracefully
- **Observability**: Track what the agent is doing

LangGraph provides all of this out-of-the-box.

---

## 🔧 Prerequisites

### Required Knowledge
- Python 3.9+ programming
- Basic understanding of REST APIs
- Familiarity with LLMs (ChatGPT, GPT-4)
- Basic React/TypeScript (for UI sections)

### Required Tools
```bash
# Python 3.9 or higher
python --version

# Node.js 18+ (for UI)
node --version

# Git
git --version

# VS Code (recommended) or your preferred IDE
```

### Azure OpenAI Setup
1. Create an Azure OpenAI resource
2. Deploy a GPT-4 model (e.g., `gpt-4` or `gpt-4-turbo`)
3. Note your:
   - Endpoint URL
   - API Key
   - Deployment name
   - API Version

---

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────┐
│                   React UI (Frontend)                │
│  - Ticket submission form                            │
│  - Results display                                   │
│  - Statistics dashboard                              │
│  - Workflow visualization                            │
└───────────────────┬─────────────────────────────────┘
                    │ HTTP/REST API
                    ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI (Backend API)                   │
│  - /api/v1/tickets/classify                         │
│  - /api/v1/stats                                    │
│  - /api/v1/workflow/graph                           │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│         SmartTech Agent (LangGraph Core)            │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  StateGraph Workflow                         │  │
│  │                                               │  │
│  │  ┌─────────────┐      ┌─────────────┐       │  │
│  │  │   Analyze   │──────▶│   Check     │       │  │
│  │  │   Intent    │      │ Self-Service│       │  │
│  │  └─────────────┘      └─────────────┘       │  │
│  │         │                     │              │  │
│  │         ▼                     ▼              │  │
│  │  ┌─────────────┐      ┌─────────────┐       │  │
│  │  │    Find     │──────▶│  Recommend  │       │  │
│  │  │ KB Articles │      │   Routing   │       │  │
│  │  └─────────────┘      └─────────────┘       │  │
│  └──────────────────────────────────────────────┘  │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│              Azure OpenAI (GPT-4)                   │
│  - Intent classification                            │
│  - Reasoning and analysis                           │
└─────────────────────────────────────────────────────┘
```

### Workflow Sequence

1. **User Input**: Submit support ticket via UI
2. **API Request**: Frontend calls `/api/v1/tickets/classify`
3. **Agent Initialization**: FastAPI triggers agent workflow
4. **State Creation**: Initial state with ticket data
5. **Node Execution**: Each node processes and updates state
6. **LLM Calls**: Nodes invoke Azure OpenAI as needed
7. **Result Compilation**: Final state converted to response
8. **API Response**: JSON result returned to frontend
9. **UI Display**: React components render results

---

## Part 1: Setting Up Your Environment

### Step 1.1: Create Project Structure

```bash
# Create project directory
mkdir smarttech-agent
cd smarttech-agent

# Create backend directory
mkdir backend
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate
```

### Step 1.2: Install Python Dependencies

```bash
# Create requirements.txt
cat > requirements.txt << EOF
# Core dependencies
langchain>=0.1.0
langgraph>=0.2.0
langchain-openai>=0.0.5

# API framework
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0

# Azure OpenAI
openai>=1.3.0

# Utilities
python-dotenv>=1.0.0
jinja2>=3.1.0

# Visualization (optional)
pygraphviz>=1.11
pillow>=10.0.0
EOF

# Install dependencies
pip install -r requirements.txt
```

### Step 1.3: Set Up Environment Variables

```bash
# Create .env file
cat > .env << EOF
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Application Configuration
LOG_LEVEL=INFO
APP_ENV=development
EOF

# IMPORTANT: Never commit .env to version control!
echo ".env" >> .gitignore
```

### Step 1.4: Verify Setup

Create a test script to verify your Azure OpenAI connection:

```python
# test_azure_openai.py
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

# Initialize LLM
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    temperature=0.3
)

# Test connection
response = llm.invoke([{"role": "user", "content": "Hello! This is a test."}])
print("✓ Azure OpenAI connection successful!")
print(f"Response: {response.content}")
```

Run the test:
```bash
python test_azure_openai.py
```

---

## Part 2: Creating Your First LangGraph Agent

### Step 2.1: Understanding State

In LangGraph, **state** is the data that flows through your workflow. Define it using TypedDict:

```python
# smarttech_agent.py
from typing import TypedDict, Dict, List, Optional, Any

class TicketState(TypedDict):
    """State schema for ticket classification workflow"""
    # Input
    ticket: Dict[str, Any]  # Original ticket data
    
    # Processing results
    detected_intent: Optional[str]  # User's intent
    confidence: Optional[float]  # Confidence score (0-1)
    self_service_eligible: Optional[bool]  # Can user self-solve?
    kb_articles: Optional[List[Dict[str, Any]]]  # Recommended articles
    routing: Optional[str]  # Where to route ticket
    analysis: Optional[str]  # Human-readable analysis
    
    # Metadata
    execution_trace: List[Dict[str, Any]]  # Execution history
```

**Key Concepts:**
- State persists across all workflow nodes
- Each node can read and modify state
- TypedDict provides type hints and validation
- Use Optional for fields populated during execution

### Step 2.2: Initialize the Agent Class

```python
import os
import logging
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

class SmartTechTicketAgent:
    """AI-powered ticket classification agent using LangGraph"""
    
    def __init__(self):
        """Initialize the agent with LLM and workflow"""
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
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            temperature=0.3,  # Lower = more deterministic
            max_tokens=1500
        )
        
        # Build the workflow graph
        self.logger.info("Building LangGraph workflow...")
        self.workflow = self._build_workflow()
        self.logger.info("✓ Agent initialized successfully")
    
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        # We'll implement this in the next section
        pass
```

### Step 2.3: Create Workflow Nodes

Nodes are functions that process state. Each node:
1. Receives current state
2. Performs some action (LLM call, computation, etc.)
3. Updates and returns state

```python
def _analyze_intent(self, state: TicketState) -> TicketState:
    """Node 1: Analyze the ticket to detect user intent"""
    self.logger.info("Node: Analyzing intent...")
    
    # Create prompt for intent detection
    prompt = f"""
You are an expert at analyzing IT support tickets.

Analyze this ticket and identify the user's primary intent:

Subject: {state['ticket']['subject']}
Description: {state['ticket']['description']}
Category: {state['ticket']['category']}

Classify into ONE of these intents:
- password_reset
- vpn_access
- software_installation
- hardware_issue
- email_problem
- network_connectivity
- account_access
- permission_request
- data_recovery
- other

Return ONLY a JSON object:
{{
    "intent": "detected_intent_here",
    "confidence": 0.95,
    "reasoning": "Brief explanation"
}}
"""
    
    try:
        # Call LLM
        response = self.llm.invoke([
            {"role": "system", "content": "You are an IT support intent classifier."},
            {"role": "user", "content": prompt}
        ])
        
        # Parse response (simplified - add error handling in production)
        import json
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        # Update state
        state['detected_intent'] = result['intent']
        state['confidence'] = result['confidence']
        
        self.logger.info(f"✓ Intent detected: {result['intent']} ({result['confidence']:.2f})")
        
    except Exception as e:
        self.logger.error(f"✗ Intent analysis failed: {e}")
        state['detected_intent'] = 'unknown'
        state['confidence'] = 0.0
    
    return state
```

---

## Part 3: Building the Workflow

### Step 3.1: Define the Graph Structure

```python
def _build_workflow(self):
    """Build the LangGraph workflow with nodes and edges"""
    
    # Create a StateGraph with our TicketState schema
    workflow = StateGraph(TicketState)
    
    # Add nodes (each node is a processing step)
    workflow.add_node("analyze_intent", self._analyze_intent)
    workflow.add_node("check_self_service", self._check_self_service)
    workflow.add_node("find_kb_articles", self._find_kb_articles)
    workflow.add_node("recommend_routing", self._recommend_routing)
    
    # Define edges (workflow flow)
    workflow.set_entry_point("analyze_intent")  # Start here
    workflow.add_edge("analyze_intent", "check_self_service")
    workflow.add_edge("check_self_service", "find_kb_articles")
    workflow.add_edge("find_kb_articles", "recommend_routing")
    workflow.add_edge("recommend_routing", END)  # Finish here
    
    # Compile the graph
    return workflow.compile()
```

**Graph Concepts:**
- **Nodes**: Processing units (your functions)
- **Edges**: Transitions between nodes
- **Entry Point**: Where execution starts
- **END**: Special marker for workflow completion
- **Compile**: Creates executable workflow

### Step 3.2: Visualize Your Workflow

```python
def get_workflow_graph(self) -> Dict[str, Any]:
    """Get workflow structure for visualization"""
    nodes = [
        {"id": "START", "label": "Start", "type": "entry"},
        {"id": "analyze_intent", "label": "Analyze Intent", "type": "node"},
        {"id": "check_self_service", "label": "Check Self-Service", "type": "node"},
        {"id": "find_kb_articles", "label": "Find KB Articles", "type": "node"},
        {"id": "recommend_routing", "label": "Recommend Routing", "type": "node"},
        {"id": "END", "label": "End", "type": "exit"}
    ]
    
    edges = [
        {"from": "START", "to": "analyze_intent", "label": "begin"},
        {"from": "analyze_intent", "to": "check_self_service", "label": "intent_detected"},
        {"from": "check_self_service", "to": "find_kb_articles", "label": "eligibility_checked"},
        {"from": "find_kb_articles", "to": "recommend_routing", "label": "articles_found"},
        {"from": "recommend_routing", "to": "END", "label": "complete"}
    ]
    
    return {"nodes": nodes, "edges": edges}
```

---

## Part 4: Adding State Management

### Step 4.1: Implement Execution Tracing

Add observability to track what your agent is doing:

```python
import time
from datetime import datetime

def _add_trace_step(self, state: TicketState, node: str, action: str, 
                    details: Dict[str, Any], duration_ms: int):
    """Add a step to the execution trace"""
    step = {
        'step': len(state['execution_trace']) + 1,
        'node': node,
        'action': action,
        'timestamp': datetime.now().isoformat(),
        'duration_ms': duration_ms,
        'status': 'completed',
        'details': details
    }
    state['execution_trace'].append(step)
```

### Step 4.2: Update Nodes with Tracing

```python
def _analyze_intent(self, state: TicketState) -> TicketState:
    """Node 1: Analyze intent with tracing"""
    start_time = time.time()
    self.logger.info("Node: Analyzing intent...")
    
    # ... existing intent analysis code ...
    
    # Add trace
    duration = int((time.time() - start_time) * 1000)
    self._add_trace_step(
        state, 
        node='analyze_intent',
        action='Detected user intent from ticket',
        details={
            'intent': state['detected_intent'],
            'confidence': state['confidence']
        },
        duration_ms=duration
    )
    
    return state
```

### Step 4.3: Initialize State Before Execution

```python
def classify_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point: classify a support ticket"""
    self.logger.info(f"Processing ticket: {ticket['ticket_id']}")
    
    # Initialize state
    initial_state = TicketState(
        ticket=ticket,
        detected_intent=None,
        confidence=None,
        self_service_eligible=None,
        kb_articles=None,
        routing=None,
        analysis=None,
        execution_trace=[]
    )
    
    # Execute workflow
    try:
        final_state = self.workflow.invoke(initial_state)
        
        # Format result
        result = {
            'ticket_id': ticket['ticket_id'],
            'subject': ticket['subject'],
            'detected_intent': final_state['detected_intent'],
            'confidence': final_state['confidence'],
            'self_service_eligible': final_state['self_service_eligible'],
            'kb_articles': final_state['kb_articles'],
            'routing': final_state['routing'],
            'analysis': final_state['analysis'],
            'execution_trace': final_state['execution_trace']
        }
        
        self.logger.info("✓ Classification complete")
        return result
        
    except Exception as e:
        self.logger.error(f"✗ Classification failed: {e}")
        raise
```

---

## Part 5: Implementing Workflow Nodes

### Step 5.1: Node 2 - Check Self-Service Eligibility

```python
def _check_self_service(self, state: TicketState) -> TicketState:
    """Node 2: Determine if issue can be self-serviced"""
    start_time = time.time()
    self.logger.info("Node: Checking self-service eligibility...")
    
    # Self-service rules
    self_service_intents = [
        'password_reset',
        'vpn_access',
        'software_installation',
        'email_problem'
    ]
    
    intent = state['detected_intent']
    confidence = state['confidence']
    
    # Simple rule-based check
    is_eligible = (
        intent in self_service_intents and 
        confidence >= 0.75 and
        state['ticket']['priority'] in ['Low', 'Medium']
    )
    
    state['self_service_eligible'] = is_eligible
    
    # Add trace
    duration = int((time.time() - start_time) * 1000)
    self._add_trace_step(
        state,
        node='check_self_service',
        action='Evaluated self-service eligibility',
        details={
            'eligible': is_eligible,
            'reason': f"Intent '{intent}' with {confidence:.2f} confidence"
        },
        duration_ms=duration
    )
    
    self.logger.info(f"✓ Self-service eligible: {is_eligible}")
    return state
```

### Step 5.2: Node 3 - Find Knowledge Base Articles

```python
# First, define your knowledge base
KNOWLEDGE_BASE = {
    "password_reset": {
        "article_id": "KB-001",
        "title": "How to Reset Your Password",
        "category": "password_reset",
        "avg_resolution_time": "5 minutes",
        "success_rate": 95,
        "steps": [
            "Go to https://portal.smarttech.com",
            "Click 'Forgot Password'",
            "Enter your email address",
            "Check email for reset link",
            "Follow link and create new password"
        ]
    },
    "vpn_access": {
        "article_id": "KB-002",
        "title": "VPN Connection Setup Guide",
        "category": "vpn_access",
        "avg_resolution_time": "10 minutes",
        "success_rate": 88,
        "steps": [
            "Download Cisco AnyConnect client",
            "Install the application",
            "Open AnyConnect",
            "Enter VPN address: vpn.smarttech.com",
            "Login with your credentials"
        ]
    },
    # Add more KB articles...
}

def _find_kb_articles(self, state: TicketState) -> TicketState:
    """Node 3: Find relevant KB articles"""
    start_time = time.time()
    self.logger.info("Node: Finding KB articles...")
    
    intent = state['detected_intent']
    articles = []
    
    # Simple keyword matching (use vector search in production)
    for kb_id, article in KNOWLEDGE_BASE.items():
        if article['category'] == intent:
            articles.append({
                'article_id': article['article_id'],
                'title': article['title'],
                'avg_resolution_time': article['avg_resolution_time'],
                'success_rate': article['success_rate'],
                'steps_count': len(article.get('steps', []))
            })
    
    # Sort by success rate
    articles.sort(key=lambda x: x['success_rate'], reverse=True)
    
    # Take top 3
    state['kb_articles'] = articles[:3]
    
    # Add trace
    duration = int((time.time() - start_time) * 1000)
    self._add_trace_step(
        state,
        node='find_kb_articles',
        action='Retrieved relevant knowledge base articles',
        details={
            'articles_found': len(articles),
            'top_article': articles[0]['title'] if articles else 'None'
        },
        duration_ms=duration
    )
    
    self.logger.info(f"✓ Found {len(articles)} KB articles")
    return state
```

### Step 5.3: Node 4 - Recommend Routing

```python
def _recommend_routing(self, state: TicketState) -> TicketState:
    """Node 4: Recommend where to route the ticket"""
    start_time = time.time()
    self.logger.info("Node: Recommending routing...")
    
    intent = state['detected_intent']
    priority = state['ticket']['priority']
    self_service = state['self_service_eligible']
    
    # Routing logic
    if priority == 'Critical':
        routing = 'URGENT_QUEUE'
        analysis = "Critical priority - immediate escalation required"
    elif self_service and len(state['kb_articles']) > 0:
        routing = 'SELF_SERVICE'
        analysis = f"User can resolve via KB article: {state['kb_articles'][0]['title']}"
    elif intent in ['hardware_issue', 'data_recovery']:
        routing = 'SPECIALIST_TEAM'
        analysis = "Requires specialized technical expertise"
    elif intent == 'permission_request':
        routing = 'SECURITY_TEAM'
        analysis = "Requires security team approval"
    else:
        routing = 'GENERAL_SUPPORT'
        analysis = "Route to general support queue"
    
    state['routing'] = routing
    state['analysis'] = analysis
    
    # Add trace
    duration = int((time.time() - start_time) * 1000)
    self._add_trace_step(
        state,
        node='recommend_routing',
        action='Determined optimal routing',
        details={
            'routing': routing,
            'reasoning': analysis
        },
        duration_ms=duration
    )
    
    self.logger.info(f"✓ Routing: {routing}")
    return state
```

---

## Part 6: Building the REST API

### Step 6.1: Create FastAPI Application

```python
# smarttech_api.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from smarttech_agent import SmartTechTicketAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="SmartTech TSD Agent API",
    description="AI-powered ticket classification system",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[SmartTechTicketAgent] = None

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global agent
    try:
        logger.info("Initializing agent...")
        agent = SmartTechTicketAgent()
        logger.info("✓ Agent ready")
    except Exception as e:
        logger.error(f"✗ Failed to initialize: {e}")
```

### Step 6.2: Define Request/Response Models

```python
class TicketRequest(BaseModel):
    """Request model for ticket classification"""
    ticket_id: str = Field(..., description="Unique ticket ID")
    subject: str = Field(..., description="Ticket subject", min_length=1)
    description: str = Field(..., description="Detailed description", min_length=1)
    category: str = Field(..., description="Ticket category")
    priority: str = Field(..., description="Priority (Low/Medium/High/Critical)")
    user: str = Field(..., description="User email")
    created_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "TSD-2024-001",
                "subject": "Cannot access VPN",
                "description": "I'm unable to connect to the company VPN from home.",
                "category": "Network",
                "priority": "High",
                "user": "john.doe@smarttech.com",
                "created_at": "2024-11-22 10:00:00"
            }
        }

class ClassificationResult(BaseModel):
    """Response model"""
    ticket_id: str
    subject: str
    detected_intent: str
    confidence: float
    self_service_eligible: bool
    routing: str
    kb_articles: List[Dict[str, Any]]
    analysis: str
    execution_trace: List[Dict[str, Any]]
    timestamp: str
```

### Step 6.3: Create Classification Endpoint

```python
@app.post("/api/v1/tickets/classify", response_model=ClassificationResult)
async def classify_ticket(ticket: TicketRequest):
    """
    Classify a support ticket
    
    Args:
        ticket: Ticket information
    
    Returns:
        Classification result with recommendations
    """
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized"
        )
    
    try:
        # Convert to dict
        ticket_dict = ticket.model_dump()
        if not ticket_dict.get("created_at"):
            ticket_dict["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Classify
        logger.info(f"Classifying ticket: {ticket.ticket_id}")
        result = agent.classify_ticket(ticket_dict)
        
        # Add timestamp
        result['timestamp'] = datetime.now().isoformat()
        
        return ClassificationResult(**result)
        
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

### Step 6.4: Add Health Check Endpoint

```python
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if agent is not None else "degraded",
        "agent_initialized": agent is not None,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### Step 6.5: Run the API Server

```python
# At the bottom of smarttech_api.py
if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("SmartTech TSD Agent API")
    print("="*60)
    print("\nStarting server...")
    print("Docs: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop")
    print("="*60 + "\n")
    
    uvicorn.run(
        "smarttech_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

Test it:
```bash
python smarttech_api.py
```

Visit http://localhost:8000/docs to see interactive API documentation!

---

## Part 7: Creating the UI

### Step 7.1: Set Up React Project

```bash
# In your project root (not backend/)
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install

# Install additional dependencies
npm install axios lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 7.2: Configure Tailwind CSS

```javascript
// tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.card {
  @apply bg-white/95 backdrop-blur-md rounded-2xl shadow-xl p-6 border border-white/20;
}
```

### Step 7.3: Create API Client

```typescript
// src/api.ts
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const smartTechApi = {
  async classifyTicket(ticket: any) {
    const response = await axios.post(
      `${API_BASE_URL}/tickets/classify`,
      ticket
    );
    return response.data;
  },

  async healthCheck() {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  },

  async getWorkflowGraph() {
    const response = await axios.get(`${API_BASE_URL}/workflow/graph`);
    return response.data;
  }
};
```

### Step 7.4: Create Ticket Form Component

```typescript
// src/components/TicketForm.tsx
import { useState } from 'react';
import { Send } from 'lucide-react';

interface TicketFormProps {
  onSubmit: (ticket: any) => void;
  loading: boolean;
}

const TicketForm = ({ onSubmit, loading }: TicketFormProps) => {
  const [formData, setFormData] = useState({
    subject: '',
    description: '',
    category: 'General',
    priority: 'Medium',
    user: 'user@smarttech.com'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const ticket = {
      ticket_id: `TSD-${Date.now()}`,
      ...formData,
      created_at: new Date().toISOString()
    };
    
    onSubmit(ticket);
  };

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
        Submit Support Ticket
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Subject
          </label>
          <input
            type="text"
            value={formData.subject}
            onChange={(e) => setFormData({...formData, subject: e.target.value})}
            className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            rows={4}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Category
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({...formData, category: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500"
            >
              <option>General</option>
              <option>Network</option>
              <option>Hardware</option>
              <option>Software</option>
              <option>Account</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Priority
            </label>
            <select
              value={formData.priority}
              onChange={(e) => setFormData({...formData, priority: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500"
            >
              <option>Low</option>
              <option>Medium</option>
              <option>High</option>
              <option>Critical</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold py-3 px-6 rounded-xl hover:shadow-lg transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Submit Ticket'}
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
};

export default TicketForm;
```

### Step 7.5: Create Results Display Component

```typescript
// src/components/ClassificationResults.tsx
import { CheckCircle, AlertCircle, BookOpen, ArrowRight } from 'lucide-react';

interface ResultsProps {
  result: any;
}

const ClassificationResults = ({ result }: ResultsProps) => {
  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
        Classification Results
      </h2>

      {/* Intent Detection */}
      <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-gray-600 mb-1">Detected Intent</p>
            <p className="text-2xl font-bold text-gray-900">
              {result.detected_intent.replace('_', ' ').toUpperCase()}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm font-semibold text-gray-600 mb-1">Confidence</p>
            <p className="text-2xl font-bold text-indigo-600">
              {(result.confidence * 100).toFixed(0)}%
            </p>
          </div>
        </div>
      </div>

      {/* Self-Service Status */}
      <div className={`mb-6 p-4 rounded-xl border-2 ${
        result.self_service_eligible 
          ? 'bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200'
          : 'bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200'
      }`}>
        <div className="flex items-center gap-3">
          {result.self_service_eligible ? (
            <CheckCircle className="w-6 h-6 text-emerald-600" />
          ) : (
            <AlertCircle className="w-6 h-6 text-orange-600" />
          )}
          <div>
            <p className="font-bold text-gray-900">
              {result.self_service_eligible ? 'Self-Service Available' : 'Support Required'}
            </p>
            <p className="text-sm text-gray-700">{result.analysis}</p>
          </div>
        </div>
      </div>

      {/* Routing */}
      <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border-2 border-purple-200">
        <div className="flex items-center gap-3">
          <ArrowRight className="w-6 h-6 text-purple-600" />
          <div>
            <p className="text-sm font-semibold text-gray-600">Recommended Routing</p>
            <p className="text-lg font-bold text-gray-900">{result.routing}</p>
          </div>
        </div>
      </div>

      {/* KB Articles */}
      {result.kb_articles && result.kb_articles.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <BookOpen className="w-5 h-5 text-indigo-600" />
            <h3 className="text-lg font-bold text-gray-900">Recommended Articles</h3>
          </div>
          
          <div className="space-y-3">
            {result.kb_articles.map((article: any) => (
              <div key={article.article_id} className="p-4 bg-gray-50 rounded-xl border border-gray-200 hover:shadow-md transition-shadow">
                <p className="font-bold text-gray-900">{article.title}</p>
                <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                  <span>⏱️ {article.avg_resolution_time}</span>
                  <span>✅ {article.success_rate}% success rate</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ClassificationResults;
```

### Step 7.6: Create Main App Component

```typescript
// src/App.tsx
import { useState, useEffect } from 'react';
import TicketForm from './components/TicketForm';
import ClassificationResults from './components/ClassificationResults';
import { smartTechApi } from './api';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const data = await smartTechApi.healthCheck();
      setHealth(data);
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const handleClassifyTicket = async (ticket: any) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await smartTechApi.classifyTicket(ticket);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Classification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8">
      <header className="max-w-7xl mx-auto mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">
          SmartTech TSD Agent
        </h1>
        <p className="text-white/80">
          AI-Powered Ticket Classification System
        </p>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <TicketForm onSubmit={handleClassifyTicket} loading={loading} />
        </div>

        <div>
          {error && (
            <div className="card bg-red-50 border-2 border-red-200 mb-4">
              <p className="text-red-700 font-semibold">{error}</p>
            </div>
          )}

          {result && <ClassificationResults result={result} />}
        </div>
      </main>
    </div>
  );
}

export default App;
```

### Step 7.7: Run the Frontend

```bash
npm run dev
```

Visit http://localhost:5173 to see your UI!

---

## Part 8: Advanced Features

### Step 8.1: Add Conditional Routing

Modify your workflow to handle different paths:

```python
def _build_workflow_with_conditions(self):
    """Build workflow with conditional branches"""
    workflow = StateGraph(TicketState)
    
    # Add nodes
    workflow.add_node("analyze_intent", self._analyze_intent)
    workflow.add_node("check_self_service", self._check_self_service)
    workflow.add_node("find_kb_articles", self._find_kb_articles)
    workflow.add_node("escalate_urgent", self._escalate_urgent)
    workflow.add_node("recommend_routing", self._recommend_routing)
    
    # Entry point
    workflow.set_entry_point("analyze_intent")
    
    # Conditional edge based on priority
    def should_escalate(state: TicketState) -> str:
        if state['ticket']['priority'] == 'Critical':
            return "escalate"
        return "check_service"
    
    workflow.add_conditional_edges(
        "analyze_intent",
        should_escalate,
        {
            "escalate": "escalate_urgent",
            "check_service": "check_self_service"
        }
    )
    
    workflow.add_edge("escalate_urgent", END)
    workflow.add_edge("check_self_service", "find_kb_articles")
    workflow.add_edge("find_kb_articles", "recommend_routing")
    workflow.add_edge("recommend_routing", END)
    
    return workflow.compile()
```

### Step 8.2: Add Human-in-the-Loop

```python
def _request_human_review(self, state: TicketState) -> TicketState:
    """Request human review for uncertain cases"""
    if state['confidence'] < 0.70:
        state['requires_human_review'] = True
        state['review_reason'] = "Low confidence in intent detection"
        
        # In production, trigger notification to human reviewer
        self.logger.warning(f"Human review requested: {state['review_reason']}")
    
    return state
```

### Step 8.3: Implement Streaming

```python
# Use LangGraph's streaming capabilities
async def classify_ticket_streaming(self, ticket: Dict[str, Any]):
    """Stream classification results as they're generated"""
    initial_state = TicketState(ticket=ticket, execution_trace=[])
    
    async for chunk in self.workflow.astream(initial_state):
        # Yield each node's output as it completes
        yield chunk
```

---

## Part 9: Testing & Deployment

### Step 9.1: Unit Tests

```python
# test_agent.py
import pytest
from smarttech_agent import SmartTechTicketAgent

@pytest.fixture
def agent():
    return SmartTechTicketAgent()

@pytest.fixture
def sample_ticket():
    return {
        "ticket_id": "TEST-001",
        "subject": "Cannot reset password",
        "description": "I forgot my password and need to reset it",
        "category": "Account",
        "priority": "High",
        "user": "test@smarttech.com",
        "created_at": "2024-11-22 10:00:00"
    }

def test_classify_ticket(agent, sample_ticket):
    """Test basic ticket classification"""
    result = agent.classify_ticket(sample_ticket)
    
    assert result['ticket_id'] == 'TEST-001'
    assert result['detected_intent'] == 'password_reset'
    assert result['confidence'] > 0.7
    assert result['self_service_eligible'] == True
    assert len(result['kb_articles']) > 0

def test_intent_detection(agent, sample_ticket):
    """Test intent detection node"""
    state = {'ticket': sample_ticket, 'execution_trace': []}
    result_state = agent._analyze_intent(state)
    
    assert 'detected_intent' in result_state
    assert 'confidence' in result_state
    assert result_state['confidence'] >= 0.0 and result_state['confidence'] <= 1.0
```

Run tests:
```bash
pytest test_agent.py -v
```

### Step 9.2: Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "smarttech_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION}
      - AZURE_OPENAI_DEPLOYMENT=${AZURE_OPENAI_DEPLOYMENT}
    env_file:
      - .env

  frontend:
    build:
      context: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

Deploy:
```bash
docker-compose up -d
```

---

## 📋 Best Practices

### 1. Error Handling

```python
def _analyze_intent(self, state: TicketState) -> TicketState:
    try:
        # Your logic
        pass
    except Exception as e:
        self.logger.error(f"Intent analysis failed: {e}")
        # Set fallback values
        state['detected_intent'] = 'unknown'
        state['confidence'] = 0.0
        # Add error to trace
        state['execution_trace'].append({
            'node': 'analyze_intent',
            'status': 'error',
            'error': str(e)
        })
    return state
```

### 2. Prompt Engineering

- Use structured output formats (JSON)
- Provide clear examples
- Set appropriate temperature (0.3 for classification, 0.7 for creative tasks)
- Include safety instructions
- Test with edge cases

### 3. State Management

- Keep state schema simple
- Use TypedDict for type safety
- Don't store large objects in state
- Clear sensitive data after processing

### 4. Performance

- Cache LLM responses when appropriate
- Use batch processing for multiple tickets
- Implement request throttling
- Monitor token usage
- Consider using cheaper models for simple tasks

### 5. Monitoring

```python
# Add metrics collection
from prometheus_client import Counter, Histogram

classification_counter = Counter('classifications_total', 'Total classifications')
classification_duration = Histogram('classification_duration_seconds', 'Classification duration')

@classification_duration.time()
def classify_ticket(self, ticket):
    classification_counter.inc()
    # Your classification logic
```

---

## 🔧 Troubleshooting

### Common Issues

**Issue: "Agent not initialized"**
```
Solution: Check Azure OpenAI credentials in .env file
Verify: python test_azure_openai.py
```

**Issue: "JSON parsing failed"**
```
Solution: Add robust JSON extraction:
content = response.content.strip()
if content.startswith("```json"):
    content = content.split("```json")[1].split("```")[0]
content = content.strip()
```

**Issue: "Low confidence scores"**
```
Solution:
1. Improve prompt with examples
2. Add few-shot learning
3. Use GPT-4 instead of GPT-3.5
4. Fine-tune model on your data
```

**Issue: "Slow response times"**
```
Solution:
1. Implement caching
2. Use parallel processing
3. Reduce max_tokens
4. Consider streaming
```

---

## 🎯 Next Steps

### Enhance Your Agent

1. **Add more intents** - Expand to 20+ ticket types
2. **Implement RAG** - Use vector search for KB articles
3. **Multi-agent system** - Create specialist sub-agents
4. **Add tools** - Let agent take actions (reset passwords, etc.)
5. **Fine-tuning** - Train on your actual ticket data
6. **Feedback loop** - Learn from user corrections
7. **A/B testing** - Compare different prompts/models
8. **Analytics dashboard** - Visualize agent performance

### Production Readiness

- [ ] Implement authentication and authorization
- [ ] Add rate limiting
- [ ] Set up monitoring and alerting
- [ ] Create comprehensive test suite
- [ ] Document API with OpenAPI
- [ ] Implement CI/CD pipeline
- [ ] Add database for persistence
- [ ] Set up logging aggregation
- [ ] Implement backup and disaster recovery
- [ ] Conduct security audit

---

## 📚 Additional Resources

### Documentation
- [LangGraph Docs](https://python.langchain.com/docs/langgraph)
- [LangChain Docs](https://python.langchain.com/)
- [Azure OpenAI Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

### Example Projects
- [LangGraph Examples Repo](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [Agent Architectures](https://www.anthropic.com/research/building-effective-agents)

### Community
- [LangChain Discord](https://discord.gg/langchain)
- [r/LangChain Reddit](https://reddit.com/r/LangChain)

---

## 🎉 Congratulations!

You've built a complete AI agent system with:
- ✅ LangGraph workflow orchestration
- ✅ Azure OpenAI integration
- ✅ REST API with FastAPI
- ✅ Modern React UI
- ✅ State management
- ✅ Execution tracing
- ✅ Error handling
- ✅ Production-ready architecture

**Keep building! 🚀**

---

*Tutorial Version: 1.0*
*Last Updated: November 22, 2025*
*Author: SmartTech AI Team*
