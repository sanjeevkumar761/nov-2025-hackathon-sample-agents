"""
Creds Inspect Agent

AI-powered agent for detecting credentials in Confluence content using LangGraph.

Workflow:
1. scan_content - Parse and extract content
2. detect_credentials - Identify exposed credentials
3. assess_risk - Evaluate severity and impact
4. generate_remediation - Create action plans
5. create_report - Executive summary
"""

import os
import json
import logging
import time
import re
from typing import TypedDict, Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


class CredsInspectState(TypedDict):
    """State schema for credential inspection workflow"""
    # Input
    scan_id: str
    content_text: str
    content_type: str  # 'confluence_page', 'attachment', 'text'
    content_metadata: Dict[str, Any]
    
    # Processing results
    extracted_content: Optional[Dict[str, Any]]
    detected_credentials: Optional[List[Dict[str, Any]]]
    risk_assessment: Optional[Dict[str, Any]]
    remediation_plan: Optional[List[Dict[str, Any]]]
    executive_report: Optional[str]
    
    # Metadata
    execution_trace: List[Dict[str, Any]]
    processing_status: str


class CredsInspectAgent:
    """
    AI agent for detecting and triaging exposed credentials using LangGraph.
    
    Workflow:
    1. Scan and extract content
    2. Detect credentials using patterns + AI
    3. Assess risk and severity
    4. Generate remediation guidance
    5. Create executive report
    """
    
    # Common credential patterns
    CREDENTIAL_PATTERNS = {
        'aws_access_key': r'AKIA[0-9A-Z]{16}',
        'aws_secret_key': r'(?i)aws(.{0,20})?[\'\"][0-9a-zA-Z\/+]{40}[\'\"]',
        'azure_connection_string': r'DefaultEndpointsProtocol=https;AccountName=.+;AccountKey=.+',
        'github_pat': r'ghp_[0-9a-zA-Z]{36}',
        'github_oauth': r'gho_[0-9a-zA-Z]{36}',
        'generic_api_key': r'(?i)(api[_-]?key|apikey)[\'\"\s:=]+[\'\"]*[0-9a-zA-Z\-_]{20,}[\'\"]*',
        'generic_secret': r'(?i)(secret|password|passwd|pwd)[\'\"\s:=]+[\'\"]*[0-9a-zA-Z\-_@#$%^&*]{8,}[\'\"]*',
        'jwt_token': r'eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+',
        'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        'connection_string': r'(?i)(server|host|hostname)[\s]*=[\s]*[^\s;]+[\s]*;[\s]*(database|db)[\s]*=',
        'slack_token': r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[0-9a-zA-Z]{24,32}',
        'bearer_token': r'Bearer\s+[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+',
    }
    
    def __init__(self):
        """Initialize the creds inspect agent"""
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
            temperature=0.1,  # Very low for deterministic security analysis
            max_tokens=2000
        )
        
        # Build the workflow
        self.logger.info("Building LangGraph workflow...")
        self.workflow = self._build_workflow()
        self.logger.info("✓ Creds Inspect Agent initialized successfully")
    
    def _build_workflow(self):
        """Build the LangGraph workflow for credential detection"""
        workflow = StateGraph(CredsInspectState)
        
        # Add nodes
        workflow.add_node("scan_content", self._scan_content)
        workflow.add_node("detect_credentials", self._detect_credentials)
        workflow.add_node("assess_risk", self._assess_risk)
        workflow.add_node("generate_remediation", self._generate_remediation)
        workflow.add_node("create_report", self._create_report)
        
        # Define edges
        workflow.set_entry_point("scan_content")
        workflow.add_edge("scan_content", "detect_credentials")
        workflow.add_edge("detect_credentials", "assess_risk")
        workflow.add_edge("assess_risk", "generate_remediation")
        workflow.add_edge("generate_remediation", "create_report")
        workflow.add_edge("create_report", END)
        
        return workflow.compile()
    
    def _add_trace_step(self, state: CredsInspectState, node: str, 
                       action: str, details: Dict = None, duration_ms: int = 0):
        """Add execution trace step"""
        state['execution_trace'].append({
            'step': len(state['execution_trace']) + 1,
            'node': node,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'duration_ms': duration_ms,
            'status': 'success',
            'details': details or {}
        })
    
    def _scan_content(self, state: CredsInspectState) -> CredsInspectState:
        """
        Node 1: Scan and extract content structure
        """
        start_time = time.time()
        self.logger.info("Node: Scanning content...")
        
        try:
            content_text = state['content_text']
            
            # Extract basic structure
            extracted = {
                'text_length': len(content_text),
                'line_count': len(content_text.split('\n')),
                'has_code_blocks': bool(re.search(r'```|<code>|<pre>', content_text)),
                'has_urls': bool(re.search(r'https?://', content_text)),
                'sections': self._extract_sections(content_text)
            }
            
            state['extracted_content'] = extracted
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='scan_content',
                action='Extracted content structure',
                details={
                    'text_length': extracted['text_length'],
                    'line_count': extracted['line_count'],
                    'sections': len(extracted['sections'])
                },
                duration_ms=duration
            )
            
            self.logger.info(f"✓ Content scanned: {extracted['text_length']} chars")
            
        except Exception as e:
            self.logger.error(f"✗ Content scanning failed: {e}")
            state['extracted_content'] = {}
        
        return state
    
    def _extract_sections(self, text: str) -> List[Dict[str, str]]:
        """Extract code blocks and sections"""
        sections = []
        
        # Extract code blocks
        code_pattern = r'```(\w+)?\n(.*?)```'
        for match in re.finditer(code_pattern, text, re.DOTALL):
            language = match.group(1) or 'unknown'
            code = match.group(2)
            sections.append({
                'type': 'code_block',
                'language': language,
                'content': code,
                'line_start': text[:match.start()].count('\n') + 1
            })
        
        # Extract pre/code tags
        html_code_pattern = r'<(?:pre|code)>(.*?)</(?:pre|code)>'
        for match in re.finditer(html_code_pattern, text, re.DOTALL):
            sections.append({
                'type': 'html_code',
                'content': match.group(1),
                'line_start': text[:match.start()].count('\n') + 1
            })
        
        return sections
    
    def _detect_credentials(self, state: CredsInspectState) -> CredsInspectState:
        """
        Node 2: Detect credentials using patterns + AI
        """
        start_time = time.time()
        self.logger.info("Node: Detecting credentials...")
        
        try:
            content_text = state['content_text']
            detected = []
            
            # Pattern-based detection
            for cred_type, pattern in self.CREDENTIAL_PATTERNS.items():
                matches = list(re.finditer(pattern, content_text, re.MULTILINE))
                for match in matches:
                    # Get context around match
                    start_pos = max(0, match.start() - 50)
                    end_pos = min(len(content_text), match.end() + 50)
                    context = content_text[start_pos:end_pos]
                    
                    detected.append({
                        'type': cred_type,
                        'value': match.group(0)[:20] + '...' if len(match.group(0)) > 20 else match.group(0),
                        'position': match.start(),
                        'line': content_text[:match.start()].count('\n') + 1,
                        'context': context,
                        'detection_method': 'pattern',
                        'confidence': 0.9
                    })
            
            # AI-enhanced detection for context-based credentials
            if len(detected) < 50:  # Only if not too many already found
                ai_detected = self._ai_credential_detection(content_text)
                detected.extend(ai_detected)
            
            # Remove duplicates
            detected = self._deduplicate_findings(detected)
            
            state['detected_credentials'] = detected
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='detect_credentials',
                action='Detected credentials',
                details={
                    'total_found': len(detected),
                    'pattern_based': sum(1 for d in detected if d['detection_method'] == 'pattern'),
                    'ai_based': sum(1 for d in detected if d['detection_method'] == 'ai')
                },
                duration_ms=duration
            )
            
            self.logger.info(f"✓ Found {len(detected)} potential credentials")
            
        except Exception as e:
            self.logger.error(f"✗ Credential detection failed: {e}")
            state['detected_credentials'] = []
        
        return state
    
    def _ai_credential_detection(self, text: str) -> List[Dict[str, Any]]:
        """Use AI to detect credentials that patterns might miss"""
        try:
            # Truncate if too long
            text_sample = text[:3000] if len(text) > 3000 else text
            
            prompt = f"""
Analyze this text for exposed credentials that might not match common patterns.

Text:
{text_sample}

Look for:
1. Passwords in comments or configuration
2. API keys in non-standard formats
3. Connection strings
4. Authentication tokens
5. Secrets in variable assignments

Return ONLY a JSON array:
[
  {{
    "type": "credential_type",
    "value_preview": "first_15_chars",
    "context": "surrounding_text_50_chars",
    "confidence": 0.0-1.0
  }}
]

If no credentials found, return: []
"""
            
            response = self.llm.invoke([
                {"role": "system", "content": "You are a security expert detecting exposed credentials."},
                {"role": "user", "content": prompt}
            ])
            
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            
            ai_results = json.loads(content)
            
            # Format results
            formatted = []
            for result in ai_results:
                formatted.append({
                    'type': result.get('type', 'unknown'),
                    'value': result.get('value_preview', ''),
                    'context': result.get('context', ''),
                    'detection_method': 'ai',
                    'confidence': result.get('confidence', 0.7),
                    'position': 0,
                    'line': 0
                })
            
            return formatted
            
        except Exception as e:
            self.logger.warning(f"AI credential detection failed: {e}")
            return []
    
    def _deduplicate_findings(self, findings: List[Dict]) -> List[Dict]:
        """Remove duplicate credential findings"""
        seen = set()
        unique = []
        
        for finding in findings:
            key = (finding['type'], finding['value'], finding.get('line', 0))
            if key not in seen:
                seen.add(key)
                unique.append(finding)
        
        return unique
    
    def _assess_risk(self, state: CredsInspectState) -> CredsInspectState:
        """
        Node 3: Assess risk and severity of findings
        """
        start_time = time.time()
        self.logger.info("Node: Assessing risk...")
        
        try:
            credentials = state['detected_credentials']
            
            if not credentials:
                state['risk_assessment'] = {
                    'overall_risk': 'low',
                    'high_risk_count': 0,
                    'medium_risk_count': 0,
                    'low_risk_count': 0,
                    'critical_findings': []
                }
                return state
            
            # Use AI for risk assessment
            prompt = f"""
Assess the security risk of these {len(credentials)} detected credentials:

Credentials:
{json.dumps([{'type': c['type'], 'context': c.get('context', '')[:100]} for c in credentials[:20]], indent=2)}

Content Type: {state['content_type']}
Source: {state['content_metadata'].get('source', 'Unknown')}

Provide risk assessment with:
1. Severity for each (High/Medium/Low)
2. Overall risk level
3. Exposure scope (public/internal/private)
4. Active vs expired assessment
5. Compliance impact

Return ONLY a JSON object:
{{
  "overall_risk": "high|medium|low",
  "credential_risks": [
    {{
      "credential_index": 0,
      "severity": "high|medium|low",
      "is_active": true|false,
      "exposure_scope": "public|internal|private",
      "compliance_risk": "description"
    }}
  ],
  "critical_findings": ["finding1", "finding2"],
  "compliance_violations": ["violation1"]
}}
"""
            
            response = self.llm.invoke([
                {"role": "system", "content": "You are a cybersecurity risk assessor."},
                {"role": "user", "content": prompt}
            ])
            
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            
            risk_assessment = json.loads(content)
            
            # Merge risk data back into credentials
            for i, cred_risk in enumerate(risk_assessment.get('credential_risks', [])):
                idx = cred_risk.get('credential_index', i)
                if idx < len(credentials):
                    credentials[idx].update({
                        'severity': cred_risk.get('severity', 'medium'),
                        'is_active': cred_risk.get('is_active', True),
                        'exposure_scope': cred_risk.get('exposure_scope', 'unknown')
                    })
            
            # Calculate counts
            risk_counts = {
                'high_risk_count': sum(1 for c in credentials if c.get('severity') == 'high'),
                'medium_risk_count': sum(1 for c in credentials if c.get('severity') == 'medium'),
                'low_risk_count': sum(1 for c in credentials if c.get('severity') == 'low')
            }
            
            risk_assessment.update(risk_counts)
            state['risk_assessment'] = risk_assessment
            state['detected_credentials'] = credentials
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='assess_risk',
                action='Assessed risk levels',
                details=risk_counts,
                duration_ms=duration
            )
            
            self.logger.info(f"✓ Risk assessment complete: {risk_assessment['overall_risk']}")
            
        except Exception as e:
            self.logger.error(f"✗ Risk assessment failed: {e}")
            state['risk_assessment'] = {'overall_risk': 'unknown'}
        
        return state
    
    def _generate_remediation(self, state: CredsInspectState) -> CredsInspectState:
        """
        Node 4: Generate remediation guidance
        """
        start_time = time.time()
        self.logger.info("Node: Generating remediation...")
        
        try:
            credentials = state['detected_credentials']
            risk_assessment = state['risk_assessment']
            
            if not credentials:
                state['remediation_plan'] = []
                return state
            
            # Group by severity
            high_risk = [c for c in credentials if c.get('severity') == 'high']
            
            prompt = f"""
Generate remediation plan for these exposed credentials:

High Risk Credentials: {len(high_risk)}
Total Credentials: {len(credentials)}
Overall Risk: {risk_assessment.get('overall_risk', 'unknown')}

For the top {min(10, len(credentials))} findings, provide:
1. Immediate actions (revoke, rotate)
2. Verification steps
3. Prevention measures
4. Owner notification template
5. Timeline

Return ONLY a JSON array:
[
  {{
    "credential_type": "type",
    "priority": "immediate|urgent|normal",
    "immediate_actions": ["action1", "action2"],
    "verification_steps": ["step1"],
    "prevention": ["measure1"],
    "notification_template": "Dear ...",
    "timeline": "X hours/days"
  }}
]
"""
            
            response = self.llm.invoke([
                {"role": "system", "content": "You are a security remediation specialist."},
                {"role": "user", "content": prompt}
            ])
            
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            
            remediation_plan = json.loads(content)
            state['remediation_plan'] = remediation_plan
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='generate_remediation',
                action='Generated remediation plan',
                details={'plan_items': len(remediation_plan)},
                duration_ms=duration
            )
            
            self.logger.info(f"✓ Remediation plan created: {len(remediation_plan)} items")
            
        except Exception as e:
            self.logger.error(f"✗ Remediation generation failed: {e}")
            state['remediation_plan'] = []
        
        return state
    
    def _create_report(self, state: CredsInspectState) -> CredsInspectState:
        """
        Node 5: Create executive report
        """
        start_time = time.time()
        self.logger.info("Node: Creating report...")
        
        try:
            credentials = state['detected_credentials']
            risk_assessment = state['risk_assessment']
            remediation = state['remediation_plan']
            
            prompt = f"""
Create an executive security report:

Findings Summary:
- Total credentials found: {len(credentials)}
- High risk: {risk_assessment.get('high_risk_count', 0)}
- Medium risk: {risk_assessment.get('medium_risk_count', 0)}
- Low risk: {risk_assessment.get('low_risk_count', 0)}
- Overall risk: {risk_assessment.get('overall_risk', 'unknown')}

Remediation Items: {len(remediation)}

Create a concise executive summary covering:
1. Key findings
2. Security impact
3. Compliance implications
4. Recommended immediate actions
5. Prevention strategy

Return as plain text (no JSON).
"""
            
            response = self.llm.invoke([
                {"role": "system", "content": "You are a CISO writing a security report."},
                {"role": "user", "content": prompt}
            ])
            
            state['executive_report'] = response.content
            state['processing_status'] = 'completed'
            
            # Add trace
            duration = int((time.time() - start_time) * 1000)
            self._add_trace_step(
                state,
                node='create_report',
                action='Created executive report',
                details={'report_length': len(response.content)},
                duration_ms=duration
            )
            
            self.logger.info("✓ Executive report created")
            
        except Exception as e:
            self.logger.error(f"✗ Report creation failed: {e}")
            state['executive_report'] = "Error generating report"
            state['processing_status'] = 'failed'
        
        return state
    
    def scan_content(self, scan_id: str, content_text: str, 
                    content_type: str = 'text',
                    metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point: Scan content for credentials
        
        Args:
            scan_id: Unique scan identifier
            content_text: Content to scan
            content_type: Type of content (confluence_page, attachment, text)
            metadata: Optional metadata
        
        Returns:
            Complete scan results
        """
        self.logger.info(f"Scanning content: {scan_id}")
        
        # Initialize state
        initial_state = CredsInspectState(
            scan_id=scan_id,
            content_text=content_text,
            content_type=content_type,
            content_metadata=metadata or {},
            extracted_content=None,
            detected_credentials=None,
            risk_assessment=None,
            remediation_plan=None,
            executive_report=None,
            execution_trace=[],
            processing_status='processing'
        )
        
        # Execute workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            # Format result
            result = {
                'scan_id': scan_id,
                'metadata': metadata or {},
                'content_type': content_type,
                'scan_summary': {
                    'credentials_found': len(final_state.get('detected_credentials', [])),
                    'high_risk': final_state.get('risk_assessment', {}).get('high_risk_count', 0),
                    'medium_risk': final_state.get('risk_assessment', {}).get('medium_risk_count', 0),
                    'low_risk': final_state.get('risk_assessment', {}).get('low_risk_count', 0),
                    'overall_risk': final_state.get('risk_assessment', {}).get('overall_risk', 'unknown')
                },
                'detected_credentials': final_state.get('detected_credentials', []),
                'risk_assessment': final_state.get('risk_assessment', {}),
                'remediation_plan': final_state.get('remediation_plan', []),
                'executive_report': final_state.get('executive_report', ''),
                'execution_trace': final_state.get('execution_trace', []),
                'status': final_state.get('processing_status', 'completed'),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("✓ Content scan complete")
            return result
            
        except Exception as e:
            self.logger.error(f"✗ Content scan failed: {e}")
            raise
    
    def get_workflow_graph(self) -> Dict[str, Any]:
        """Get workflow structure for visualization"""
        nodes = [
            {"id": "scan_content", "name": "Scan Content", "type": "node",
             "description": "Extract and parse content structure"},
            {"id": "detect_credentials", "name": "Detect Credentials", "type": "node",
             "description": "Identify exposed credentials using patterns and AI"},
            {"id": "assess_risk", "name": "Assess Risk", "type": "node",
             "description": "Evaluate severity and exposure impact"},
            {"id": "generate_remediation", "name": "Generate Remediation", "type": "node",
             "description": "Create action plans and guidance"},
            {"id": "create_report", "name": "Create Report", "type": "node",
             "description": "Generate executive security report"}
        ]
        
        edges = [
            {"source": "scan_content", "target": "detect_credentials"},
            {"source": "detect_credentials", "target": "assess_risk"},
            {"source": "assess_risk", "target": "generate_remediation"},
            {"source": "generate_remediation", "target": "create_report"}
        ]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "workflow_type": "Credential Detection Pipeline",
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }


# Initialize agent
def create_agent():
    """Factory function to create agent instance"""
    try:
        return CredsInspectAgent()
    except Exception as e:
        logging.error(f"Failed to initialize agent: {e}")
        return None
