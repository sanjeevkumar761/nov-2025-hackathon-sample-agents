"""
ASR Data Enrichment Agent
==========================

AI-powered ServiceNow ticket enrichment agent using LangGraph.

Enhances incident tickets across 4 quality dimensions:
1. Short Description Quality (25%)
2. Long Description Quality (30%)
3. Categorization Accuracy (25%)
4. Resolution Detail Quality (20%)

Goal: Improve ticket quality from 2.6% to 95%+ meeting automation threshold.
"""

import os
import logging
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===========================
# State Definition
# ===========================

class ASREnrichmentState(TypedDict):
    """State for ticket enrichment workflow"""
    # Input
    task_id: str
    ticket_id: str
    operation: str  # 'analyze', 'enrich', 'validate'
    enrich_dimensions: List[str]  # ['short_desc', 'long_desc', 'categorization', 'resolution']
    auto_update_snow: bool
    
    # ServiceNow connection
    snow_instance: str
    snow_credentials: Dict[str, str]
    
    # Ticket data
    original_ticket: Optional[Dict[str, Any]]
    enriched_ticket: Optional[Dict[str, Any]]
    
    # Quality assessment
    quality_scores: Optional[Dict[str, Any]]
    before_score: Optional[float]
    after_score: Optional[float]
    deficiencies: Optional[List[str]]
    recommendations: Optional[List[str]]
    
    # Enrichment results
    changes_made: Optional[List[str]]
    enrichment_status: str  # 'pending', 'completed', 'failed'
    threshold_met: bool
    
    # Output
    result: Optional[Dict[str, Any]]
    execution_trace: List[Dict[str, Any]]
    processing_status: str
    error: Optional[str]


# ===========================
# Quality Scoring Models
# ===========================

@dataclass
class QualityDimensionScore:
    """Score for a single quality dimension"""
    dimension: str
    score: float  # 0-100
    weight: float  # 0.0-1.0
    max_score: float = 100.0
    issues: List[str] = None
    strengths: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.strengths is None:
            self.strengths = []


@dataclass
class OverallQualityScore:
    """Overall ticket quality score"""
    overall_score: float  # 0-100
    quality_status: str  # Poor/Fair/Good/Excellent
    threshold_met: bool
    dimension_scores: Dict[str, float]
    deficiencies: List[str]
    recommendations: List[str]
    automation_ready: bool


# ===========================
# ASR Enrichment Agent
# ===========================

class ASREnrichmentAgent:
    """LangGraph agent for ServiceNow ticket enrichment"""
    
    def __init__(self):
        """Initialize the agent with Azure OpenAI and configuration"""
        # Initialize Azure OpenAI
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
            temperature=float(os.getenv('AI_TEMPERATURE', '0.2')),
            max_tokens=int(os.getenv('AI_MAX_TOKENS', '2000'))
        )
        
        # Load configuration
        self.quality_threshold = float(os.getenv('QUALITY_THRESHOLD', '70'))
        self.dimension_weights = {
            'short_description': float(os.getenv('SHORT_DESC_WEIGHT', '0.25')),
            'long_description': float(os.getenv('LONG_DESC_WEIGHT', '0.30')),
            'categorization': float(os.getenv('CATEGORIZATION_WEIGHT', '0.25')),
            'resolution': float(os.getenv('RESOLUTION_WEIGHT', '0.20'))
        }
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        logger.info("ASR Enrichment Agent initialized successfully")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(ASREnrichmentState)
        
        # Add nodes
        workflow.add_node("fetch_ticket_data", self._fetch_ticket_data)
        workflow.add_node("assess_quality", self._assess_quality)
        workflow.add_node("enrich_content", self._enrich_content)
        workflow.add_node("categorize_route", self._categorize_route)
        workflow.add_node("validate_output", self._validate_output)
        
        # Define edges
        workflow.set_entry_point("fetch_ticket_data")
        workflow.add_edge("fetch_ticket_data", "assess_quality")
        workflow.add_edge("assess_quality", "enrich_content")
        workflow.add_edge("enrich_content", "categorize_route")
        workflow.add_edge("categorize_route", "validate_output")
        workflow.add_edge("validate_output", END)
        
        return workflow.compile()
    
    # ===========================
    # Node 1: Fetch Ticket Data
    # ===========================
    
    def _fetch_ticket_data(self, state: ASREnrichmentState) -> ASREnrichmentState:
        """Fetch ticket data from ServiceNow"""
        logger.info(f"Fetching ticket data for {state['ticket_id']}")
        
        state['execution_trace'].append({
            'node': 'fetch_ticket_data',
            'timestamp': datetime.now().isoformat(),
            'action': 'Retrieving ticket from ServiceNow'
        })
        
        try:
            # In production, use pysnow to fetch real data
            # For now, simulate ticket data structure
            ticket_data = self._fetch_from_servicenow(
                state['ticket_id'],
                state['snow_instance'],
                state['snow_credentials']
            )
            
            state['original_ticket'] = ticket_data
            state['processing_status'] = 'ticket_fetched'
            
            logger.info(f"Successfully fetched ticket {state['ticket_id']}")
            
        except Exception as e:
            logger.error(f"Error fetching ticket: {str(e)}")
            state['error'] = f"Failed to fetch ticket: {str(e)}"
            state['processing_status'] = 'error'
        
        return state
    
    def _fetch_from_servicenow(
        self,
        ticket_id: str,
        instance: str,
        credentials: Dict[str, str]
    ) -> Dict[str, Any]:
        """Fetch ticket from ServiceNow API"""
        # TODO: Implement actual pysnow integration
        # For now, return mock data structure
        return {
            'sys_id': ticket_id,
            'number': ticket_id,
            'short_description': 'App down',
            'description': 'Login broken',
            'assignment_group': '',
            'category': 'Other',
            'subcategory': '',
            'priority': '3',
            'impact': '3',
            'urgency': '3',
            'state': 'New',
            'close_notes': '',
            'opened_at': '2024-11-22 09:15:00',
            'opened_by': 'user@company.com',
            'sys_created_on': '2024-11-22 09:15:00',
            'sys_updated_on': '2024-11-22 09:15:00'
        }
    
    # ===========================
    # Node 2: Assess Quality
    # ===========================
    
    def _assess_quality(self, state: ASREnrichmentState) -> ASREnrichmentState:
        """Assess ticket quality across 4 dimensions"""
        logger.info(f"Assessing quality for ticket {state['ticket_id']}")
        
        state['execution_trace'].append({
            'node': 'assess_quality',
            'timestamp': datetime.now().isoformat(),
            'action': 'Scoring ticket across 4 dimensions'
        })
        
        ticket = state['original_ticket']
        
        # Score each dimension
        short_desc_score = self._score_short_description(
            ticket.get('short_description', '')
        )
        long_desc_score = self._score_long_description(
            ticket.get('description', '')
        )
        categorization_score = self._score_categorization(ticket)
        resolution_score = self._score_resolution(
            ticket.get('close_notes', '')
        )
        
        # Calculate overall score
        overall_score = (
            short_desc_score.score * self.dimension_weights['short_description'] +
            long_desc_score.score * self.dimension_weights['long_description'] +
            categorization_score.score * self.dimension_weights['categorization'] +
            resolution_score.score * self.dimension_weights['resolution']
        )
        
        # Determine quality status
        if overall_score >= 91:
            quality_status = "Excellent"
        elif overall_score >= 71:
            quality_status = "Good"
        elif overall_score >= 41:
            quality_status = "Fair"
        else:
            quality_status = "Poor"
        
        # Collect deficiencies and recommendations
        deficiencies = []
        recommendations = []
        
        for dim_score in [short_desc_score, long_desc_score, categorization_score, resolution_score]:
            deficiencies.extend(dim_score.issues)
            # Generate recommendations based on issues
            for issue in dim_score.issues:
                recommendations.append(self._generate_recommendation(dim_score.dimension, issue))
        
        # Store quality assessment
        state['quality_scores'] = {
            'short_description': short_desc_score.score,
            'long_description': long_desc_score.score,
            'categorization': categorization_score.score,
            'resolution': resolution_score.score,
            'overall': overall_score
        }
        state['before_score'] = overall_score
        state['deficiencies'] = deficiencies
        state['recommendations'] = recommendations
        state['threshold_met'] = overall_score >= self.quality_threshold
        state['processing_status'] = 'quality_assessed'
        
        logger.info(f"Quality score: {overall_score:.1f}/100 ({quality_status})")
        
        return state
    
    def _score_short_description(self, short_desc: str) -> QualityDimensionScore:
        """Score short description quality (0-100)"""
        score = 0.0
        issues = []
        strengths = []
        
        # Check length (25 points)
        min_len = int(os.getenv('MIN_SHORT_DESC_LENGTH', '10'))
        max_len = int(os.getenv('MAX_SHORT_DESC_LENGTH', '80'))
        
        if not short_desc or len(short_desc) < min_len:
            issues.append(f"Short description too short (min {min_len} chars)")
        elif len(short_desc) > max_len:
            issues.append(f"Short description too long (max {max_len} chars)")
        else:
            score += 25
            strengths.append("Appropriate length")
        
        # Check for system/application name (25 points)
        # Simple heuristic: contains uppercase words or common system terms
        if any(word.isupper() for word in short_desc.split()) or \
           any(term in short_desc.lower() for term in ['application', 'system', 'service', 'portal']):
            score += 25
            strengths.append("Includes system/application identifier")
        else:
            issues.append("Missing system/application name")
        
        # Check specificity (25 points)
        # Avoid vague terms
        vague_terms = ['error', 'issue', 'problem', 'help', 'not working', 'down', 'broken']
        if any(term in short_desc.lower() for term in vague_terms) and len(short_desc) < 30:
            issues.append("Description too vague (needs specific issue)")
        else:
            score += 25
            strengths.append("Specific issue described")
        
        # Check actionability (25 points)
        # Should describe what's wrong, not just state a symptom
        if len(short_desc.split()) >= 4:  # At least 4 words for context
            score += 25
            strengths.append("Actionable and clear")
        else:
            issues.append("Not actionable (too brief)")
        
        return QualityDimensionScore(
            dimension='short_description',
            score=score,
            weight=self.dimension_weights['short_description'],
            issues=issues,
            strengths=strengths
        )
    
    def _score_long_description(self, long_desc: str) -> QualityDimensionScore:
        """Score long description quality (0-100)"""
        score = 0.0
        issues = []
        strengths = []
        
        min_len = int(os.getenv('MIN_LONG_DESC_LENGTH', '100'))
        
        # Check length (15 points)
        if not long_desc or len(long_desc) < min_len:
            issues.append(f"Long description too short (min {min_len} chars)")
        else:
            score += 15
            strengths.append("Adequate length")
        
        # Check for symptom description (15 points)
        symptom_keywords = ['issue', 'problem', 'error', 'unable', 'cannot', 'failed', 'failure']
        if any(kw in long_desc.lower() for kw in symptom_keywords):
            score += 15
            strengths.append("Describes symptom")
        else:
            issues.append("Missing symptom description (what happened)")
        
        # Check for timeline (10 points)
        timeline_keywords = ['started', 'began', 'occurred', 'at', 'am', 'pm', 'time', 'date']
        if any(kw in long_desc.lower() for kw in timeline_keywords):
            score += 10
            strengths.append("Includes timeline")
        else:
            issues.append("Missing timeline (when it happened)")
        
        # Check for scope (10 points)
        scope_keywords = ['users', 'user', 'all', 'some', 'affected', 'impacted', 'team']
        if any(kw in long_desc.lower() for kw in scope_keywords):
            score += 10
            strengths.append("Describes scope")
        else:
            issues.append("Missing scope (who is affected)")
        
        # Check for reproduction steps (20 points)
        repro_keywords = ['steps', 'reproduce', 'step 1', 'step 2', '1.', '2.', 'first', 'then']
        if any(kw in long_desc.lower() for kw in repro_keywords):
            score += 20
            strengths.append("Includes reproduction steps")
        else:
            issues.append("Missing reproduction steps")
        
        # Check for error details (15 points)
        error_keywords = ['error', 'code', 'message', '500', '404', '403', 'exception', 'stack']
        if any(kw in long_desc.lower() for kw in error_keywords):
            score += 15
            strengths.append("Includes error details")
        else:
            issues.append("Missing error messages/codes")
        
        # Check for expected vs actual (15 points)
        expected_keywords = ['expected', 'should', 'actual', 'instead', 'but']
        if any(kw in long_desc.lower() for kw in expected_keywords):
            score += 15
            strengths.append("Describes expected vs actual behavior")
        else:
            issues.append("Missing expected vs actual behavior")
        
        return QualityDimensionScore(
            dimension='long_description',
            score=score,
            weight=self.dimension_weights['long_description'],
            issues=issues,
            strengths=strengths
        )
    
    def _score_categorization(self, ticket: Dict[str, Any]) -> QualityDimensionScore:
        """Score categorization quality (0-100)"""
        score = 0.0
        issues = []
        strengths = []
        
        # Check assignment group (30 points)
        if ticket.get('assignment_group') and ticket['assignment_group'].strip():
            score += 30
            strengths.append("Has assignment group")
        else:
            issues.append("No assignment group specified")
        
        # Check category (25 points)
        if ticket.get('category') and ticket['category'] not in ['', 'Other', 'Unassigned']:
            score += 25
            strengths.append("Has category")
        else:
            issues.append("Missing or invalid category")
        
        # Check subcategory (20 points)
        if ticket.get('subcategory') and ticket['subcategory'].strip():
            score += 20
            strengths.append("Has subcategory")
        else:
            issues.append("Missing subcategory")
        
        # Check priority (15 points)
        if ticket.get('priority') and ticket['priority'] in ['1', '2', '3', '4']:
            score += 15
            strengths.append("Has priority")
        else:
            issues.append("Missing or invalid priority")
        
        # Check impact (10 points)
        if ticket.get('impact') and ticket['impact'] in ['1', '2', '3']:
            score += 10
            strengths.append("Has impact level")
        else:
            issues.append("Missing impact level")
        
        return QualityDimensionScore(
            dimension='categorization',
            score=score,
            weight=self.dimension_weights['categorization'],
            issues=issues,
            strengths=strengths
        )
    
    def _score_resolution(self, resolution: str) -> QualityDimensionScore:
        """Score resolution detail quality (0-100)"""
        score = 0.0
        issues = []
        strengths = []
        
        min_len = int(os.getenv('MIN_RESOLUTION_LENGTH', '50'))
        
        # Check if resolution exists (25 points)
        if not resolution or len(resolution) < min_len:
            issues.append("No resolution notes or too brief")
            return QualityDimensionScore(
                dimension='resolution',
                score=0,
                weight=self.dimension_weights['resolution'],
                issues=issues,
                strengths=strengths
            )
        else:
            score += 25
            strengths.append("Has resolution notes")
        
        # Check for root cause (25 points)
        root_cause_keywords = ['root cause', 'cause', 'reason', 'due to', 'caused by']
        if any(kw in resolution.lower() for kw in root_cause_keywords):
            score += 25
            strengths.append("Identifies root cause")
        else:
            issues.append("Missing root cause")
        
        # Check for resolution steps (20 points)
        steps_keywords = ['step', 'steps', '1.', '2.', 'first', 'then', 'next', 'finally']
        if any(kw in resolution.lower() for kw in steps_keywords):
            score += 20
            strengths.append("Documents resolution steps")
        else:
            issues.append("Missing resolution steps")
        
        # Check for verification (15 points)
        verify_keywords = ['verified', 'confirmed', 'tested', 'validation', 'checked']
        if any(kw in resolution.lower() for kw in verify_keywords):
            score += 15
            strengths.append("Includes verification")
        else:
            issues.append("No verification noted")
        
        # Check for preventive measures (15 points)
        preventive_keywords = ['prevent', 'future', 'monitoring', 'alert', 'knowledge', 'kb']
        if any(kw in resolution.lower() for kw in preventive_keywords):
            score += 15
            strengths.append("Notes preventive measures")
        else:
            issues.append("No preventive measures documented")
        
        return QualityDimensionScore(
            dimension='resolution',
            score=score,
            weight=self.dimension_weights['resolution'],
            issues=issues,
            strengths=strengths
        )
    
    def _generate_recommendation(self, dimension: str, issue: str) -> str:
        """Generate actionable recommendation from issue"""
        recommendations_map = {
            'Short description too short': 'Expand short description to include system name and specific issue (10-80 chars)',
            'Short description too long': 'Condense short description to 80 characters or less',
            'Missing system/application name': 'Add specific system/application name (e.g., "ATLAS Application")',
            'Description too vague': 'Replace vague terms with specific error type or symptom',
            'Not actionable': 'Make description actionable by stating what needs investigation',
            'Long description too short': 'Expand description with timeline, scope, steps, and error details',
            'Missing symptom description': 'Describe what happened (e.g., "Users unable to authenticate")',
            'Missing timeline': 'Add when issue started (date/time)',
            'Missing scope': 'Specify who is affected (all users, specific team, etc.)',
            'Missing reproduction steps': 'Add step-by-step instructions to reproduce the issue',
            'Missing error messages/codes': 'Include exact error messages, codes, or screenshots',
            'Missing expected vs actual': 'Describe expected behavior vs what actually happened',
            'No assignment group': 'Route to correct assignment group based on system/service',
            'Missing or invalid category': 'Assign accurate category (Hardware, Software, Network, etc.)',
            'Missing subcategory': 'Add specific subcategory for issue type',
            'Missing or invalid priority': 'Assess priority (P1-P4) based on impact and urgency',
            'Missing impact level': 'Classify impact (Critical/High/Medium/Low)',
            'No resolution notes': 'Document root cause, resolution steps, and verification',
            'Missing root cause': 'Identify and document root cause of the issue',
            'Missing resolution steps': 'List step-by-step resolution actions taken',
            'No verification noted': 'Document how resolution was verified/tested',
            'No preventive measures': 'Note preventive measures (monitoring, KB article, code fix)'
        }
        
        for key, rec in recommendations_map.items():
            if key.lower() in issue.lower():
                return rec
        
        return f"Improve {dimension}: {issue}"
    
    # ===========================
    # Node 3: Enrich Content
    # ===========================
    
    def _enrich_content(self, state: ASREnrichmentState) -> ASREnrichmentState:
        """Enrich ticket content using AI"""
        logger.info(f"Enriching content for ticket {state['ticket_id']}")
        
        state['execution_trace'].append({
            'node': 'enrich_content',
            'timestamp': datetime.now().isoformat(),
            'action': 'Enhancing ticket content with AI'
        })
        
        ticket = state['original_ticket']
        enriched = ticket.copy()
        changes_made = []
        
        # Enrich short description if needed
        if 'short_desc' in state['enrich_dimensions']:
            if state['quality_scores']['short_description'] < 70:
                enriched_short = self._enrich_short_description(ticket)
                if enriched_short != ticket.get('short_description'):
                    enriched['short_description'] = enriched_short
                    changes_made.append("Enhanced short description with system name and specific issue")
        
        # Enrich long description if needed
        if 'long_desc' in state['enrich_dimensions']:
            if state['quality_scores']['long_description'] < 70:
                enriched_long = self._enrich_long_description(ticket, state['deficiencies'])
                if enriched_long != ticket.get('description'):
                    enriched['description'] = enriched_long
                    changes_made.append("Added structured long description with timeline, scope, and reproduction steps")
        
        state['enriched_ticket'] = enriched
        state['changes_made'] = changes_made
        state['processing_status'] = 'content_enriched'
        
        return state
    
    def _enrich_short_description(self, ticket: Dict[str, Any]) -> str:
        """Use AI to enhance short description"""
        current_short = ticket.get('short_description', '')
        current_long = ticket.get('description', '')
        
        prompt = f"""You are a ServiceNow ticket quality expert. Enhance this incident ticket's short description.

Current Short Description: "{current_short}"
Additional Context: "{current_long}"

Requirements:
- 10-80 characters
- Include system/application name if identifiable
- Describe specific issue clearly
- Make it actionable
- No jargon without context

Generate an enhanced short description that meets quality standards.

Enhanced Short Description:"""

        try:
            response = self.llm.invoke(prompt)
            enhanced = response.content.strip().strip('"').strip("'")
            
            # Ensure length constraints
            if len(enhanced) > 80:
                enhanced = enhanced[:77] + "..."
            
            return enhanced if enhanced else current_short
        
        except Exception as e:
            logger.error(f"Error enriching short description: {str(e)}")
            return current_short
    
    def _enrich_long_description(self, ticket: Dict[str, Any], deficiencies: List[str]) -> str:
        """Use AI to enhance long description"""
        current_long = ticket.get('description', '')
        current_short = ticket.get('short_description', '')
        
        prompt = f"""You are a ServiceNow ticket quality expert. Enhance this incident ticket's long description to meet automation standards.

Current Short Description: "{current_short}"
Current Long Description: "{current_long}"

Identified Deficiencies:
{chr(10).join(f'- {d}' for d in deficiencies if 'long description' in d.lower())}

Required Sections:
1. Issue: What happened (symptom)
2. Timeline: When it happened
3. Scope: Who is affected
4. Environment: Production/Test/Dev
5. Symptoms: Observable behaviors
6. Steps to Reproduce: Detailed steps
7. Expected vs Actual: What should happen vs what does
8. Impact: Business impact

Generate a comprehensive long description with all required sections. Use the current information and infer reasonable details where appropriate.

Enhanced Long Description:"""

        try:
            response = self.llm.invoke(prompt)
            enhanced = response.content.strip()
            
            return enhanced if len(enhanced) >= 100 else current_long
        
        except Exception as e:
            logger.error(f"Error enriching long description: {str(e)}")
            return current_long
    
    # ===========================
    # Node 4: Categorize & Route
    # ===========================
    
    def _categorize_route(self, state: ASREnrichmentState) -> ASREnrichmentState:
        """Categorize ticket and determine routing"""
        logger.info(f"Categorizing and routing ticket {state['ticket_id']}")
        
        state['execution_trace'].append({
            'node': 'categorize_route',
            'timestamp': datetime.now().isoformat(),
            'action': 'Determining categorization and routing'
        })
        
        enriched = state['enriched_ticket']
        
        # Enrich categorization if needed
        if 'categorization' in state['enrich_dimensions']:
            if state['quality_scores']['categorization'] < 70:
                categorization = self._determine_categorization(enriched)
                
                enriched['assignment_group'] = categorization.get('assignment_group', '')
                enriched['category'] = categorization.get('category', '')
                enriched['subcategory'] = categorization.get('subcategory', '')
                enriched['priority'] = categorization.get('priority', '3')
                enriched['impact'] = categorization.get('impact', '3')
                enriched['urgency'] = categorization.get('urgency', '3')
                
                state['changes_made'].append(
                    f"Updated categorization to {categorization['category']} > {categorization['subcategory']}"
                )
                state['changes_made'].append(
                    f"Routed to {categorization['assignment_group']}"
                )
        
        state['enriched_ticket'] = enriched
        state['processing_status'] = 'categorized'
        
        return state
    
    def _determine_categorization(self, ticket: Dict[str, Any]) -> Dict[str, str]:
        """Use AI to determine correct categorization"""
        short_desc = ticket.get('short_description', '')
        long_desc = ticket.get('description', '')
        
        prompt = f"""You are a ServiceNow ITSM categorization expert. Analyze this ticket and determine the correct categorization.

Short Description: "{short_desc}"
Long Description: "{long_desc}"

Determine:
1. Assignment Group: Which team should handle this? (e.g., "Platform Engineering", "Network Operations", "Database Team")
2. Category: High-level category (Hardware, Software, Network, Database, Security, Other)
3. Subcategory: Specific issue type (e.g., "Authentication Service", "API Gateway", "Load Balancer")
4. Priority: P1 (Critical), P2 (High), P3 (Medium), P4 (Low)
5. Impact: 1 (Critical), 2 (High), 3 (Medium)
6. Urgency: 1 (High), 2 (Medium), 3 (Low)

Respond in JSON format:
{{
    "assignment_group": "...",
    "category": "...",
    "subcategory": "...",
    "priority": "...",
    "impact": "...",
    "urgency": "...",
    "reasoning": "..."
}}"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Extract JSON from response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            import json
            categorization = json.loads(content)
            
            return categorization
        
        except Exception as e:
            logger.error(f"Error determining categorization: {str(e)}")
            return {
                'assignment_group': 'IT Support',
                'category': 'Software',
                'subcategory': 'Application',
                'priority': '3',
                'impact': '3',
                'urgency': '3',
                'reasoning': 'Default categorization due to processing error'
            }
    
    # ===========================
    # Node 5: Validate Output
    # ===========================
    
    def _validate_output(self, state: ASREnrichmentState) -> ASREnrichmentState:
        """Validate enriched ticket and calculate improvement"""
        logger.info(f"Validating enrichment for ticket {state['ticket_id']}")
        
        state['execution_trace'].append({
            'node': 'validate_output',
            'timestamp': datetime.now().isoformat(),
            'action': 'Validating enrichment quality'
        })
        
        # Re-score enriched ticket
        enriched_scores = self._calculate_quality_score(state['enriched_ticket'])
        
        state['after_score'] = enriched_scores['overall']
        state['threshold_met'] = enriched_scores['overall'] >= self.quality_threshold
        state['enrichment_status'] = 'completed'
        
        # Build result
        state['result'] = {
            'ticket_id': state['ticket_id'],
            'enrichment_status': 'completed',
            'before_score': state['before_score'],
            'after_score': state['after_score'],
            'improvement': state['after_score'] - state['before_score'],
            'threshold_met': state['threshold_met'],
            'quality_status': self._get_quality_status(state['after_score']),
            'enriched_data': state['enriched_ticket'],
            'changes_made': state['changes_made'],
            'dimension_scores': {
                'before': state['quality_scores'],
                'after': enriched_scores
            }
        }
        
        state['processing_status'] = 'completed'
        
        logger.info(
            f"Enrichment completed: {state['before_score']:.1f} → "
            f"{state['after_score']:.1f} (Δ{state['after_score'] - state['before_score']:.1f})"
        )
        
        return state
    
    def _calculate_quality_score(self, ticket: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quality scores for ticket"""
        short_score = self._score_short_description(ticket.get('short_description', ''))
        long_score = self._score_long_description(ticket.get('description', ''))
        cat_score = self._score_categorization(ticket)
        res_score = self._score_resolution(ticket.get('close_notes', ''))
        
        overall = (
            short_score.score * self.dimension_weights['short_description'] +
            long_score.score * self.dimension_weights['long_description'] +
            cat_score.score * self.dimension_weights['categorization'] +
            res_score.score * self.dimension_weights['resolution']
        )
        
        return {
            'short_description': short_score.score,
            'long_description': long_score.score,
            'categorization': cat_score.score,
            'resolution': res_score.score,
            'overall': overall
        }
    
    def _get_quality_status(self, score: float) -> str:
        """Get quality status label"""
        if score >= 91:
            return "Excellent"
        elif score >= 71:
            return "Good"
        elif score >= 41:
            return "Fair"
        else:
            return "Poor"
    
    # ===========================
    # Public Interface
    # ===========================
    
    def process(
        self,
        ticket_id: str,
        operation: str = 'enrich',
        enrich_dimensions: List[str] = None,
        auto_update_snow: bool = False,
        snow_instance: str = None,
        snow_credentials: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Process a ticket through the enrichment workflow"""
        
        if enrich_dimensions is None:
            enrich_dimensions = ['short_desc', 'long_desc', 'categorization']
        
        if snow_instance is None:
            snow_instance = os.getenv('SNOW_INSTANCE')
        
        if snow_credentials is None:
            snow_credentials = {
                'username': os.getenv('SNOW_USERNAME'),
                'password': os.getenv('SNOW_PASSWORD')
            }
        
        # Initialize state
        initial_state = ASREnrichmentState(
            task_id=f"enrich_{ticket_id}_{datetime.now().timestamp()}",
            ticket_id=ticket_id,
            operation=operation,
            enrich_dimensions=enrich_dimensions,
            auto_update_snow=auto_update_snow,
            snow_instance=snow_instance,
            snow_credentials=snow_credentials,
            original_ticket=None,
            enriched_ticket=None,
            quality_scores=None,
            before_score=None,
            after_score=None,
            deficiencies=None,
            recommendations=None,
            changes_made=[],
            enrichment_status='pending',
            threshold_met=False,
            result=None,
            execution_trace=[],
            processing_status='initialized',
            error=None
        )
        
        try:
            # Execute workflow
            final_state = self.workflow.invoke(initial_state)
            
            return final_state['result']
        
        except Exception as e:
            logger.error(f"Error processing ticket: {str(e)}")
            return {
                'ticket_id': ticket_id,
                'enrichment_status': 'failed',
                'error': str(e)
            }


# ===========================
# Main Entry Point
# ===========================

if __name__ == "__main__":
    # Test the agent
    agent = ASREnrichmentAgent()
    
    result = agent.process(
        ticket_id="INC0025000",
        operation="enrich",
        enrich_dimensions=['short_desc', 'long_desc', 'categorization']
    )
    
    print("Enrichment Result:")
    print(f"Before: {result['before_score']:.1f}/100")
    print(f"After: {result['after_score']:.1f}/100")
    print(f"Improvement: +{result['improvement']:.1f}")
    print(f"Threshold Met: {result['threshold_met']}")
    print(f"\nChanges Made:")
    for change in result['changes_made']:
        print(f"  - {change}")
