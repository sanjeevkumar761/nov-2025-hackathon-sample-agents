"""
Regulatory Requirements Analyzer Agent

AI-powered agent for analyzing regulatory documents and extracting
Laws, Rules, and Regulations (LRR) using LangGraph workflow.
"""

import os
import json
import logging
import time
from typing import TypedDict, Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


class RegulatoryState(TypedDict):
    """State schema for regulatory document analysis workflow"""
    # Input
    document_id: str
    document_text: str
    document_metadata: Dict[str, Any]
    
    # Processing results
    extracted_sections: Optional[List[Dict[str, Any]]]
    identified_lrr: Optional[List[Dict[str, Any]]]
    categorized_rules: Optional[Dict[str, List[Dict[str, Any]]]]
    taxonomy_impacts: Optional[List[Dict[str, Any]]]
    compliance_summary: Optional[str]
    risk_assessment: Optional[Dict[str, Any]]
    
    # Metadata
    execution_trace: List[Dict[str, Any]]
    processing_status: str


class RegulatoryAnalyzerAgent:
    """
    AI agent for analyzing regulatory documents using LangGraph.
    
    Workflow:
    1. Extract document structure and sections
    2. Identify Laws, Rules, and Regulations (LRR)
    3. Categorize rules by type and impact
    4. Assess taxonomy impacts
    5. Generate compliance summary
    """
    
    def __init__(self):
        """Initialize the regulatory analyzer agent"""
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
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.2,  # Lower for more deterministic analysis
            max_tokens=2000
        )
        
        # Build the workflow
        self.logger.info("Building LangGraph workflow...")
        self.workflow = self._build_workflow()
        self.logger.info("✓ Regulatory Analyzer Agent initialized successfully")
    
    def _build_workflow(self):
        """Build the LangGraph workflow for regulatory analysis"""
        workflow = StateGraph(RegulatoryState)
        
        # Add nodes
        workflow.add_node("extract_sections", self._extract_sections)
        workflow.add_node("identify_lrr", self._identify_lrr)
        workflow.add_node("categorize_rules", self._categorize_rules)
        workflow.add_node("assess_taxonomy", self._assess_taxonomy)
        workflow.add_node("generate_summary", self._generate_summary)
        
        # Define edges
        workflow.set_entry_point("extract_sections")
        workflow.add_edge("extract_sections", "identify_lrr")
        workflow.add_edge("identify_lrr", "categorize_rules")
        workflow.add_edge("categorize_rules", "assess_taxonomy")
        workflow.add_edge("assess_taxonomy", "generate_summary")
        workflow.add_edge("generate_summary", END)
        
        return workflow.compile()
    
    def _add_trace_step(self, state: RegulatoryState, node: str, 
                        action: str, details: Dict[str, Any], duration_ms: int):
        """Add execution trace step"""
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
    
    def _extract_sections(self, state: RegulatoryState) -> RegulatoryState:
        """
        Node 1: Extract document structure and key sections
        """
        start_time = time.time()
        self.logger.info("Node: Extracting document sections...")
        
        try:
            prompt = f"""
You are an expert at analyzing regulatory documents.

Analyze this regulatory document and extract its key sections:

Document Text:
{state['document_text'][:8000]}

Extract the following:
1. Document title and identifier
2. Main sections and their purposes
3. Key definitions
4. Effective dates
5. Scope and applicability

Return ONLY a JSON object with this structure:
{{
    "title": "document title",
    "identifier": "regulation ID",
    "sections": [
        {{
            "section_number": "1.1",
            "title": "Section Title",
            "content": "Brief summary",
            "type": "definition|requirement|procedure|other"
        }}
    ],
    "effective_date": "YYYY-MM-DD or null",
    "scope": "Brief description of scope",
    "key_definitions": ["term1", "term2"]
}}
"""
            
            response = self.llm.invoke([
                {"role": "system", "content": "You are a regulatory document analysis expert."},
                {"role": "user", "content": prompt}
            ])
            
            # Parse response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            
            extracted = json.loads(content)
            state['extracted_sections'] = extracted.get('sections', [])
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='extract_sections',
                action='Extracted document structure and sections',
                details={
                    'sections_found': len(state['extracted_sections']),
                    'document_title': extracted.get('title', 'Unknown'),
                    'identifier': extracted.get('identifier', 'N/A')
                },
                duration_ms=duration
            )
            
            self.logger.info(f"✓ Extracted {len(state['extracted_sections'])} sections")
            
        except Exception as e:
            self.logger.error(f"✗ Section extraction failed: {e}")
            state['extracted_sections'] = []
        
        return state
    
    def _identify_lrr(self, state: RegulatoryState) -> RegulatoryState:
        """
        Node 2: Identify Laws, Rules, and Regulations (LRR)
        """
        start_time = time.time()
        self.logger.info("Node: Identifying LRR...")
        
        try:
            # Prepare sections text
            sections_text = "\n\n".join([
                f"Section {s.get('section_number', 'N/A')}: {s.get('title', 'Untitled')}\n{s.get('content', '')}"
                for s in state['extracted_sections'][:10]  # Limit to first 10 sections
            ])
            
            prompt = f"""
You are an expert at identifying Laws, Rules, and Regulations in regulatory documents.

Analyze these document sections and identify all Laws, Rules, and Regulations (LRR):

{sections_text}

For each LRR, extract:
1. Type (Law, Rule, or Regulation)
2. Reference number or identifier
3. Brief description
4. Compliance requirement (what must be done)
5. Obligations (who must comply)
6. Penalties for non-compliance (if mentioned)

Return ONLY a JSON object:
{{
    "lrr_items": [
        {{
            "type": "Law|Rule|Regulation",
            "reference": "Section X.Y or Article Z",
            "description": "Brief description",
            "requirement": "What must be done",
            "obligated_parties": ["party1", "party2"],
            "penalties": "Penalties if any",
            "severity": "High|Medium|Low"
        }}
    ]
}}
"""
            
            response = self.llm.invoke([
                {"role": "system", "content": "You are a regulatory compliance expert."},
                {"role": "user", "content": prompt}
            ])
            
            # Parse response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(content)
            state['identified_lrr'] = result.get('lrr_items', [])
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='identify_lrr',
                action='Identified Laws, Rules, and Regulations',
                details={
                    'lrr_count': len(state['identified_lrr']),
                    'types': {
                        'laws': len([x for x in state['identified_lrr'] if x.get('type') == 'Law']),
                        'rules': len([x for x in state['identified_lrr'] if x.get('type') == 'Rule']),
                        'regulations': len([x for x in state['identified_lrr'] if x.get('type') == 'Regulation'])
                    }
                },
                duration_ms=duration
            )
            
            self.logger.info(f"✓ Identified {len(state['identified_lrr'])} LRR items")
            
        except Exception as e:
            self.logger.error(f"✗ LRR identification failed: {e}")
            state['identified_lrr'] = []
        
        return state
    
    def _categorize_rules(self, state: RegulatoryState) -> RegulatoryState:
        """
        Node 3: Categorize rules by type and impact
        """
        start_time = time.time()
        self.logger.info("Node: Categorizing rules...")
        
        try:
            # Categorize by type and severity
            categories = {
                'high_priority': [],
                'medium_priority': [],
                'low_priority': [],
                'reporting_requirements': [],
                'operational_requirements': [],
                'compliance_deadlines': []
            }
            
            for lrr in state['identified_lrr']:
                severity = lrr.get('severity', 'Medium')
                requirement = lrr.get('requirement', '').lower()
                
                # Priority categorization
                if severity == 'High':
                    categories['high_priority'].append(lrr)
                elif severity == 'Medium':
                    categories['medium_priority'].append(lrr)
                else:
                    categories['low_priority'].append(lrr)
                
                # Functional categorization
                if any(word in requirement for word in ['report', 'filing', 'disclosure', 'submit']):
                    categories['reporting_requirements'].append(lrr)
                if any(word in requirement for word in ['implement', 'establish', 'maintain', 'operate']):
                    categories['operational_requirements'].append(lrr)
                if any(word in requirement for word in ['deadline', 'by', 'within', 'before']):
                    categories['compliance_deadlines'].append(lrr)
            
            state['categorized_rules'] = categories
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='categorize_rules',
                action='Categorized rules by priority and type',
                details={
                    'high_priority': len(categories['high_priority']),
                    'reporting_requirements': len(categories['reporting_requirements']),
                    'operational_requirements': len(categories['operational_requirements']),
                    'compliance_deadlines': len(categories['compliance_deadlines'])
                },
                duration_ms=duration
            )
            
            self.logger.info("✓ Rules categorized successfully")
            
        except Exception as e:
            self.logger.error(f"✗ Rule categorization failed: {e}")
            state['categorized_rules'] = {}
        
        return state
    
    def _assess_taxonomy(self, state: RegulatoryState) -> RegulatoryState:
        """
        Node 4: Assess taxonomy impacts
        """
        start_time = time.time()
        self.logger.info("Node: Assessing taxonomy impacts...")
        
        try:
            # Prepare LRR summary for taxonomy analysis
            lrr_summary = "\n".join([
                f"- {item.get('type')}: {item.get('description', 'N/A')} (Severity: {item.get('severity', 'Unknown')})"
                for item in state['identified_lrr'][:20]
            ])
            
            prompt = f"""
You are an expert at assessing regulatory impact on organizational taxonomy.

Given these regulatory requirements:
{lrr_summary}

Analyze the potential impacts on organizational taxonomy:
1. Which business functions/departments are affected?
2. What new classifications or categories might be needed?
3. What existing processes need modification?
4. What new data fields or attributes are required?

Return ONLY a JSON object:
{{
    "taxonomy_impacts": [
        {{
            "area": "Business area affected",
            "impact_type": "New Category|Modification|Reporting",
            "description": "Impact description",
            "urgency": "High|Medium|Low",
            "recommended_action": "What should be done"
        }}
    ],
    "overall_assessment": "Summary of taxonomy changes needed"
}}
"""
            
            response = self.llm.invoke([
                {"role": "system", "content": "You are a regulatory taxonomy expert."},
                {"role": "user", "content": prompt}
            ])
            
            # Parse response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(content)
            state['taxonomy_impacts'] = result.get('taxonomy_impacts', [])
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='assess_taxonomy',
                action='Assessed taxonomy impacts',
                details={
                    'impacts_identified': len(state['taxonomy_impacts']),
                    'high_urgency': len([x for x in state['taxonomy_impacts'] if x.get('urgency') == 'High'])
                },
                duration_ms=duration
            )
            
            self.logger.info(f"✓ Identified {len(state['taxonomy_impacts'])} taxonomy impacts")
            
        except Exception as e:
            self.logger.error(f"✗ Taxonomy assessment failed: {e}")
            state['taxonomy_impacts'] = []
        
        return state
    
    def _generate_summary(self, state: RegulatoryState) -> RegulatoryState:
        """
        Node 5: Generate compliance summary and risk assessment
        """
        start_time = time.time()
        self.logger.info("Node: Generating compliance summary...")
        
        try:
            prompt = f"""
You are a regulatory compliance expert.

Based on this analysis:
- Total LRR items: {len(state['identified_lrr'])}
- High priority items: {len(state['categorized_rules'].get('high_priority', []))}
- Taxonomy impacts: {len(state['taxonomy_impacts'])}

Generate a comprehensive compliance summary including:
1. Executive summary of key findings
2. Critical compliance requirements
3. Risk assessment (high/medium/low risks)
4. Recommended immediate actions
5. Timeline for compliance

Return ONLY a JSON object:
{{
    "executive_summary": "Brief overview",
    "critical_requirements": ["requirement1", "requirement2"],
    "risk_assessment": {{
        "high_risks": ["risk1"],
        "medium_risks": ["risk2"],
        "low_risks": ["risk3"],
        "overall_risk_level": "High|Medium|Low"
    }},
    "immediate_actions": ["action1", "action2"],
    "compliance_timeline": "Recommended timeline"
}}
"""
            
            response = self.llm.invoke([
                {"role": "system", "content": "You are a compliance risk expert."},
                {"role": "user", "content": prompt}
            ])
            
            # Parse response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(content)
            state['compliance_summary'] = result.get('executive_summary', '')
            state['risk_assessment'] = result.get('risk_assessment', {})
            state['processing_status'] = 'completed'
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='generate_summary',
                action='Generated compliance summary and risk assessment',
                details={
                    'overall_risk': result.get('risk_assessment', {}).get('overall_risk_level', 'Unknown'),
                    'immediate_actions': len(result.get('immediate_actions', []))
                },
                duration_ms=duration
            )
            
            self.logger.info("✓ Compliance summary generated")
            
        except Exception as e:
            self.logger.error(f"✗ Summary generation failed: {e}")
            state['compliance_summary'] = "Error generating summary"
            state['risk_assessment'] = {}
            state['processing_status'] = 'failed'
        
        return state
    
    def analyze_document(self, document_id: str, document_text: str, 
                        metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point: Analyze a regulatory document
        
        Args:
            document_id: Unique document identifier
            document_text: Full text of the regulatory document
            metadata: Optional document metadata (filename, upload date, etc.)
        
        Returns:
            Complete analysis results
        """
        self.logger.info(f"Analyzing document: {document_id}")
        
        # Initialize state
        initial_state = RegulatoryState(
            document_id=document_id,
            document_text=document_text,
            document_metadata=metadata or {},
            extracted_sections=None,
            identified_lrr=None,
            categorized_rules=None,
            taxonomy_impacts=None,
            compliance_summary=None,
            risk_assessment=None,
            execution_trace=[],
            processing_status='processing'
        )
        
        # Execute workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            # Format result
            result = {
                'document_id': document_id,
                'metadata': metadata or {},
                'analysis': {
                    'sections_extracted': len(final_state.get('extracted_sections', [])),
                    'lrr_identified': len(final_state.get('identified_lrr', [])),
                    'taxonomy_impacts': len(final_state.get('taxonomy_impacts', []))
                },
                'extracted_sections': final_state.get('extracted_sections', []),
                'identified_lrr': final_state.get('identified_lrr', []),
                'categorized_rules': final_state.get('categorized_rules', {}),
                'taxonomy_impacts': final_state.get('taxonomy_impacts', []),
                'compliance_summary': final_state.get('compliance_summary', ''),
                'risk_assessment': final_state.get('risk_assessment', {}),
                'execution_trace': final_state.get('execution_trace', []),
                'status': final_state.get('processing_status', 'completed'),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("✓ Document analysis complete")
            return result
            
        except Exception as e:
            self.logger.error(f"✗ Document analysis failed: {e}")
            raise
    
    def get_workflow_graph(self) -> Dict[str, Any]:
        """Get workflow structure for visualization"""
        nodes = [
            {"id": "START", "label": "Start", "type": "entry", 
             "description": "Begin regulatory document analysis"},
            {"id": "extract_sections", "label": "Extract Sections", "type": "node",
             "description": "Extract document structure and key sections"},
            {"id": "identify_lrr", "label": "Identify LRR", "type": "node",
             "description": "Identify Laws, Rules, and Regulations"},
            {"id": "categorize_rules", "label": "Categorize Rules", "type": "node",
             "description": "Categorize by priority and type"},
            {"id": "assess_taxonomy", "label": "Assess Taxonomy", "type": "node",
             "description": "Assess impacts on organizational taxonomy"},
            {"id": "generate_summary", "label": "Generate Summary", "type": "node",
             "description": "Create compliance summary and risk assessment"},
            {"id": "END", "label": "End", "type": "exit",
             "description": "Complete analysis"}
        ]
        
        edges = [
            {"from": "START", "to": "extract_sections", "label": "begin"},
            {"from": "extract_sections", "to": "identify_lrr", "label": "sections_extracted"},
            {"from": "identify_lrr", "to": "categorize_rules", "label": "lrr_identified"},
            {"from": "categorize_rules", "to": "assess_taxonomy", "label": "rules_categorized"},
            {"from": "assess_taxonomy", "to": "generate_summary", "label": "impacts_assessed"},
            {"from": "generate_summary", "to": "END", "label": "complete"}
        ]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "workflow_type": "sequential",
            "total_nodes": 5,
            "total_edges": 6
        }


if __name__ == "__main__":
    # Test the agent
    print("\n" + "="*60)
    print("Regulatory Requirements Analyzer Agent")
    print("="*60 + "\n")
    
    try:
        agent = RegulatoryAnalyzerAgent()
        print("✓ Agent initialized successfully\n")
        
        # Test with sample document
        sample_doc = """
        REGULATION (EU) 2024/123
        
        Article 1 - Scope
        This regulation applies to all financial institutions operating within the EU.
        
        Article 2 - Reporting Requirements
        All institutions must submit quarterly compliance reports by the last day
        of each quarter. Failure to comply may result in penalties up to €1,000,000.
        
        Article 3 - Data Protection
        Institutions must implement robust data protection measures compliant with
        GDPR standards. This includes encryption, access controls, and audit trails.
        """
        
        print("Testing with sample regulatory document...")
        result = agent.analyze_document(
            document_id="TEST-REG-001",
            document_text=sample_doc,
            metadata={"filename": "test_regulation.txt", "source": "EU"}
        )
        
        print(f"\n✓ Analysis complete!")
        print(f"  - Sections extracted: {result['analysis']['sections_extracted']}")
        print(f"  - LRR identified: {result['analysis']['lrr_identified']}")
        print(f"  - Taxonomy impacts: {result['analysis']['taxonomy_impacts']}")
        print(f"  - Status: {result['status']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
