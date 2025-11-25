# Jinja2 Template System Implementation

## Overview

The SmartTech TSD Agent now uses **Jinja2 templates** for all LLM prompts, making them:
- ✅ Configurable without code changes
- ✅ Version-controllable
- ✅ Easy to A/B test
- ✅ Maintainable by non-developers

## What Changed

### 1. Added Dependencies
```bash
pip install jinja2
```

### 2. New Directory Structure
```
UBS/langgraph-agents/
├── prompts/
│   ├── intent_detection.j2              # Main template
│   ├── base_intent_detection.j2         # Base template for inheritance
│   ├── intent_detection_urgent.j2       # Urgent ticket variant
│   ├── prompt_config.json               # Configuration file
│   └── README.md                        # Documentation
├── smarttech_ticket_agent.py            # Updated with Jinja2 support
├── test_template_prompt.py              # Test script
└── examples_prompt_templates.py         # Usage examples
```

### 3. Code Changes

**Before (Hardcoded Prompt):**
```python
prompt = f"""You are an expert IT support ticket classifier...
Ticket: {ticket['subject']}
...
"""
```

**After (Template-Based):**
```python
template = self.jinja_env.get_template("intent_detection.j2")
prompt = template.render(
    company_name="SmartTech",
    ticket=ticket,
    intent_categories=intent_categories
)
```

## Usage Examples

### Basic Usage
```python
from smarttech_ticket_agent import SmartTechTicketAgent

# Uses default template (prompts/intent_detection.j2)
agent = SmartTechTicketAgent()
result = agent.classify_ticket(ticket)
```

### Custom Template
```python
# Use a different template
agent = SmartTechTicketAgent(
    prompt_template_path="prompts/intent_detection_urgent.j2"
)
```

### Preview Template
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("prompts"))
template = env.get_template("intent_detection.j2")

prompt = template.render(
    company_name="SmartTech",
    ticket=my_ticket,
    intent_categories=categories
)
print(prompt)  # See what will be sent to LLM
```

## Template Features

### 1. Variables
Access ticket data dynamically:
```jinja2
{{ company_name }}
{{ ticket.subject }}
{{ ticket.description }}
```

### 2. Loops
Generate intent list automatically:
```jinja2
{% for category, description in intent_categories.items() %}
- {{ category }}: {{ description }}
{% endfor %}
```

### 3. Conditionals
Add logic to templates:
```jinja2
{% if ticket.priority == "High" %}
⚠️ HIGH PRIORITY - Expedite classification
{% endif %}
```

### 4. Template Inheritance
Reuse common structures:
```jinja2
{% extends "base_intent_detection.j2" %}

{% block instructions %}
{{ super() }}
Additional instructions here...
{% endblock %}
```

## Benefits

### For Developers
- **Version Control**: Templates in separate files, easy to track changes
- **Testing**: Quick A/B tests with different prompt variations
- **Maintenance**: Update prompts without touching Python code
- **Reusability**: Template inheritance reduces duplication

### For Business Users
- **No Coding Required**: Edit `.j2` files like text documents
- **Instant Updates**: Change prompts without redeploying
- **Transparency**: Clear view of what's sent to the LLM
- **Experimentation**: Try different wordings easily

## Configuration File

`prompts/prompt_config.json` stores settings:

```json
{
  "company_name": "SmartTech",
  "intent_categories": {
    "password_reset": "Password-related issues",
    "vpn_issues": "VPN connection problems",
    ...
  },
  "llm_settings": {
    "temperature": 0.3,
    "model_instructions": "Respond with ONLY JSON..."
  }
}
```

## Testing

### Run Tests
```bash
# Test template loading and rendering
python test_template_prompt.py

# See all template examples
python examples_prompt_templates.py
```

### Expected Output
```
✓ Jinja2 template engine initialized
✓ Azure OpenAI client initialized
✓ LangGraph workflow compiled

Intent: email_setup, Confidence: 95%
```

## Creating Custom Templates

### Step 1: Create Template File
Create `prompts/my_custom_template.j2`:
```jinja2
You are a {{ role }} at {{ company_name }}.

Analyze this ticket:
{{ ticket.description }}

Categories: {% for cat in intent_categories.keys() %}{{ cat }}{% if not loop.last %}, {% endif %}{% endfor %}

Return JSON: {"intent": "...", "confidence": 0.0}
```

### Step 2: Use Custom Template
```python
agent = SmartTechTicketAgent(
    prompt_template_path="prompts/my_custom_template.j2"
)
```

### Step 3: Add New Variables
Modify `_analyze_intent()` in `smarttech_ticket_agent.py`:
```python
prompt = template.render(
    company_name="SmartTech",
    role="Senior IT Analyst",  # New variable
    ticket=ticket,
    intent_categories=intent_categories
)
```

## Advanced: Template Variants

### For Different Ticket Types

**Email Tickets**: `prompts/intent_email.j2`
```jinja2
Focus on email-related issues: mobile setup, Outlook problems, authentication.
```

**Hardware Tickets**: `prompts/intent_hardware.j2`
```jinja2
Identify specific hardware: printers, monitors, peripherals, devices.
```

**Use Conditionally**:
```python
if ticket['category'] == 'Email':
    template_path = "prompts/intent_email.j2"
elif ticket['category'] == 'Hardware':
    template_path = "prompts/intent_hardware.j2"
else:
    template_path = "prompts/intent_detection.j2"

agent = SmartTechTicketAgent(prompt_template_path=template_path)
```

## Troubleshooting

### Template Not Found
**Error**: `jinja2.exceptions.TemplateNotFound: intent_detection.j2`

**Solution**:
- Verify file exists in `prompts/` directory
- Check file extension is `.j2`
- Ensure filename matches exactly (case-sensitive)

### Variable Not Rendering
**Issue**: Template shows `{{ ticket.subject }}` literally

**Solution**:
- Check variable name matches in `template.render()`
- Use correct dictionary key: `ticket.subject` not `ticket['subject']`
- Verify data structure matches template expectations

### Fallback Behavior
If template loading fails, the agent uses a hardcoded fallback prompt automatically.

## Migration Guide

### Existing Prompts → Templates

**Old code**:
```python
prompt = f"""Classify this ticket: {ticket['subject']}
Categories: password_reset, vpn_issues
"""
```

**New template** (`my_prompt.j2`):
```jinja2
Classify this ticket: {{ ticket.subject }}
Categories: {% for cat in categories %}{{ cat }}{% if not loop.last %}, {% endif %}{% endfor %}
```

**New code**:
```python
template = env.get_template("my_prompt.j2")
prompt = template.render(ticket=ticket, categories=['password_reset', 'vpn_issues'])
```

## Next Steps

1. ✅ **Test current implementation**
   ```bash
   python test_template_prompt.py
   ```

2. 📝 **Customize your template**
   - Edit `prompts/intent_detection.j2`
   - Add company-specific instructions
   - Adjust response format

3. 🧪 **Create prompt variations**
   - Copy template to `intent_detection_v2.j2`
   - Modify wording/structure
   - A/B test with different tickets

4. 📊 **Measure improvements**
   - Track confidence scores
   - Compare classification accuracy
   - Analyze self-service rates

## API Impact

No changes to the FastAPI endpoints. Templates work transparently:

```python
# API still works the same
response = requests.post(
    "http://localhost:8000/api/v1/tickets/classify",
    json={"ticket_id": "TSD-001", "subject": "Help!", ...}
)
```

The agent now uses templates internally, but the API interface remains unchanged.

## Resources

- **Jinja2 Documentation**: https://jinja.palletsprojects.com/
- **Template Syntax**: `prompts/README.md`
- **Examples**: `examples_prompt_templates.py`
- **Tests**: `test_template_prompt.py`

---

**Questions?** Check `prompts/README.md` for detailed template documentation.
