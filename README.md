# Simple LangGraph Agent with Azure OpenAI

A simple implementation of a LangGraph agent using Azure OpenAI, based on the [Azure Samples reference](https://github.com/Azure-Samples/app-service-agentic-langgraph-foundry-python).

## Features

- **Azure OpenAI Integration**: Uses Azure OpenAI with API key authentication
- **ReAct Agent**: Implements a ReAct (Reasoning and Acting) agent pattern
- **Custom Tools**: Includes example tools for weather queries and calculations
- **Memory Management**: Maintains conversation context using thread IDs
- **Async Support**: Full async/await support with sync wrapper

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Then edit `.env` with your Azure OpenAI details:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### 3. Get Your Azure OpenAI API Key

You can find your API key in the Azure Portal:
1. Go to your Azure OpenAI resource
2. Click on "Keys and Endpoint" in the left menu
3. Copy one of the keys and add it to your `.env` file

## Usage

### Basic Example

```python
import asyncio
from simple_langgraph_agent import SimpleLangGraphAgent

async def main():
    # Initialize the agent
    agent = SimpleLangGraphAgent()
    
    # Send a message
    response = await agent.chat("What's the weather like in San Francisco?")
    print(response)

asyncio.run(main())
```

### Synchronous Usage

```python
from simple_langgraph_agent import SimpleLangGraphAgent

# Initialize the agent
agent = SimpleLangGraphAgent()

# Use sync wrapper
response = agent.chat_sync("Calculate 15 * 23")
print(response)
```

### Conversation with Context

```python
import asyncio
from simple_langgraph_agent import SimpleLangGraphAgent

async def main():
    agent = SimpleLangGraphAgent()
    
    # Use thread_id to maintain conversation context
    thread_id = "user-123"
    
    response1 = await agent.chat("Remember this number: 42", thread_id)
    print(response1)
    
    response2 = await agent.chat("What number did I just tell you?", thread_id)
    print(response2)

asyncio.run(main())
```

## Running the Example

```bash
python simple_langgraph_agent.py
```

## Architecture

### Components

1. **SimpleLangGraphAgent**: Main agent class
   - Initializes Azure OpenAI client
   - Creates tools and ReAct agent
   - Manages conversation memory

2. **Tools**:
   - `get_weather`: Mock weather information tool
   - `calculate`: Simple calculator tool

3. **Memory**: Uses `MemorySaver` for in-memory conversation history

### How It Works

1. User sends a message to the agent
2. Agent uses ReAct pattern to:
   - Reason about what to do
   - Decide which tool(s) to use
   - Execute the tools
   - Formulate a response
3. Conversation context is preserved using thread IDs

## Customization

### Adding Custom Tools

Create a new tool method:

```python
def _your_custom_tool(self):
    @tool
    def your_tool(param: str) -> str:
        """Tool description for the LLM"""
        # Your tool logic here
        return f"Result: {param}"
    
    return your_tool
```

Then add it to the tools list in `__init__`:

```python
tools = [
    self._get_weather_tool(),
    self._calculate_tool(),
    self._your_custom_tool()  # Add here
]
```

### Changing LLM Parameters

Modify the `AzureChatOpenAI` initialization:

```python
self.llm = AzureChatOpenAI(
    azure_endpoint=endpoint,
    azure_deployment=deployment_name,
    api_version=api_version,
    azure_ad_token_provider=token_provider,
    temperature=0.7,  # Change this
    max_tokens=1000,  # Add parameters
)
```

## Reference

Based on the Azure Samples LangGraph agent:
- [GitHub Repository](https://github.com/Azure-Samples/app-service-agentic-langgraph-foundry-python)
- [Original File](https://github.com/Azure-Samples/app-service-agentic-langgraph-foundry-python/blob/main/src/agents/langgraph_task_agent.py)

## Key Differences from Reference

This simplified version:
- Uses API key authentication instead of managed identity
- Uses basic tools instead of task management
- Simplified error handling
- Removed service layer dependencies
- Added sync wrapper for easier usage
- Cleaner structure for learning purposes
