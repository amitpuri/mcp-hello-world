#!/usr/bin/env python3
"""
Real Models FastMCP Server - Python Implementation

A modern MCP server using FastMCP framework with real AI model integrations:
- Ollama (local models)
- Claude (Anthropic)
- OpenAI GPT-4

Built with FastMCP decorators for cleaner, more maintainable code.
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Optional

# Add the parent directory to the path so we can import shared modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, will use system environment variables only
    pass

try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    # Fallback to standard MCP with FastMCP-like interface
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    import json
    FASTMCP_AVAILABLE = False

from shared.types import (
    ChatRequest,
    ListModelsRequest,
    ChatResponse,
    ListModelsResponse,
    ModelInfo,
    determine_task_type,
    select_model_for_task,
    validate_model_request,
    get_env_config
)
from shared.models import get_model_clients

# Initialize FastMCP app
app = FastMCP("Real Models FastMCP Server")

# Global instances
config = get_env_config()
model_clients = get_model_clients()

@app.tool()
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat with AI models (Ollama, Claude, or GPT-4) with automatic or manual model selection.
    
    Automatically selects the best model based on task type, or uses specified provider.
    Supports temperature and max_tokens parameters for fine-tuning responses.
    """
    # Determine task type and select appropriate provider
    task_type = determine_task_type(request.prompt)
    selected_provider = select_model_for_task(task_type, request.provider)
    
    # Validate the request
    is_valid, error_msg = validate_model_request(selected_provider.value, request.model)
    if not is_valid:
        raise ValueError(error_msg)
    
    # Prepare options
    options = {
        "temperature": request.temperature,
        "max_tokens": request.max_tokens
    }
    
    # Call the model
    result = await model_clients.call_model(
        selected_provider.value, 
        request.prompt, 
        request.model, 
        options
    )
    
    if not result["success"]:
        raise ValueError(f"{result.get('provider', 'Unknown')} API error: {result['error']}")
    
    return ChatResponse(
        response=result["content"],
        model_info=ModelInfo(
            provider=result["provider"],
            model=result["model"],
            task_type=task_type.value,
            auto_selected=request.provider is None
        ),
        usage=result["usage"],
        timestamp=datetime.now().isoformat()
    )

@app.tool()
async def list_models(request: ListModelsRequest) -> ListModelsResponse:
    """
    List available models for a specific provider.
    
    Returns the list of models available for the specified provider (ollama, claude, or openai).
    For Ollama, queries the local server for installed models.
    """
    result = await model_clients.get_available_models(request.provider.value)
    
    if not result["success"]:
        raise ValueError(f"Failed to get models for {request.provider}: {result['error']}")
    
    return ListModelsResponse(
        provider=result["provider"],
        models=result["models"],
        timestamp=datetime.now().isoformat()
    )

if __name__ == "__main__":
    # Print startup information
    print(f"🚀 Real Models FastMCP Server started - {datetime.now().isoformat()}", file=sys.stderr)
    print(f"📋 Server: {config.server_name} v{config.server_version}", file=sys.stderr)
    print(f"🔧 Configured providers: ollama, claude, openai", file=sys.stderr)
    print(f"🎯 Model routing enabled: {config.enable_model_routing}", file=sys.stderr)
    
    # Run the FastMCP server
    app.run()