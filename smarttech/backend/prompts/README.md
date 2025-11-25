# Prompt Templates

This directory contains Jinja2 templates for LLM prompts used in the SmartTech TSD Agent.

## Files

- **intent_detection.j2**: Main prompt template for intent detection
- **prompt_config.json**: Configuration file with intent categories and settings

## Using Templates

### Basic Usage

The agent automatically loads templates from this directory:

```python
agent = SmartTechTicketAgent()
```

### Custom Template Path

You can specify a custom template:

```python
agent = SmartTechTicketAgent(prompt_template_path="prompts/custom_intent_detection.j2")
```

### Template Variables

Available variables in `intent_detection.j2`:

- `company_name`: Name of the company (e.g., "SmartTech")
- `ticket`: Dictionary containing ticket details
  - `ticket.ticket_id`
  - `ticket.subject`
  - `ticket.description`
  - `ticket.category`
- `intent_categories`: Dictionary of intent categories and descriptions

### Customizing Prompts

1. **Edit the template** (`intent_detection.j2`):
   - Modify the prompt structure
   - Add new instructions
   - Change the response format

2. **Update configuration** (`prompt_config.json`):
   - Add/remove intent categories
   - Change company name
   - Adjust LLM settings

3. **Create variant templates**:
   ```bash
   # Copy existing template
   cp intent_detection.j2 intent_detection_v2.j2
   
   # Modify as needed
   # Use with: SmartTechTicketAgent(prompt_template_path="prompts/intent_detection_v2.j2")
   ```

## Template Syntax

Jinja2 template features used:

### Variables
```jinja2
{{ company_name }}
{{ ticket.subject }}
```

### Loops
```jinja2
{% for category, description in intent_categories.items() %}
- {{ category }}: {{ description }}
{% endfor %}
```

### Conditionals
```jinja2
{% if ticket.priority == "High" %}
URGENT: 
{% endif %}
```

## Example: Creating a Custom Template

**File: `prompts/intent_detection_detailed.j2`**

```jinja2
You are a senior IT support analyst at {{ company_name }} with 10+ years of experience.

Your task: Analyze the support ticket below and classify the user's primary intent with high precision.

TICKET INFORMATION
==================
ID:          {{ ticket.ticket_id }}
Subject:     {{ ticket.subject }}
Description: {{ ticket.description }}
Category:    {{ ticket.category }}
Priority:    {{ ticket.priority }}
User:        {{ ticket.user }}

INTENT CATEGORIES
=================
{% for category, description in intent_categories.items() %}
{{ loop.index }}. {{ category | upper }}
   Description: {{ description }}
{% endfor %}

INSTRUCTIONS
============
1. Read the ticket carefully
2. Identify keywords and context clues
3. Select the MOST SPECIFIC category that matches
4. Provide confidence score (0.0 to 1.0)
5. Explain your reasoning in 1-2 sentences

OUTPUT FORMAT (JSON only, no markdown):
{
    "intent": "category_name",
    "confidence": 0.95,
    "reasoning": "Your explanation here"
}
```

## Best Practices

1. **Keep templates focused**: One template per task
2. **Use clear variable names**: `ticket.subject` not `t.s`
3. **Document template changes**: Add comments in Jinja2
4. **Version your templates**: Use v1, v2 suffixes for iterations
5. **Test thoroughly**: Verify template rendering before deployment

## Troubleshooting

### Template not found
- Check file name matches exactly (case-sensitive)
- Ensure file is in `prompts/` directory
- Verify file extension is `.j2`

### Variables not rendering
- Check variable names in template match those passed
- Use `{{ ticket.subject }}` not `{{ subject }}`
- Verify dictionary keys are correct

### Fallback behavior
If template fails to load, the agent uses a hardcoded fallback prompt.
