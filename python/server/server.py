#!/usr/bin/env python3
"""
Hello World MCP Server (Python Implementation)

A complete MCP server implementation demonstrating:
- Multiple greeting styles with model routing
- JSON-RPC protocol handling
- Proper error handling and logging
- Environment configuration support
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, will use system environment variables only
    pass

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.types import (
    ModelProvider, 
    HelloWorldScenario, 
    DEFAULT_ROUTING_RULES, 
    GREETING_TEMPLATES
)

class HelloWorldServer:
    """MCP Hello World Server with multiple greeting styles and model routing."""
    
    def __init__(self):
        """Initialize the server with configuration."""
        self.config = {
            'name': os.getenv('MCP_SERVER_NAME', 'hello-world-server'),
            'version': os.getenv('MCP_SERVER_VERSION', '1.0.0'),
            'default_model': os.getenv('DEFAULT_MODEL', ModelProvider.CLAUDE.value),
            'enable_model_routing': os.getenv('ENABLE_MODEL_ROUTING', 'true').lower() != 'false',
            'max_name_length': int(os.getenv('MAX_NAME_LENGTH', '50')),
            'enable_emoji': os.getenv('ENABLE_EMOJI', 'true').lower() != 'false',
            'default_style': os.getenv('DEFAULT_GREETING_STYLE', HelloWorldScenario.SIMPLE.value)
        }
        
        self.tools = [
            {
                "name": "hello",
                "description": "Generate a hello world message with different styles and model routing",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name to greet",
                            "default": "World"
                        },
                        "style": {
                            "type": "string",
                            "enum": [style.value for style in HelloWorldScenario],
                            "description": "Style of greeting",
                            "default": "simple"
                        },
                        "model": {
                            "type": "string",
                            "description": "Specific model to use (optional)"
                        }
                    },
                    "required": ["name"]
                }
            }
        ]

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC request."""
        method = request.get("method")
        request_id = request.get("id")
        
        try:
            if method == "tools/list":
                return self._handle_list_tools(request_id)
            elif method == "tools/call":
                return self._handle_call_tool(request, request_id)
            else:
                return self._create_error_response(
                    request_id, -32601, f"Unknown method: {method}"
                )
        except Exception as e:
            return self._create_error_response(
                request_id, -32603, f"Internal error: {str(e)}"
            )

    def _handle_list_tools(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.tools
            }
        }

    def _handle_call_tool(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle tools/call request."""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "hello":
            return self._handle_hello_tool(arguments, request_id)
        else:
            return self._create_error_response(
                request_id, -32601, f"Unknown tool: {tool_name}"
            )

    def _handle_hello_tool(self, args: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Handle the hello tool call."""
        # Extract and validate arguments
        name = args.get("name", "World")
        style = args.get("style", self.config['default_style'])
        model = args.get("model")
        
        # Validate name length
        if len(name) > self.config['max_name_length']:
            return self._create_error_response(
                request_id, -32602, 
                f"Name too long (max {self.config['max_name_length']} characters)"
            )
        
        # Validate style
        try:
            style_enum = HelloWorldScenario(style)
        except ValueError:
            return self._create_error_response(
                request_id, -32602, f"Invalid style: {style}"
            )
        
        # Determine model to use
        if model:
            selected_model = model
            routing_applied = False
        else:
            selected_model = DEFAULT_ROUTING_RULES.get(
                style_enum, self.config['default_model']
            )
            routing_applied = True
        
        # Generate message
        message = self._generate_message(name, style_enum)
        
        # Create result
        result = {
            "message": message,
            "style": style,
            "model_used": selected_model,
            "timestamp": datetime.now().isoformat(),
            "routing_applied": routing_applied,
            "implementation": "python"
        }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        }

    def _generate_message(self, name: str, style: HelloWorldScenario) -> str:
        """Generate greeting message based on style."""
        template = GREETING_TEMPLATES.get(style, GREETING_TEMPLATES[HelloWorldScenario.SIMPLE])
        
        # Handle emoji setting
        if not self.config['enable_emoji'] and style == HelloWorldScenario.CREATIVE:
            template = "Greetings and salutations, magnificent {name}!"
        
        return template.format(name=name)

    def _create_error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create a JSON-RPC error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    def run(self):
        """Run the MCP server, reading from stdin and writing to stdout."""
        print("Hello World MCP server running on stdio", file=sys.stderr)
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = self.handle_request(request)
                    print(json.dumps(response))
                    sys.stdout.flush()
                except json.JSONDecodeError:
                    error_response = self._create_error_response(
                        None, -32700, "Parse error"
                    )
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                except Exception as e:
                    print(f"[MCP Error] {e}", file=sys.stderr)
                    error_response = self._create_error_response(
                        None, -32603, f"Internal error: {str(e)}"
                    )
                    print(json.dumps(error_response))
                    sys.stdout.flush()
        except KeyboardInterrupt:
            print("Server shutting down...", file=sys.stderr)
        except Exception as e:
            print(f"[MCP Error] Server error: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    """Main entry point."""
    server = HelloWorldServer()
    server.run()

if __name__ == "__main__":
    main()