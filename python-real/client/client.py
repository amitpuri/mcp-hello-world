#!/usr/bin/env python3
"""
Real Models MCP Client - Python Implementation

Interactive client for the Real Models MCP Server with support for:
- Automatic model selection based on task type
- Manual provider selection (/ollama, /claude, /openai)
- Model listing and configuration
- Real-time chat interface
"""

import asyncio
import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MCPClient:
    """MCP Client for real model interactions."""
    
    def __init__(self):
        self.server_process = None
        self.request_id = 1
        self.is_connected = False
    
    async def connect(self):
        """Connect to the MCP server."""
        server_path = os.path.join(os.path.dirname(__file__), '..', 'server', 'server.py')
        
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait a moment for server to start
        await asyncio.sleep(1)
        self.is_connected = True
    
    async def send_request(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Send a request to the MCP server."""
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

async def run_interactive_demo():
    """Run the interactive demo."""
    print("🤖 Real Models MCP Client Demo (Python)")
    print("========================================\n")
    
    client = MCPClient()
    
    try:
        print("Connecting to MCP server...")
        await client.connect()
        print("✅ Connected!\n")
        
        # List available tools
        print("📋 Available tools:")
        tools = await client.list_tools()
        for tool in tools["tools"]:
            print(f"  • {tool['name']}: {tool['description']}")
        print()
        
        # Interactive chat loop
        print("💬 Interactive Chat (type 'quit' to exit, 'help' for commands)")
        print("You can specify provider with: /ollama, /claude, /openai")
        print("Example: /claude Tell me a creative story about AI\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    break
                
                if user_input.lower() == 'help':
                    print("\nAvailable commands:")
                    print("  /ollama <prompt>  - Use Ollama (local)")
                    print("  /claude <prompt>  - Use Claude")
                    print("  /openai <prompt>  - Use OpenAI GPT-4")
                    print("  /models <provider> - List models for provider")
                    print("  help             - Show this help")
                    print("  quit/exit        - Exit the demo\n")
                    continue
                
                if user_input.startswith('/models '):
                    provider = user_input[8:].strip()
                    try:
                        print(f"\n🔍 Getting models for {provider}...")
                        result = await client.call_tool('list_models', {'provider': provider})
                        data = json.loads(result['content'][0]['text'])
                        print(f"\n📋 Available {data['provider']} models:")
                        for model in data['models']:
                            print(f"  • {model}")
                        print()
                    except Exception as e:
                        print(f"❌ Error: {e}\n")
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
                    print("\n🤔 Thinking...")
                    start_time = datetime.now()
                    
                    args = {"prompt": prompt}
                    if provider:
                        args["provider"] = provider
                    
                    result = await client.call_tool('chat', args)
                    data = json.loads(result['content'][0]['text'])
                    
                    duration = (datetime.now() - start_time).total_seconds() * 1000
                    
                    if "error" in data:
                        print(f"❌ Error: {data['error']}\n")
                    else:
                        print(f"\n🤖 {data['model_info']['provider'].upper()} ({data['model_info']['model']}):")
                        print(data['response'])
                        print(f"\n📊 Usage: {data['usage']['total_tokens']} tokens | {duration:.0f}ms")
                        if data['model_info']['auto_selected']:
                            print(f"🎯 Auto-selected for task: {data['model_info']['task_type']}")
                        print()
                
                except Exception as e:
                    print(f"❌ Error: {e}\n")
            
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except EOFError:
                break
    
    except Exception as e:
        print(f"Demo error: {e}")
    finally:
        await client.disconnect()
        print("\n👋 Goodbye!")

async def run_examples():
    """Run example API calls."""
    print("🧪 Real Models MCP Examples (Python)")
    print("=====================================\n")
    
    client = MCPClient()
    
    try:
        await client.connect()
        
        # Example 1: Auto-selected model for creative task
        print("1. Creative task (auto-selected model):")
        result = await client.call_tool('chat', {
            'prompt': 'Write a short creative story about a robot learning to paint'
        })
        data = json.loads(result['content'][0]['text'])
        print(f"   Model: {data['model_info']['provider']} ({data['model_info']['model']})")
        print(f"   Response: {data['response'][:100]}...\n")
        
        # Example 2: Specific provider - Ollama
        print("2. Coding task with Ollama:")
        try:
            result = await client.call_tool('chat', {
                'prompt': 'Write a Python function to calculate fibonacci numbers',
                'provider': 'ollama'
            })
            data = json.loads(result['content'][0]['text'])
            if "error" in data:
                print(f"   ⚠️ Ollama error: {data['error'][:50]}...")
            else:
                print(f"   Model: {data['model_info']['provider']} ({data['model_info']['model']})")
                print(f"   Response: {data['response'][:100]}...")
        except Exception as e:
            print(f"   ⚠️ Ollama not available: {e}")
        print()
        
        # Example 3: List models
        print("3. Available OpenAI models:")
        result = await client.call_tool('list_models', {'provider': 'openai'})
        data = json.loads(result['content'][0]['text'])
        print(f"   Models: {', '.join(data['models'])}\n")
    
    except Exception as e:
        print(f"Examples error: {e}")
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