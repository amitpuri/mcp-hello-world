#!/usr/bin/env python3
"""
Real Models MCP Server - Python Implementation

A production-ready MCP server with real AI model integrations:
- Ollama (local models)
- Claude (Anthropic)
- OpenAI GPT-4

Supports automatic model selection based on task type and manual provider selection.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Add the parent directory to the path so we can import shared modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from shared.types import (
    ModelProvider,
    TaskType,
    determine_task_type,
    select_model_for_task,
    validate_model_request,
    get_env_config
)
from shared.models import get_model_clients

# Load environment variables
load_dotenv()

class MCPServer:
    """MCP Server with real model integrations."""
    
    def __init__(self):
        self.config = get_env_config()
        self.model_clients = get_model_clients()
        self.request_id = 0
    
    def log(self, message: str, level: str = "INFO"):
        """Log message to stderr (won't interfere with MCP communication)."""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] {level}: {message}", file=sys.stderr)
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "tools/list":
                result = await self.list_tools()
            elif method == "tools/call":
                result = await self.call_tool(params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        except Exception as e:
            self.log(f"Error handling request {method}: {str(e)}", "ERROR")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available MCP tools."""
        return {
            "tools": [
                {
                    "name": "chat",
                    "description": "Chat with AI models (Ollama, Claude, or GPT-4) with automatic or manual model selection",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The message/prompt to send to the AI model"
                            },
                            "provider": {
                                "type": "string",
                                "description": "Model provider: ollama, claude, or openai (optional - will auto-select based on task)",
                                "enum": ["ollama", "claude", "openai"]
                            },
                            "model": {
                                "type": "string",
                                "description": "Specific model name (optional - will use provider default)"
                            },
                            "temperature": {
                                "type": "number",
                                "description": "Temperature for response generation (0.0-1.0, default: 0.7)",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "max_tokens": {
                                "type": "number",
                                "description": "Maximum tokens in response (default: 1000)",
                                "minimum": 1,
                                "maximum": 4000
                            }
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "list_models",
                    "description": "List available models for a specific provider",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "description": "Model provider: ollama, claude, or openai",
                                "enum": ["ollama", "claude", "openai"]
                            }
                        },
                        "required": ["provider"]
                    }
                }
            ]
        }
    
    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "chat":
            return await self.handle_chat(arguments)
        elif tool_name == "list_models":
            return await self.handle_list_models(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def handle_chat(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat requests."""
        prompt = args.get("prompt")
        if not prompt:
            raise ValueError("Prompt is required")
        
        provider = args.get("provider")
        model = args.get("model")
        temperature = args.get("temperature")
        max_tokens = args.get("max_tokens")
        
        # Determine task type and select appropriate provider
        task_type = determine_task_type(prompt)
        selected_provider = select_model_for_task(task_type, provider)
        
        # Validate the request
        is_valid, error_msg = validate_model_request(selected_provider.value, model)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Prepare options
        options = {}
        if temperature is not None:
            options["temperature"] = temperature
        if max_tokens is not None:
            options["max_tokens"] = max_tokens
        
        # Call the model
        result = await self.model_clients.call_model(selected_provider.value, prompt, model, options)
        
        if not result["success"]:
            raise ValueError(f"{result.get('provider', 'Unknown')} API error: {result['error']}")
        
        response_data = {
            "response": result["content"],
            "model_info": {
                "provider": result["provider"],
                "model": result["model"],
                "task_type": task_type.value,
                "auto_selected": provider is None
            },
            "usage": result["usage"],
            "timestamp": datetime.now().isoformat(),
            "implementation": "python"
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(response_data, indent=2)
                }
            ]
        }
    
    async def handle_list_models(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list models requests."""
        provider = args.get("provider")
        if not provider:
            raise ValueError("Provider is required")
        
        result = await self.model_clients.get_available_models(provider)
        
        if not result["success"]:
            raise ValueError(f"Failed to get models for {provider}: {result['error']}")
        
        response_data = {
            "provider": result["provider"],
            "models": result["models"],
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(response_data, indent=2)
                }
            ]
        }
    
    async def run(self):
        """Run the MCP server."""
        self.log(f"Real Models MCP Server (Python) started - {datetime.now().isoformat()}")
        self.log(f"Configured providers: {', '.join([p.value for p in ModelProvider])}")
        
        try:
            while True:
                # Read request from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    
                    # Send response to stdout
                    print(json.dumps(response), flush=True)
                
                except json.JSONDecodeError as e:
                    self.log(f"Invalid JSON received: {e}", "ERROR")
                except Exception as e:
                    self.log(f"Error processing request: {e}", "ERROR")
        
        except KeyboardInterrupt:
            self.log("Server interrupted by user")
        except Exception as e:
            self.log(f"Server error: {e}", "ERROR")
        finally:
            await self.model_clients.close()
            self.log("Server shutdown complete")

async def main():
    """Main entry point."""
    server = MCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())