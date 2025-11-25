"""
Quick test script to verify execution trace functionality
"""
from smarttech_ticket_agent import SmartTechTicketAgent, MOCK_TSD_TICKETS

# Initialize agent
agent = SmartTechTicketAgent()

# Classify a ticket
print("\nClassifying ticket...")
result = agent.classify_ticket(MOCK_TSD_TICKETS[1])

# Display trace summary
trace = result.get('execution_trace', [])
print(f"\n{'='*60}")
print("EXECUTION TRACE SUMMARY")
print(f"{'='*60}")
print(f"Total Steps: {len(trace)}")
print(f"Ticket ID: {result['ticket_id']}")
print(f"Intent: {result['detected_intent']}")
print(f"Confidence: {result['confidence']:.0%}")
print(f"Self-Service: {result['self_service_eligible']}")
print(f"\nWorkflow Steps:")
for step in trace:
    status_icon = "✓" if step['status'] == 'success' else "✗"
    print(f"  {status_icon} Step {step['step']}: {step['node']}")
    print(f"    Action: {step['action']}")
    print(f"    Duration: {step['duration_ms']}ms")
    print(f"    Status: {step['status']}")
    if 'llm_call' in step.get('details', {}):
        print(f"    LLM Call: {step['details']['llm_call']['model']}")
    print()

total_duration = sum(s['duration_ms'] for s in trace)
print(f"Total Duration: {total_duration}ms")
print(f"{'='*60}\n")
