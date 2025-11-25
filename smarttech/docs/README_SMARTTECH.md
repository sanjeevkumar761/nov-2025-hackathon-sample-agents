# SmartTech AI-Enabled TSD Ticket Classification System

## Overview

This LangGraph-based agent demonstrates an AI-powered solution for SmartTech's TSD (Technical Support Desk) ticket classification system. It moves beyond basic keyword matching to use LLM-based intent detection, enabling more accurate identification of self-service opportunities and reducing helpdesk load.

## Business Problem

**Current State:**
- SmartTech uses basic keyword matching and deterministic logic
- Limited ability to detect user intent
- Many tickets that could be self-resolved go to helpdesk
- Helpdesk resources are stretched

**Desired State:**
- Use AI/LLM to detect user intent accurately
- Surface more self-service opportunities
- Reduce tickets going to helpdesk
- Improve user satisfaction with faster resolution

## Solution Architecture

### LangGraph Workflow

```
┌─────────────────┐
│  Ticket Input   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Analyze Intent  │ ◄─── Azure OpenAI LLM
│  (LLM-based)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check Self-     │
│ Service         │
│ Eligibility     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Find Knowledge  │
│ Base Articles   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Recommend       │
│ Routing         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Classification  │
│ Result          │
└─────────────────┘
```

### Key Components

1. **Intent Detection (LLM-Powered)**
   - Uses Azure OpenAI to understand ticket content
   - Classifies into 10+ intent categories
   - Provides confidence scores

2. **Self-Service Eligibility Check**
   - Determines if ticket can be resolved without helpdesk
   - Uses confidence thresholds per intent type
   - Considers complexity and urgency

3. **Knowledge Base Matching**
   - Maps intents to relevant KB articles
   - Provides resolution time estimates
   - Includes success rate metrics

4. **Routing Recommendations**
   - SELF_SERVICE: Can be resolved by user
   - TIER_1_HELPDESK: Standard support
   - TIER_2_HELPDESK: Specialized support
   - MANUAL_REVIEW: Intent unclear

## Features

### Intent Categories Supported

| Intent | Description | Self-Service Eligible |
|--------|-------------|----------------------|
| `password_reset` | Password-related issues | ✓ |
| `vpn_issues` | VPN connection problems | ✓ |
| `email_setup` | Email configuration | ✓ |
| `network_connectivity` | WiFi/network issues | ✓ |
| `software_request` | Software installation | ✓ |
| `mfa_setup` | Multi-factor auth setup | ✓ |
| `performance` | Computer performance | ✓ |
| `access_request` | Access permissions | ✓ |
| `hardware` | Physical equipment issues | ✗ |
| `outlook_issues` | Outlook problems | Conditional |

### Mock Data Included

- **10 Sample TSD Tickets** covering common support scenarios
- **8 Knowledge Base Articles** with step-by-step instructions
- Success rates and average resolution times for each KB article

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Azure OpenAI account with deployed model
- Visual Studio Code (optional)

### Installation

1. **Clone/Navigate to the project directory:**
   ```bash
   cd c:\Users\sanjeku\vscoderepos\UBS\langgraph-agents
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Azure OpenAI:**
   
   Create a `.env` file with your Azure OpenAI credentials:
   ```env
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_API_VERSION=2024-08-01-preview
   ```

### Running the Agent

**Process all mock tickets:**
```bash
python smarttech_ticket_agent.py
```

**Expected Output:**
- Individual classification reports for each ticket
- Summary statistics showing:
  - Total tickets processed
  - Self-service eligibility rate
  - Average confidence scores
  - Routing distribution
  - Intent distribution

## Usage Examples

### Example 1: Batch Processing

```python
from smarttech_ticket_agent import SmartTechTicketAgent, MOCK_TSD_TICKETS

# Initialize agent
agent = SmartTechTicketAgent()

# Process all tickets
results = agent.batch_classify_tickets(MOCK_TSD_TICKETS)

# Get statistics
stats = agent.generate_summary_statistics(results)
print(f"Self-service eligible: {stats['self_service_percentage']:.1f}%")
```

### Example 2: Single Ticket Classification

```python
# Create custom ticket
custom_ticket = {
    "ticket_id": "TSD-2024-999",
    "subject": "Cannot login to portal",
    "description": "I keep getting 'invalid credentials' error when trying to login",
    "category": "Account",
    "priority": "High",
    "user": "test.user@smarttech.com",
    "created_at": "2024-11-22 10:00:00"
}

# Classify
result = agent.classify_ticket(custom_ticket)
agent.print_classification_report(result)
```

### Example 3: Custom Workflow

```python
# Access individual workflow components
state = {
    "ticket": custom_ticket,
    "intent": None,
    "confidence": 0.0,
    "self_service_eligible": False,
    "knowledge_base_articles": [],
    "routing_recommendation": "",
    "analysis": "",
    "messages": []
}

# Run workflow
result = agent.workflow.invoke(state, config={"configurable": {"thread_id": "custom-001"}})
```

## Sample Output

```
============================================================
CLASSIFICATION REPORT
============================================================
Ticket ID:     TSD-2024-002
Subject:       Forgot VPN password
Intent:        vpn_issues
Confidence:    92%
Self-Service:  ✓ YES
Routing:       SELF_SERVICE

Recommended KB Articles:
  • KB-002: VPN Setup and Password Reset
    Success Rate: 90% | Avg Time: 10 minutes

Analysis: User explicitly states they forgot VPN password, 
which is a clear intent for password reset functionality.
============================================================

SUMMARY STATISTICS
============================================================
Total Tickets Processed: 10
Self-Service Eligible: 8 (80.0%)
Average Confidence: 87%

Routing Distribution:
  • SELF_SERVICE: 8 (80.0%)
  • TIER_1_HELPDESK: 2 (20.0%)

💡 Insight: 8 tickets (80.0%) could be resolved through 
   self-service, reducing helpdesk load significantly!
```

## Benefits & Impact

### Quantitative Benefits
- **80%** of sample tickets identified as self-service eligible
- **87%** average confidence in classifications
- Estimated **60-70%** reduction in helpdesk tickets (based on industry benchmarks)

### Qualitative Benefits
- **Improved User Experience**: Faster resolution through self-service
- **Better Resource Allocation**: Helpdesk focuses on complex issues
- **24/7 Availability**: Self-service works outside business hours
- **Scalability**: Handles increased ticket volume without linear cost increase
- **Data Insights**: Understanding common issues for process improvement

## Customization Guide

### Adding New Intent Categories

```python
# In smarttech_ticket_agent.py

# 1. Add to INTENT_CATEGORIES dictionary
INTENT_CATEGORIES["new_intent"] = ["keyword1", "keyword2"]

# 2. Update the LLM prompt in _analyze_intent()
# Add your new category to the "Available Intent Categories" list

# 3. Add knowledge base article
KNOWLEDGE_BASE["new_kb_article"] = {
    "title": "How to Handle New Intent",
    "article_id": "KB-009",
    "steps": [...],
    "avg_resolution_time": "5 minutes",
    "success_rate": 90
}

# 4. Map intent to KB in _find_knowledge_base_articles()
intent_to_kb["new_intent"] = ["new_kb_article"]
```

### Adjusting Confidence Thresholds

```python
# In _check_self_service_eligibility() method
self_service_intents = {
    "password_reset": 0.7,  # Adjust threshold (0.0 - 1.0)
    "vpn_issues": 0.7,
    # ... add your adjustments
}
```

### Integrating with Real Systems

1. **Replace Mock Data:**
   - Connect to actual ticket system API
   - Query real knowledge base
   - Use production user data

2. **Add Persistence:**
   - Save classifications to database
   - Track metrics over time
   - Build reporting dashboards

3. **Webhook Integration:**
   - Trigger on new ticket creation
   - Send results to ticketing system
   - Update ticket status automatically

## Advanced Features

### Tools Available

```python
@tool
def get_ticket_by_id(ticket_id: str) -> str:
    """Retrieve ticket details by ID"""
    
@tool
def get_knowledge_base_article(article_id: str) -> str:
    """Get KB article details"""
    
@tool
def search_tickets(query: str) -> str:
    """Search tickets by keyword"""
```

### State Management

The agent uses LangGraph's state management with memory:
- Tracks conversation history per ticket
- Maintains classification context
- Enables multi-turn interactions

## Performance Considerations

- **LLM Calls**: One LLM call per ticket (intent detection)
- **Response Time**: ~2-3 seconds per ticket
- **Batch Processing**: Process multiple tickets efficiently
- **Cost**: Depends on Azure OpenAI pricing and token usage

## Troubleshooting

### Common Issues

1. **"Missing Azure OpenAI configuration" error**
   - Ensure `.env` file exists with correct credentials
   - Verify environment variables are loaded

2. **Low confidence scores**
   - Adjust temperature in LLM initialization (default: 0.3)
   - Improve ticket descriptions with more details
   - Fine-tune prompt in `_analyze_intent()`

3. **Incorrect intent detection**
   - Review and expand INTENT_CATEGORIES keywords
   - Add more examples to the LLM prompt
   - Consider fine-tuning the model

## Future Enhancements

- [ ] Multi-language support
- [ ] Sentiment analysis for priority adjustment
- [ ] Integration with ticketing systems (ServiceNow, Jira)
- [ ] Real-time dashboard for monitoring
- [ ] A/B testing framework
- [ ] Feedback loop for continuous improvement
- [ ] Automated KB article creation
- [ ] Predictive ticket routing
- [ ] SLA prediction and management

## Technical Stack

- **Framework**: LangGraph 0.2.0+
- **LLM**: Azure OpenAI (GPT-4 recommended)
- **Language**: Python 3.10+
- **Key Libraries**:
  - `langgraph` - Workflow orchestration
  - `langchain-openai` - Azure OpenAI integration
  - `python-dotenv` - Environment configuration

## Support & Contact

For questions or issues:
- Review the code comments in `smarttech_ticket_agent.py`
- Check the example in `simple_langgraph_agent.py`
- Refer to LangGraph documentation: https://langchain-ai.github.io/langgraph/

## License

This is a demonstration project for SmartTech's AI enablement initiative.

---

**Created**: November 2024  
**Version**: 1.0.0  
**Status**: Demo/POC
