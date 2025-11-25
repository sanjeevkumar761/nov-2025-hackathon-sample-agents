"""
Test script for Jinja2 template-based prompts
"""

from smarttech_ticket_agent import SmartTechTicketAgent, MOCK_TSD_TICKETS

def test_template_prompt():
    """Test that the Jinja2 template is loaded and renders correctly"""
    
    print("\n" + "="*60)
    print("Testing Jinja2 Template-Based Prompts")
    print("="*60)
    
    # Initialize agent (should load template)
    agent = SmartTechTicketAgent()
    
    # Test with one ticket
    test_ticket = MOCK_TSD_TICKETS[0]
    
    print(f"\nTesting with ticket: {test_ticket['ticket_id']}")
    print(f"Subject: {test_ticket['subject']}")
    
    # Classify the ticket
    result = agent.classify_ticket(test_ticket)
    
    # Print results
    agent.print_classification_report(result)
    
    print("\n✓ Template-based prompt test completed successfully!")
    print("="*60)

if __name__ == "__main__":
    test_template_prompt()
