# SmartTech Agent - Execution Trace Feature

## Overview

The SmartTech TSD Classification Agent now includes **detailed execution tracing** that shows exactly how the AI agent processes each ticket, including:

- ✅ **Workflow Steps** - Each node in the LangGraph workflow
- 🔧 **Tool Invocations** - LLM calls and knowledge base searches
- 📊 **State Transitions** - How data flows between nodes
- ⏱️ **Performance Metrics** - Duration of each step
- 🎯 **Decision Logic** - Why certain decisions were made

## What Gets Tracked

### Step 1: Analyze Intent
- **Action**: Azure OpenAI LLM analyzes ticket content
- **Details Captured**:
  - Model used (Azure OpenAI)
  - Prompt length
  - Number of messages sent
  - Detected intent
  - Confidence score
  - AI reasoning/explanation
- **Duration**: Typically 1-2 seconds

### Step 2: Check Self-Service Eligibility
- **Action**: Evaluates if ticket can be self-serviced
- **Details Captured**:
  - Intent being evaluated
  - Confidence score
  - Eligibility decision (YES/NO)
  - Reason for decision
  - Confidence threshold checked
- **Duration**: < 1ms (rule-based)

### Step 3: Find Knowledge Base Articles
- **Action**: Searches KB for relevant articles
- **Details Captured**:
  - Intent used for search
  - KB keys searched
  - Number of articles found
  - Article IDs returned
- **Duration**: < 1ms (dictionary lookup)

### Step 4: Recommend Routing
- **Action**: Determines optimal routing
- **Details Captured**:
  - Final routing decision
  - Recommendation text
  - Self-service eligibility
  - Final confidence
  - KB articles available
- **Duration**: < 1ms (rule-based)

## Example Execution Trace

```json
{
  "step": 1,
  "node": "analyze_intent",
  "action": "Analyzing ticket intent using Azure OpenAI",
  "timestamp": "2025-11-22T01:17:03.345486",
  "duration_ms": 1378,
  "status": "success",
  "details": {
    "llm_call": {
      "model": "Azure OpenAI",
      "prompt_length": 1185,
      "messages_sent": 1
    },
    "result": {
      "intent": "email_setup",
      "confidence": 0.95,
      "reasoning": "The user is attempting to configure their work email..."
    }
  }
}
```

## UI Visualization

The execution trace is displayed as a **visual timeline** in the web UI:

### Features:
1. **Timeline View**: Vertical timeline showing each step
2. **Status Indicators**: Green checkmarks for success, red alerts for errors
3. **Step Details**: Expandable sections with full execution details
4. **Performance Metrics**: Duration displayed for each step
5. **Color-Coded Cards**: Different colors for different types of information
   - 🔵 Blue: LLM invocations
   - 🟢 Green: Results and outputs
   - 🟣 Purple: Eligibility checks
   - 🟡 Yellow: Knowledge base operations
   - 🔷 Indigo: Routing decisions

### Summary Statistics:
- Total workflow steps
- Successful steps
- Total execution duration

## API Response Format

The execution trace is included in every classification response:

```json
{
  "ticket_id": "TSD-2024-001",
  "subject": "Cannot access email on mobile device",
  "detected_intent": "email_setup",
  "confidence": 0.95,
  "self_service_eligible": true,
  "routing": "SELF_SERVICE",
  "knowledge_base_articles": [...],
  "analysis": "The user is attempting...",
  "execution_trace": [
    {
      "step": 1,
      "node": "analyze_intent",
      ...
    },
    {
      "step": 2,
      "node": "check_self_service_eligibility",
      ...
    },
    ...
  ]
}
```

## Use Cases

### 1. **Debugging & Troubleshooting**
- See exactly where the agent made decisions
- Identify if LLM responses are accurate
- Track down performance bottlenecks

### 2. **Transparency & Explainability**
- Show users how AI reached its conclusion
- Build trust with stakeholders
- Audit trail for compliance

### 3. **Performance Optimization**
- Identify slow steps
- Optimize prompts based on response times
- Monitor LLM token usage

### 4. **Training & Documentation**
- Demonstrate how the agent works
- Train support staff on AI capabilities
- Create better documentation

### 5. **Quality Assurance**
- Verify correct workflow execution
- Catch errors or unexpected behavior
- Validate confidence thresholds

## Viewing Execution Traces

### In the Web UI:
1. Submit or select a ticket for classification
2. Wait for results to load
3. Scroll down below the classification results
4. View the "Agent Execution Trace" section
5. Expand details for each step

### Via API:
```bash
curl -X POST http://localhost:8000/api/v1/tickets/classify \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TEST-001",
    "subject": "Password reset needed",
    "description": "I forgot my password",
    "category": "Account",
    "priority": "High",
    "user": "test@smarttech.com"
  }'
```

The response will include the `execution_trace` array.

### In Python:
```python
from smarttech_ticket_agent import SmartTechTicketAgent, MOCK_TSD_TICKETS

agent = SmartTechTicketAgent()
result = agent.classify_ticket(MOCK_TSD_TICKETS[0])

# Access execution trace
for step in result['execution_trace']:
    print(f"Step {step['step']}: {step['action']}")
    print(f"  Duration: {step['duration_ms']}ms")
    print(f"  Status: {step['status']}")
    print()
```

## Performance Impact

The execution trace adds **minimal overhead**:
- Memory: ~2-5 KB per classification
- CPU: Negligible (simple dictionary operations)
- Latency: < 1ms additional processing time

The trace data is only stored in memory for the duration of the request and is not persisted.

## Privacy & Security

### What's NOT Included:
- ❌ API keys or credentials
- ❌ Full LLM prompts (only length)
- ❌ Full LLM responses (only extracted data)
- ❌ User personal information beyond ticket data

### What IS Included:
- ✅ Node names and actions
- ✅ Timestamps and durations
- ✅ Intent detection results
- ✅ Decision reasoning
- ✅ KB article references

## Customization

### Disable Execution Trace:
To disable trace collection, modify the agent initialization:

```python
# In smarttech_ticket_agent.py
initial_state = {
    # ... other fields ...
    "execution_trace": []  # Comment this line or set to None
}
```

### Add Custom Trace Data:
```python
trace_entry["details"]["custom_field"] = "custom_value"
```

### Filter Trace Data:
```python
# Only include specific fields
filtered_trace = [
    {
        "step": t["step"],
        "node": t["node"],
        "duration_ms": t["duration_ms"]
    }
    for t in result["execution_trace"]
]
```

## Future Enhancements

Potential improvements:
- 📊 Export trace to monitoring tools (Datadog, New Relic)
- 💾 Store traces in database for analysis
- 📈 Aggregate trace data for insights
- 🔍 Search and filter historical traces
- 📝 Generate reports from trace data
- 🎨 Different visualization modes (graph, table)
- 🔔 Alerts on slow or failed steps

## Troubleshooting

### Trace Not Appearing:
1. Ensure you're using the updated agent code
2. Check that `execution_trace` is in the initial state
3. Verify API is returning trace data
4. Check browser console for errors

### Missing Trace Details:
- Ensure each node appends its trace entry
- Check for exceptions that might skip trace logging
- Verify state is properly passed between nodes

### UI Not Showing Trace:
- Check that ExecutionTrace component is imported
- Verify trace data structure matches TypeScript types
- Check for console errors in browser

---

**The execution trace feature provides complete visibility into the AI agent's decision-making process, making the system more transparent, debuggable, and trustworthy!** 🚀
