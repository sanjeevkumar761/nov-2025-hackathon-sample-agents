"""
Example: Using custom prompt templates and configurations

This script demonstrates how to:
1. Use different prompt templates
2. Customize intent categories
3. Create prompt variations for A/B testing
"""

from smarttech_ticket_agent import SmartTechTicketAgent, MOCK_TSD_TICKETS
from pathlib import Path

def example_default_template():
    """Example 1: Using the default template"""
    print("\n" + "="*60)
    print("Example 1: Default Template")
    print("="*60)
    
    agent = SmartTechTicketAgent()
    result = agent.classify_ticket(MOCK_TSD_TICKETS[0])
    print(f"Intent: {result['detected_intent']}, Confidence: {result['confidence']:.0%}")


def example_custom_template():
    """Example 2: Creating and using a custom template"""
    print("\n" + "="*60)
    print("Example 2: Custom Template (if exists)")
    print("="*60)
    
    # Check if custom template exists
    custom_template = Path("prompts/intent_detection_v2.j2")
    
    if custom_template.exists():
        agent = SmartTechTicketAgent(prompt_template_path="prompts/intent_detection_v2.j2")
        result = agent.classify_ticket(MOCK_TSD_TICKETS[0])
        print(f"Intent: {result['detected_intent']}, Confidence: {result['confidence']:.0%}")
    else:
        print("Create a custom template at prompts/intent_detection_v2.j2 to test this")


def example_render_template_only():
    """Example 3: Preview rendered template without calling LLM"""
    print("\n" + "="*60)
    print("Example 3: Preview Rendered Template")
    print("="*60)
    
    from jinja2 import Environment, FileSystemLoader
    
    # Initialize Jinja2
    env = Environment(loader=FileSystemLoader("prompts"))
    template = env.get_template("intent_detection.j2")
    
    # Define test data
    ticket = MOCK_TSD_TICKETS[1]  # VPN ticket
    intent_categories = {
        "password_reset": "Password-related issues or reset requests",
        "vpn_issues": "VPN connection or access problems",
        "email_setup": "Email configuration on devices",
    }
    
    # Render template
    rendered_prompt = template.render(
        company_name="SmartTech",
        ticket=ticket,
        intent_categories=intent_categories
    )
    
    print("\nRendered Prompt Preview:")
    print("-" * 60)
    print(rendered_prompt)
    print("-" * 60)


def example_batch_with_template():
    """Example 4: Batch processing with template"""
    print("\n" + "="*60)
    print("Example 4: Batch Processing")
    print("="*60)
    
    agent = SmartTechTicketAgent()
    
    # Process first 3 tickets
    results = agent.batch_classify_tickets(MOCK_TSD_TICKETS[:3])
    
    print("\nBatch Results:")
    for result in results:
        print(f"  • {result['ticket_id']}: {result['detected_intent']} ({result['confidence']:.0%})")


def example_template_benefits():
    """Print benefits of using Jinja2 templates"""
    print("\n" + "="*60)
    print("Benefits of Jinja2 Templates")
    print("="*60)
    
    benefits = [
        "✓ Centralized prompt management",
        "✓ Easy A/B testing of prompt variations",
        "✓ Version control friendly (separate .j2 files)",
        "✓ Dynamic content based on ticket properties",
        "✓ Consistent formatting across prompts",
        "✓ Non-technical users can edit prompts",
        "✓ Template inheritance and reuse",
        "✓ No code changes needed for prompt updates"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")
    
    print("\n" + "="*60)
    print("Template Location: prompts/intent_detection.j2")
    print("Config Location: prompts/prompt_config.json")
    print("Documentation: prompts/README.md")
    print("="*60)


if __name__ == "__main__":
    # Run all examples
    example_default_template()
    example_custom_template()
    example_render_template_only()
    example_batch_with_template()
    example_template_benefits()
    
    print("\n✓ All examples completed!\n")
