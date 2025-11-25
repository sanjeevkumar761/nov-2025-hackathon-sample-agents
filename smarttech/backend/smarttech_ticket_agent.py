"""
SmartTech AI-Enabled TSD Ticket Classification Agent

This LangGraph agent uses LLM-based intent detection to classify TSD tickets
and recommend self-service solutions, reducing helpdesk load.

Key Features:
- Intent detection using Azure OpenAI
- Self-service opportunity identification
- Ticket routing recommendations
- Knowledge base article suggestions
"""

import os
import json
from typing import Optional, Dict, List, TypedDict, Annotated
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()


# Mock Data: TSD Tickets
MOCK_TSD_TICKETS = [
    {
        "ticket_id": "TSD-2024-001",
        "subject": "Cannot access email on mobile device",
        "description": "I'm trying to set up my work email on my iPhone but keep getting an authentication error. I've tried my password multiple times.",
        "category": "Email",
        "priority": "Medium",
        "user": "john.smith@smarttech.com",
        "created_at": "2024-11-20 09:15:00"
    },
    {
        "ticket_id": "TSD-2024-002",
        "subject": "Forgot VPN password",
        "description": "I forgot my VPN password and need to reset it. How can I do this?",
        "category": "VPN",
        "priority": "High",
        "user": "sarah.johnson@smarttech.com",
        "created_at": "2024-11-20 10:30:00"
    },
    {
        "ticket_id": "TSD-2024-003",
        "subject": "Printer not working",
        "description": "The printer on floor 3 is showing 'paper jam' error but I can't see any jammed paper. Need help urgently.",
        "category": "Hardware",
        "priority": "Medium",
        "user": "mike.brown@smarttech.com",
        "created_at": "2024-11-20 11:00:00"
    },
    {
        "ticket_id": "TSD-2024-004",
        "subject": "Password reset request",
        "description": "My password expired and I need to reset it. The system says my new password doesn't meet requirements but I don't know what they are.",
        "category": "Account",
        "priority": "High",
        "user": "emily.davis@smarttech.com",
        "created_at": "2024-11-20 11:45:00"
    },
    {
        "ticket_id": "TSD-2024-005",
        "subject": "Software installation - Adobe Acrobat",
        "description": "I need Adobe Acrobat Pro installed on my laptop for reviewing contracts. How do I request this?",
        "category": "Software",
        "priority": "Low",
        "user": "david.wilson@smarttech.com",
        "created_at": "2024-11-20 13:20:00"
    },
    {
        "ticket_id": "TSD-2024-006",
        "subject": "Laptop running very slow",
        "description": "My laptop has been extremely slow for the past week. It takes 10 minutes to start up and applications freeze constantly.",
        "category": "Performance",
        "priority": "Medium",
        "user": "lisa.anderson@smarttech.com",
        "created_at": "2024-11-20 14:00:00"
    },
    {
        "ticket_id": "TSD-2024-007",
        "subject": "Cannot connect to WiFi",
        "description": "I can't connect to the company WiFi network in the conference room. Other people seem to be connected fine.",
        "category": "Network",
        "priority": "Medium",
        "user": "robert.thomas@smarttech.com",
        "created_at": "2024-11-20 14:30:00"
    },
    {
        "ticket_id": "TSD-2024-008",
        "subject": "Need access to shared drive",
        "description": "I need access to the Finance shared drive. My manager approved it last week but I still can't access it.",
        "category": "Access",
        "priority": "Medium",
        "user": "jennifer.martinez@smarttech.com",
        "created_at": "2024-11-20 15:00:00"
    },
    {
        "ticket_id": "TSD-2024-009",
        "subject": "Outlook keeps crashing",
        "description": "My Outlook crashes every time I try to open attachments. This is impacting my work significantly.",
        "category": "Software",
        "priority": "High",
        "user": "william.garcia@smarttech.com",
        "created_at": "2024-11-20 15:30:00"
    },
    {
        "ticket_id": "TSD-2024-010",
        "subject": "How to setup multi-factor authentication",
        "description": "I received an email saying I need to set up MFA but I don't know how to do it. Is there a guide?",
        "category": "Security",
        "priority": "Medium",
        "user": "amanda.rodriguez@smarttech.com",
        "created_at": "2024-11-20 16:00:00"
    }
]

# Mock Data: Self-Service Knowledge Base
KNOWLEDGE_BASE = {
    "password_reset": {
        "title": "How to Reset Your Password",
        "article_id": "KB-001",
        "steps": [
            "Go to portal.smarttech.com/reset",
            "Enter your employee ID",
            "Verify your identity using your mobile phone",
            "Create a new password (min 12 chars, uppercase, lowercase, number, special char)",
            "Confirm the new password"
        ],
        "avg_resolution_time": "5 minutes",
        "success_rate": 95
    },
    "vpn_setup": {
        "title": "VPN Setup and Password Reset",
        "article_id": "KB-002",
        "steps": [
            "Download Cisco AnyConnect from portal.smarttech.com/vpn",
            "For password reset, visit portal.smarttech.com/vpn-reset",
            "Enter credentials: username is your email, password is your network password",
            "If forgotten, use 'Forgot Password' link to reset via email"
        ],
        "avg_resolution_time": "10 minutes",
        "success_rate": 90
    },
    "email_mobile": {
        "title": "Configure Email on Mobile Devices",
        "article_id": "KB-003",
        "steps": [
            "On iOS: Settings > Mail > Add Account > Exchange",
            "Email: your.email@smarttech.com",
            "Server: outlook.office365.com",
            "Domain: leave blank",
            "Username: your.email@smarttech.com",
            "Password: your network password (not app password)"
        ],
        "avg_resolution_time": "8 minutes",
        "success_rate": 88
    },
    "wifi_troubleshooting": {
        "title": "WiFi Connection Troubleshooting",
        "article_id": "KB-004",
        "steps": [
            "Forget the network and reconnect",
            "Ensure you're connecting to 'SmartTech-Secure' not 'SmartTech-Guest'",
            "Enter credentials: username (without @smarttech.com), network password",
            "If still failing, restart your device",
            "Contact IT if issues persist after restart"
        ],
        "avg_resolution_time": "7 minutes",
        "success_rate": 85
    },
    "software_installation": {
        "title": "Software Installation Request Process",
        "article_id": "KB-005",
        "steps": [
            "Visit portal.smarttech.com/software",
            "Browse available software catalog",
            "Click 'Request Software' for your desired application",
            "Provide business justification",
            "Manager approval required for licensed software",
            "Installation typically completed within 24 hours"
        ],
        "avg_resolution_time": "24 hours",
        "success_rate": 92
    },
    "mfa_setup": {
        "title": "Multi-Factor Authentication Setup",
        "article_id": "KB-006",
        "steps": [
            "Visit portal.smarttech.com/mfa",
            "Click 'Set up MFA'",
            "Download Microsoft Authenticator app on your phone",
            "Scan the QR code displayed on screen",
            "Enter the 6-digit code from the app to verify",
            "Save backup codes in a secure location"
        ],
        "avg_resolution_time": "10 minutes",
        "success_rate": 93
    },
    "performance_issues": {
        "title": "Computer Performance Troubleshooting",
        "article_id": "KB-007",
        "steps": [
            "Restart your computer",
            "Check for Windows updates and install pending updates",
            "Run disk cleanup: search 'Disk Cleanup' in Windows",
            "Check if antivirus is running a scan (wait for completion)",
            "Close unnecessary background applications",
            "If issues persist, submit ticket for hardware assessment"
        ],
        "avg_resolution_time": "15 minutes",
        "success_rate": 70
    },
    "access_request": {
        "title": "Shared Drive Access Request",
        "article_id": "KB-008",
        "steps": [
            "Visit portal.smarttech.com/access",
            "Select 'Shared Drive Access'",
            "Choose the drive you need access to",
            "Provide manager's email for approval",
            "Access granted within 2 business hours after approval"
        ],
        "avg_resolution_time": "2 hours",
        "success_rate": 95
    }
}

# Intent categories and their mappings
INTENT_CATEGORIES = {
    "password_reset": ["password", "reset", "expired", "forgot password", "password requirements"],
    "vpn_issues": ["vpn", "remote access", "vpn password", "vpn connection"],
    "email_setup": ["email", "mobile email", "phone email", "iphone", "android", "email setup"],
    "network_connectivity": ["wifi", "internet", "network", "connection", "cannot connect"],
    "software_request": ["software", "installation", "install", "application", "program"],
    "mfa_setup": ["mfa", "multi-factor", "authentication", "2fa", "two-factor"],
    "performance": ["slow", "freeze", "crash", "performance", "not responding"],
    "access_request": ["access", "shared drive", "permission", "folder access"],
    "hardware": ["printer", "hardware", "device", "equipment"],
    "outlook_issues": ["outlook", "email client", "attachment"]
}


# Define the agent state
class TicketState(TypedDict):
    """State of the ticket classification workflow"""
    ticket: Dict
    intent: Optional[str]
    confidence: float
    self_service_eligible: bool
    knowledge_base_articles: List[Dict]
    routing_recommendation: str
    analysis: str
    messages: Annotated[List, "The messages in the conversation"]
    execution_trace: List[Dict]  # Tracks workflow execution steps


class SmartTechTicketAgent:
    """
    AI-Enabled TSD Ticket Classification Agent for SmartTech
    
    Uses LangGraph workflow to:
    1. Analyze ticket content
    2. Detect user intent using LLM
    3. Determine self-service eligibility
    4. Recommend knowledge base articles
    5. Provide routing recommendations
    """
    
    def __init__(self, prompt_template_path: Optional[str] = None):
        self.llm = None
        self.workflow = None
        self.memory = MemorySaver()
        self.jinja_env = None
        self.prompt_template_path = prompt_template_path or "prompts/intent_detection.j2"
        self._initialize_jinja()
        self._initialize_llm()
        self._build_workflow()
    
    def _initialize_jinja(self):
        """Initialize Jinja2 template environment"""
        try:
            # Get the directory containing the prompts
            base_dir = Path(__file__).parent
            prompts_dir = base_dir / "prompts"
            
            # Create prompts directory if it doesn't exist
            prompts_dir.mkdir(exist_ok=True)
            
            # Initialize Jinja2 environment
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(prompts_dir)),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            print("✓ Jinja2 template engine initialized")
            
        except Exception as e:
            print(f"✗ Failed to initialize Jinja2: {e}")
            raise
    
    def _initialize_llm(self):
        """Initialize Azure OpenAI client"""
        try:
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
            
            if not endpoint or not deployment_name or not api_key:
                raise ValueError("Missing Azure OpenAI configuration")
            
            self.llm = AzureChatOpenAI(
                azure_endpoint=endpoint,
                azure_deployment=deployment_name,
                api_key=api_key,
                api_version=api_version,
                temperature=0.3  # Lower temperature for more consistent classification
            )
            
            print("✓ Azure OpenAI client initialized")
            
        except Exception as e:
            print(f"✗ Failed to initialize Azure OpenAI: {e}")
            raise
    
    def _build_workflow(self):
        """Build the LangGraph workflow for ticket classification"""
        
        # Create the state graph
        workflow = StateGraph(TicketState)
        
        # Add nodes for each step
        workflow.add_node("analyze_intent", self._analyze_intent)
        workflow.add_node("check_self_service", self._check_self_service_eligibility)
        workflow.add_node("find_kb_articles", self._find_knowledge_base_articles)
        workflow.add_node("recommend_routing", self._recommend_routing)
        
        # Define the workflow edges
        workflow.set_entry_point("analyze_intent")
        workflow.add_edge("analyze_intent", "check_self_service")
        workflow.add_edge("check_self_service", "find_kb_articles")
        workflow.add_edge("find_kb_articles", "recommend_routing")
        workflow.add_edge("recommend_routing", END)
        
        # Compile the workflow
        self.workflow = workflow.compile(checkpointer=self.memory)
        
        print("✓ LangGraph workflow compiled")
    
    def get_workflow_graph(self) -> Dict:
        """
        Get the workflow graph structure as a dictionary
        
        Returns:
            Dictionary containing nodes and edges information
        """
        nodes = [
            {
                "id": "START",
                "label": "Start",
                "type": "entry",
                "description": "Workflow entry point"
            },
            {
                "id": "analyze_intent",
                "label": "Analyze Intent",
                "type": "node",
                "description": "Detect user intent using Azure OpenAI LLM"
            },
            {
                "id": "check_self_service",
                "label": "Check Self-Service Eligibility",
                "type": "node",
                "description": "Determine if ticket can be resolved via self-service"
            },
            {
                "id": "find_kb_articles",
                "label": "Find KB Articles",
                "type": "node",
                "description": "Search knowledge base for relevant articles"
            },
            {
                "id": "recommend_routing",
                "label": "Recommend Routing",
                "type": "node",
                "description": "Determine optimal ticket routing destination"
            },
            {
                "id": "END",
                "label": "End",
                "type": "exit",
                "description": "Workflow completion"
            }
        ]
        
        edges = [
            {
                "from": "START",
                "to": "analyze_intent",
                "label": "entry_point"
            },
            {
                "from": "analyze_intent",
                "to": "check_self_service",
                "label": "next"
            },
            {
                "from": "check_self_service",
                "to": "find_kb_articles",
                "label": "next"
            },
            {
                "from": "find_kb_articles",
                "to": "recommend_routing",
                "label": "next"
            },
            {
                "from": "recommend_routing",
                "to": "END",
                "label": "finish"
            }
        ]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "workflow_type": "sequential",
            "total_nodes": len([n for n in nodes if n["type"] == "node"]),
            "total_edges": len(edges)
        }
    
    def visualize_workflow(self, output_path: str = "workflow_diagram.png") -> str:
        """
        Generate a visual diagram of the workflow graph
        
        Args:
            output_path: Path to save the diagram image
            
        Returns:
            Path to the generated image file
        """
        try:
            from io import BytesIO
            from PIL import Image
            
            # Get the workflow graph as PNG bytes
            graph_image = self.workflow.get_graph().draw_mermaid_png()
            
            # Convert bytes to PIL Image and save
            image = Image.open(BytesIO(graph_image))
            image.save(output_path)
            
            print(f"✓ Workflow diagram saved to {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Failed to generate workflow diagram: {e}")
            print("  Note: Ensure graphviz is installed on your system")
            return None
    
    def get_workflow_mermaid(self) -> str:
        """
        Get the workflow as Mermaid diagram syntax
        
        Returns:
            Mermaid diagram as string
        """
        try:
            return self.workflow.get_graph().draw_mermaid()
        except Exception as e:
            print(f"✗ Failed to generate Mermaid diagram: {e}")
            return None
    
    def _analyze_intent(self, state: TicketState) -> TicketState:
        """
        Node 1: Analyze the ticket to detect user intent using LLM
        """
        import time
        start_time = time.time()
        
        # Add trace entry
        trace_entry = {
            "step": 1,
            "node": "analyze_intent",
            "action": "Analyzing ticket intent using Azure OpenAI",
            "timestamp": datetime.now().isoformat(),
            "details": {}
        }
        
        ticket = state["ticket"]
        
        # Define intent categories with descriptions
        intent_categories = {
            "password_reset": "Password-related issues or reset requests",
            "vpn_issues": "VPN connection or access problems",
            "email_setup": "Email configuration on devices",
            "network_connectivity": "WiFi or network connection issues",
            "software_request": "Software installation or licensing requests",
            "mfa_setup": "Multi-factor authentication setup",
            "performance": "Computer performance or speed issues",
            "access_request": "Requesting access to drives, folders, or systems",
            "hardware": "Printer, device, or equipment issues",
            "outlook_issues": "Outlook application problems",
            "other": "Does not fit the above categories"
        }
        
        # Render prompt from Jinja2 template
        try:
            template = self.jinja_env.get_template(Path(self.prompt_template_path).name)
            prompt = template.render(
                company_name="SmartTech",
                ticket=ticket,
                intent_categories=intent_categories
            )
        except Exception as e:
            print(f"  ⚠ Failed to load template, using fallback prompt: {e}")
            # Fallback to inline prompt if template fails
            prompt = f"""You are an expert IT support ticket classifier for SmartTech.

Analyze the following support ticket and determine the user's primary intent.

Ticket Details:
- ID: {ticket['ticket_id']}
- Subject: {ticket['subject']}
- Description: {ticket['description']}
- Category: {ticket['category']}

Available Intent Categories:
- password_reset: Password-related issues or reset requests
- vpn_issues: VPN connection or access problems
- email_setup: Email configuration on devices
- network_connectivity: WiFi or network connection issues
- software_request: Software installation or licensing requests
- mfa_setup: Multi-factor authentication setup
- performance: Computer performance or speed issues
- access_request: Requesting access to drives, folders, or systems
- hardware: Printer, device, or equipment issues
- outlook_issues: Outlook application problems
- other: Does not fit the above categories

Respond with ONLY a JSON object in this exact format:
{{
    "intent": "intent_category_name",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this intent was chosen"
}}"""
        
        try:
            # Get LLM response
            messages = [HumanMessage(content=prompt)]
            trace_entry["details"]["llm_call"] = {
                "model": "Azure OpenAI",
                "prompt_length": len(prompt),
                "messages_sent": 1
            }
            response = self.llm.invoke(messages)
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                intent = result.get("intent", "other")
                confidence = result.get("confidence", 0.5)
                reasoning = result.get("reasoning", "")
            else:
                intent = "other"
                confidence = 0.5
                reasoning = "Could not parse LLM response"
            
            state["intent"] = intent
            state["confidence"] = confidence
            state["analysis"] = reasoning
            state["messages"] = [{"role": "assistant", "content": f"Intent detected: {intent} (confidence: {confidence:.0%})"}]
            
            # Complete trace entry
            trace_entry["details"]["result"] = {
                "intent": intent,
                "confidence": confidence,
                "reasoning": reasoning
            }
            trace_entry["duration_ms"] = int((time.time() - start_time) * 1000)
            trace_entry["status"] = "success"
            
            print(f"  → Intent: {intent} (confidence: {confidence:.0%})")
            
        except Exception as e:
            print(f"  ✗ Error analyzing intent: {e}")
            state["intent"] = "other"
            state["confidence"] = 0.0
            state["analysis"] = f"Error: {str(e)}"
            state["messages"] = [{"role": "assistant", "content": "Error analyzing intent"}]
            
            trace_entry["status"] = "error"
            trace_entry["error"] = str(e)
            trace_entry["duration_ms"] = int((time.time() - start_time) * 1000)
        
        # Append trace entry
        if "execution_trace" not in state:
            state["execution_trace"] = []
        state["execution_trace"].append(trace_entry)
        
        return state
    
    def _check_self_service_eligibility(self, state: TicketState) -> TicketState:
        """
        Node 2: Determine if ticket can be resolved via self-service
        """
        import time
        start_time = time.time()
        
        trace_entry = {
            "step": 2,
            "node": "check_self_service_eligibility",
            "action": "Evaluating self-service eligibility",
            "timestamp": datetime.now().isoformat(),
            "details": {}
        }
        
        intent = state["intent"]
        confidence = state["confidence"]
        
        # Define self-service eligible intents with confidence thresholds
        self_service_intents = {
            "password_reset": 0.7,
            "vpn_issues": 0.7,
            "email_setup": 0.75,
            "network_connectivity": 0.7,
            "software_request": 0.8,
            "mfa_setup": 0.75,
            "performance": 0.6,
            "access_request": 0.75
        }
        
        # Check if intent is self-service eligible and meets confidence threshold
        if intent in self_service_intents and confidence >= self_service_intents[intent]:
            state["self_service_eligible"] = True
            eligible = True
            reason = f"Intent '{intent}' is eligible with confidence {confidence:.0%} (threshold: {self_service_intents[intent]:.0%})"
            print(f"  → Self-service eligible: YES")
        else:
            state["self_service_eligible"] = False
            eligible = False
            reason = f"Intent '{intent}' not eligible or confidence too low" if intent in self_service_intents else "Intent requires helpdesk"
            print(f"  → Self-service eligible: NO (low confidence or requires helpdesk)")
        
        trace_entry["details"] = {
            "intent": intent,
            "confidence": confidence,
            "eligible": eligible,
            "reason": reason,
            "threshold_checked": self_service_intents.get(intent)
        }
        trace_entry["duration_ms"] = int((time.time() - start_time) * 1000)
        trace_entry["status"] = "success"
        
        if "execution_trace" not in state:
            state["execution_trace"] = []
        state["execution_trace"].append(trace_entry)
        
        return state
    
    def _find_knowledge_base_articles(self, state: TicketState) -> TicketState:
        """
        Node 3: Find relevant knowledge base articles
        """
        import time
        start_time = time.time()
        
        trace_entry = {
            "step": 3,
            "node": "find_knowledge_base_articles",
            "action": "Searching knowledge base for relevant articles",
            "timestamp": datetime.now().isoformat(),
            "details": {}
        }
        
        intent = state["intent"]
        
        # Map intents to knowledge base articles
        intent_to_kb = {
            "password_reset": ["password_reset"],
            "vpn_issues": ["vpn_setup"],
            "email_setup": ["email_mobile"],
            "network_connectivity": ["wifi_troubleshooting"],
            "software_request": ["software_installation"],
            "mfa_setup": ["mfa_setup"],
            "performance": ["performance_issues"],
            "access_request": ["access_request"],
            "outlook_issues": ["email_mobile"]
        }
        
        articles = []
        kb_keys = intent_to_kb.get(intent, [])
        
        for kb_key in kb_keys:
            if kb_key in KNOWLEDGE_BASE:
                kb_article = KNOWLEDGE_BASE[kb_key]
                articles.append({
                    "article_id": kb_article["article_id"],
                    "title": kb_article["title"],
                    "avg_resolution_time": kb_article["avg_resolution_time"],
                    "success_rate": kb_article["success_rate"],
                    "steps_count": len(kb_article["steps"])
                })
        
        state["knowledge_base_articles"] = articles
        
        if articles:
            print(f"  → Found {len(articles)} KB article(s)")
        else:
            print(f"  → No KB articles found")
        
        trace_entry["details"] = {
            "intent": intent,
            "kb_keys_searched": kb_keys,
            "articles_found": len(articles),
            "article_ids": [a["article_id"] for a in articles]
        }
        trace_entry["duration_ms"] = int((time.time() - start_time) * 1000)
        trace_entry["status"] = "success"
        
        if "execution_trace" not in state:
            state["execution_trace"] = []
        state["execution_trace"].append(trace_entry)
        
        return state
    
    def _recommend_routing(self, state: TicketState) -> TicketState:
        """
        Node 4: Recommend routing based on analysis
        """
        import time
        start_time = time.time()
        
        trace_entry = {
            "step": 4,
            "node": "recommend_routing",
            "action": "Determining optimal ticket routing",
            "timestamp": datetime.now().isoformat(),
            "details": {}
        }
        
        if state["self_service_eligible"] and state["knowledge_base_articles"]:
            routing = "SELF_SERVICE"
            recommendation = f"Route to Self-Service Portal - User can resolve independently"
        elif state["confidence"] >= 0.8:
            routing = "TIER_1_HELPDESK"
            recommendation = f"Route to Tier 1 Helpdesk - Standard support needed"
        elif state["confidence"] >= 0.5:
            routing = "TIER_2_HELPDESK"
            recommendation = f"Route to Tier 2 Helpdesk - Specialized support may be needed"
        else:
            routing = "MANUAL_REVIEW"
            recommendation = f"Manual Review Required - Intent unclear"
        
        state["routing_recommendation"] = routing
        
        print(f"  → Routing: {routing}")
        
        trace_entry["details"] = {
            "routing": routing,
            "recommendation": recommendation,
            "self_service_eligible": state["self_service_eligible"],
            "confidence": state["confidence"],
            "kb_articles_available": len(state["knowledge_base_articles"])
        }
        trace_entry["duration_ms"] = int((time.time() - start_time) * 1000)
        trace_entry["status"] = "success"
        
        if "execution_trace" not in state:
            state["execution_trace"] = []
        state["execution_trace"].append(trace_entry)
        
        return state
    
    def classify_ticket(self, ticket: Dict) -> Dict:
        """
        Classify a ticket and provide recommendations
        
        Args:
            ticket: Dictionary containing ticket information
            
        Returns:
            Classification result with recommendations
        """
        print(f"\n{'='*60}")
        print(f"Processing Ticket: {ticket['ticket_id']}")
        print(f"{'='*60}")
        
        # Initialize state
        initial_state = {
            "ticket": ticket,
            "intent": None,
            "confidence": 0.0,
            "self_service_eligible": False,
            "knowledge_base_articles": [],
            "routing_recommendation": "",
            "analysis": "",
            "messages": [],
            "execution_trace": []
        }
        
        # Run the workflow
        try:
            config = {"configurable": {"thread_id": ticket["ticket_id"]}}
            result = self.workflow.invoke(initial_state, config)
            
            # Format the output
            classification_result = {
                "ticket_id": ticket["ticket_id"],
                "subject": ticket["subject"],
                "detected_intent": result["intent"],
                "confidence": result["confidence"],
                "self_service_eligible": result["self_service_eligible"],
                "routing": result["routing_recommendation"],
                "knowledge_base_articles": result["knowledge_base_articles"],
                "analysis": result["analysis"],
                "execution_trace": result.get("execution_trace", [])
            }
            
            return classification_result
            
        except Exception as e:
            print(f"✗ Error processing ticket: {e}")
            return {
                "ticket_id": ticket["ticket_id"],
                "error": str(e)
            }
    
    def batch_classify_tickets(self, tickets: List[Dict]) -> List[Dict]:
        """
        Classify multiple tickets
        
        Args:
            tickets: List of ticket dictionaries
            
        Returns:
            List of classification results
        """
        results = []
        
        for ticket in tickets:
            result = self.classify_ticket(ticket)
            results.append(result)
        
        return results
    
    def print_classification_report(self, result: Dict):
        """Print a formatted classification report"""
        print(f"\n{'='*60}")
        print(f"CLASSIFICATION REPORT")
        print(f"{'='*60}")
        print(f"Ticket ID:     {result['ticket_id']}")
        print(f"Subject:       {result['subject']}")
        print(f"Intent:        {result['detected_intent']}")
        print(f"Confidence:    {result['confidence']:.0%}")
        print(f"Self-Service:  {'✓ YES' if result['self_service_eligible'] else '✗ NO'}")
        print(f"Routing:       {result['routing']}")
        
        if result.get('knowledge_base_articles'):
            print(f"\nRecommended KB Articles:")
            for article in result['knowledge_base_articles']:
                print(f"  • {article['article_id']}: {article['title']}")
                print(f"    Success Rate: {article['success_rate']}% | Avg Time: {article['avg_resolution_time']}")
        
        print(f"\nAnalysis: {result['analysis']}")
        print(f"{'='*60}")
    
    def generate_summary_statistics(self, results: List[Dict]) -> Dict:
        """Generate summary statistics from batch classification"""
        total = len(results)
        self_service_count = sum(1 for r in results if r.get('self_service_eligible', False))
        
        routing_stats = {}
        intent_stats = {}
        
        for result in results:
            # Count routing recommendations
            routing = result.get('routing', 'UNKNOWN')
            routing_stats[routing] = routing_stats.get(routing, 0) + 1
            
            # Count intents
            intent = result.get('detected_intent', 'unknown')
            intent_stats[intent] = intent_stats.get(intent, 0) + 1
        
        avg_confidence = sum(r.get('confidence', 0) for r in results) / total if total > 0 else 0
        
        return {
            "total_tickets": total,
            "self_service_eligible": self_service_count,
            "self_service_percentage": (self_service_count / total * 100) if total > 0 else 0,
            "average_confidence": avg_confidence,
            "routing_distribution": routing_stats,
            "intent_distribution": intent_stats
        }


# Helper functions for tools
@tool
def get_ticket_by_id(ticket_id: str) -> str:
    """Get ticket details by ticket ID"""
    for ticket in MOCK_TSD_TICKETS:
        if ticket["ticket_id"] == ticket_id:
            return json.dumps(ticket, indent=2)
    return f"Ticket {ticket_id} not found"


@tool
def get_knowledge_base_article(article_id: str) -> str:
    """Get knowledge base article details"""
    for kb_key, article in KNOWLEDGE_BASE.items():
        if article["article_id"] == article_id:
            return json.dumps(article, indent=2)
    return f"Article {article_id} not found"


@tool
def search_tickets(query: str) -> str:
    """Search tickets by keyword in subject or description"""
    matches = []
    query_lower = query.lower()
    
    for ticket in MOCK_TSD_TICKETS:
        if (query_lower in ticket["subject"].lower() or 
            query_lower in ticket["description"].lower()):
            matches.append({
                "ticket_id": ticket["ticket_id"],
                "subject": ticket["subject"]
            })
    
    return json.dumps(matches, indent=2) if matches else "No matching tickets found"


# Main execution
if __name__ == "__main__":
    print("\n" + "="*60)
    print("SmartTech AI-Enabled TSD Ticket Classification System")
    print("="*60)
    
    # Initialize the agent
    agent = SmartTechTicketAgent()
    
    # Process all mock tickets
    print("\n\nProcessing all TSD tickets...\n")
    results = agent.batch_classify_tickets(MOCK_TSD_TICKETS)
    
    # Print individual reports
    for result in results:
        agent.print_classification_report(result)
    
    # Generate and print summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    stats = agent.generate_summary_statistics(results)
    
    print(f"\nTotal Tickets Processed: {stats['total_tickets']}")
    print(f"Self-Service Eligible: {stats['self_service_eligible']} ({stats['self_service_percentage']:.1f}%)")
    print(f"Average Confidence: {stats['average_confidence']:.0%}")
    
    print(f"\nRouting Distribution:")
    for routing, count in stats['routing_distribution'].items():
        percentage = (count / stats['total_tickets'] * 100)
        print(f"  • {routing}: {count} ({percentage:.1f}%)")
    
    print(f"\nIntent Distribution:")
    for intent, count in sorted(stats['intent_distribution'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / stats['total_tickets'] * 100)
        print(f"  • {intent}: {count} ({percentage:.1f}%)")
    
    print("\n" + "="*60)
    print("✓ Analysis Complete")
    print("="*60)
    
    # Calculate potential helpdesk savings
    potential_savings = stats['self_service_eligible']
    print(f"\n💡 Insight: {potential_savings} tickets ({stats['self_service_percentage']:.1f}%) could be")
    print(f"   resolved through self-service, reducing helpdesk load significantly!")
    print("="*60 + "\n")
