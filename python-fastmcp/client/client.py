#!/usr/bin/env python3
"""
Real Models FastMCP Client - Python Implementation

Interactive client for the FastMCP Real Models Server with support for:
- Automatic model selection based on task type
- Manual provider selection (/ollama, /claude, /openai)
- Model listing and configuration
- Real-time chat interface with FastMCP integration
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from pydantic import BaseModel

# Import shared types for better integration
from shared.types import ModelProvider, TaskType

# Load environment variables
load_dotenv()

class FastMCPClient:
    """FastMCP Client for real model interactions."""
    
    def __init__(self):
        self.server_process = None
        self.request_id = 1
        self.is_connected = False
    
    async def connect(self):
        """Connect to the FastMCP server."""
        server_path = os.path.join(os.path.dirname(__file__), '..', 'server', 'server.py')
        
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait a moment for server to start
        await asyncio.sleep(1)
        
        # Initialize the MCP connection
        init_request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "fastmcp-client", "version": "1.0.0"}
            }
        }
        self.request_id += 1
        
        # Send initialize request
        request_json = json.dumps(init_request) + '\n'
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        # Read initialize response
        response_line = await self.server_process.stdout.readline()
        if not response_line:
            raise RuntimeError("Server closed connection during initialization")
        
        response = json.loads(response_line.decode().strip())
        if "error" in response:
            raise RuntimeError(f"Initialization failed: {response['error']['message']}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        request_json = json.dumps(initialized_notification) + '\n'
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        self.is_connected = True
    
    async def send_request(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Send a request to the FastMCP server."""
        if not self.is_connected:
            raise RuntimeError("Client not connected to server")
        
        if params is None:
            params = {}
        
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        self.request_id += 1
        
        # Send request
        request_json = json.dumps(request) + '\n'
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        # Read response
        response_line = await self.server_process.stdout.readline()
        if not response_line:
            raise RuntimeError("Server closed connection")
        
        response = json.loads(response_line.decode().strip())
        
        if "error" in response:
            raise RuntimeError(response["error"]["message"])
        
        return response["result"]
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return await self.send_request("tools/list")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool."""
        return await self.send_request("tools/call", {"name": name, "arguments": arguments})
    
    async def disconnect(self):
        """Disconnect from the server."""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
            self.is_connected = False

class CliColors:
    """Terminal colors for better UI."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

async def run_interactive_demo():
    """Run the interactive demo."""
    print(f"{CliColors.HEADER}🤖 Real Models FastMCP Client Demo{CliColors.ENDC}")
    print("========================================\n")
    
    client = FastMCPClient()
    
    try:
        print("Connecting to FastMCP server...")
        await client.connect()
        print(f"{CliColors.GREEN}✅ Connected!{CliColors.ENDC}\n")
        
        # List available tools
        print(f"{CliColors.BLUE}📋 Available tools:{CliColors.ENDC}")
        tools = await client.list_tools()
        for tool in tools["tools"]:
            print(f"  • {CliColors.BOLD}{tool['name']}{CliColors.ENDC}: {tool['description']}")
        print()
        
        # Interactive chat loop
        print(f"{CliColors.BLUE}💬 Interactive Chat{CliColors.ENDC} (type 'quit' to exit, 'help' for commands)")
        print("You can specify provider with: /ollama, /claude, /openai")
        print("Example: /claude Tell me a creative story about AI\n")
        
        while True:
            try:
                user_input = input(f"{CliColors.BOLD}You:{CliColors.ENDC} ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    break
                
                if user_input.lower() == 'help':
                    print("\nAvailable commands:")
                    print(f"  {CliColors.YELLOW}/ollama <prompt>{CliColors.ENDC}  - Use Ollama (local)")
                    print(f"  {CliColors.YELLOW}/claude <prompt>{CliColors.ENDC}  - Use Claude")
                    print(f"  {CliColors.YELLOW}/openai <prompt>{CliColors.ENDC}  - Use OpenAI GPT-4")
                    print(f"  {CliColors.YELLOW}/models <provider>{CliColors.ENDC} - List models for provider")
                    print(f"  {CliColors.YELLOW}help{CliColors.ENDC}             - Show this help")
                    print(f"  {CliColors.YELLOW}quit/exit{CliColors.ENDC}        - Exit the demo\n")
                    continue
                
                if user_input.startswith('/models '):
                    provider = user_input[8:].strip()
                    try:
                        print(f"\n🔍 Getting models for {provider}...")
                        result = await client.call_tool('list_models', {'request': {'provider': provider}})
                        data = json.loads(result['content'][0]['text'])
                        print(f"\n📋 Available {CliColors.BOLD}{data['provider']}{CliColors.ENDC} models:")
                        for model in data['models']:
                            print(f"  • {model}")
                        print()
                    except Exception as e:
                        print(f"{CliColors.RED}❌ Error: {e}{CliColors.ENDC}\n")
                    continue
                
                provider = None
                prompt = user_input
                
                # Check for provider prefix
                if user_input.startswith('/'):
                    parts = user_input.split(' ', 1)
                    provider_cmd = parts[0][1:]
                    if provider_cmd in ['ollama', 'claude', 'openai']:
                        provider = provider_cmd
                        prompt = parts[1] if len(parts) > 1 else ""
                
                if not prompt.strip():
                    print("Please enter a prompt.\n")
                    continue
                
                try:
                    print(f"\n{CliColors.YELLOW}🤔 Thinking...{CliColors.ENDC}")
                    start_time = datetime.now()
                    
                    request_args = {"prompt": prompt}
                    if provider:
                        request_args["provider"] = provider
                    
                    result = await client.call_tool('chat', {'request': request_args})
                    
                    duration = (datetime.now() - start_time).total_seconds() * 1000
                    
                    # Check if the result is an error
                    if result.get('isError', False):
                        error_text = result['content'][0]['text']
                        print(f"{CliColors.RED}❌ Error: {error_text}{CliColors.ENDC}\n")
                    else:
                        # Try to parse the JSON response
                        try:
                            data = json.loads(result['content'][0]['text'])
                            provider_name = data['model_info']['provider'].upper()
                            model_name = data['model_info']['model']
                            print(f"\n{CliColors.GREEN}🤖 {provider_name} ({model_name}):{CliColors.ENDC}")
                            print(data['response'])
                            print(f"\n{CliColors.BLUE}📊 Usage: {data['usage']['total_tokens']} tokens | {duration:.0f}ms{CliColors.ENDC}")
                            if data['model_info']['auto_selected']:
                                task_type = data['model_info']['task_type']
                                print(f"{CliColors.BLUE}🎯 Auto-selected for task: {task_type}{CliColors.ENDC}")
                            print()
                        except json.JSONDecodeError:
                            # If JSON parsing fails, show the raw response
                            print(f"{CliColors.RED}❌ Invalid response format: {result['content'][0]['text']}{CliColors.ENDC}\n")
                
                except Exception as e:
                    print(f"{CliColors.RED}❌ Error: {e}{CliColors.ENDC}\n")
            
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except EOFError:
                break
    
    except Exception as e:
        print(f"{CliColors.RED}Demo error: {e}{CliColors.ENDC}")
    finally:
        await client.disconnect()
        print(f"\n{CliColors.GREEN}👋 Goodbye!{CliColors.ENDC}")

async def run_examples():
    """Run example API calls."""
    print(f"{CliColors.HEADER}🧪 Real Models FastMCP Examples{CliColors.ENDC}")
    print("=====================================\n")
    
    client = FastMCPClient()
    
    try:
        await client.connect()
        
        # Example 1: Auto-selected model for creative task
        print(f"{CliColors.BLUE}1. Creative task (auto-selected model):{CliColors.ENDC}")
        result = await client.call_tool('chat', {
            'prompt': 'Write a short creative story about a robot learning to paint'
        })
        data = json.loads(result['content'][0]['text'])
        if "error" in data:
            print(f"   {CliColors.YELLOW}⚠️ API error: {data['error'][:50]}...{CliColors.ENDC}")
        else:
            print(f"   Model: {data['model_info']['provider']} ({data['model_info']['model']})")
            print(f"   Response: {data['response'][:100]}...\n")
        
        # Example 2: Specific provider - Ollama
        print(f"{CliColors.BLUE}2. Coding task with Ollama:{CliColors.ENDC}")
        try:
            result = await client.call_tool('chat', {
                'prompt': 'Write a Python function to calculate fibonacci numbers',
                'provider': 'ollama'
            })
            data = json.loads(result['content'][0]['text'])
            if "error" in data:
                print(f"   {CliColors.YELLOW}⚠️ Ollama error: {data['error'][:50]}...{CliColors.ENDC}")
            else:
                print(f"   Model: {data['model_info']['provider']} ({data['model_info']['model']})")
                print(f"   Response: {data['response'][:100]}...")
        except Exception as e:
            print(f"   {CliColors.YELLOW}⚠️ Ollama not available: {e}{CliColors.ENDC}")
        print()
        
        # Example 3: List models
        print(f"{CliColors.BLUE}3. Available OpenAI models:{CliColors.ENDC}")
        result = await client.call_tool('list_models', {'provider': 'openai'})
        data = json.loads(result['content'][0]['text'])
        print(f"   Models: {', '.join(data['models'])}\n")
        
        # Example 4: FastMCP-specific features
        print(f"{CliColors.BLUE}4. FastMCP implementation details:{CliColors.ENDC}")
        result = await client.call_tool('chat', {
            'prompt': 'Hello FastMCP!',
            'temperature': 0.3,
            'max_tokens': 50
        })
        data = json.loads(result['content'][0]['text'])
        if "error" in data:
            print(f"   {CliColors.YELLOW}⚠️ API error: {data['error'][:50]}...{CliColors.ENDC}")
        else:
            print(f"   Implementation: {data.get('implementation', 'unknown')}")
            print(f"   Response: {data['response'][:50]}...")
            print(f"   Temperature: 0.3 (custom parameter)")
            print(f"   Max tokens: 50 (custom parameter)")
    
    except Exception as e:
        print(f"{CliColors.RED}Examples error: {e}{CliColors.ENDC}")
    finally:
        await client.disconnect()

async def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--examples':
        await run_examples()
    else:
        await run_interactive_demo()

if __name__ == "__main__":
    asyncio.run(main())