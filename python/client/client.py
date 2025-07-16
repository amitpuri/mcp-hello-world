#!/usr/bin/env python3
"""
Hello World MCP Client (Python Implementation)

A complete MCP client implementation demonstrating:
- JSON-RPC communication with MCP server
- Multiple greeting styles testing
- Model routing validation
- Proper error handling and cleanup
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.types import HelloWorldScenario, ModelProvider

class HelloWorldClient:
    """MCP Hello World Client with comprehensive testing capabilities."""
    
    def __init__(self):
        """Initialize the client."""
        self.request_id = 1
        self.server_process: Optional[asyncio.subprocess.Process] = None

    async def connect(self) -> asyncio.subprocess.Process:
        """Connect to the MCP server by spawning the server process."""
        server_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "server", 
            "server.py"
        )
        
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("✅ Connected to Hello World MCP Server")
        return self.server_process

    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server."""
        if not self.server_process:
            raise RuntimeError("Not connected to server")
        
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        
        if params:
            request["params"] = params
        
        self.request_id += 1
        
        # Send request
        request_json = json.dumps(request) + '\n'
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        # Read response
        response_line = await self.server_process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")
        
        response = json.loads(response_line.decode().strip())
        
        # Check for errors
        if "error" in response:
            error = response["error"]
            raise RuntimeError(f"Server error {error['code']}: {error['message']}")
        
        return response

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the server."""
        response = await self.send_request("tools/list")
        return response["result"]["tools"]

    async def call_hello_tool(
        self, 
        name: str, 
        style: Optional[str] = None, 
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call the hello tool with specified parameters."""
        args = {"name": name}
        if style:
            args["style"] = style
        if model:
            args["model"] = model
        
        response = await self.send_request("tools/call", {
            "name": "hello",
            "arguments": args
        })
        
        # Parse the result from the response
        result_text = response["result"]["content"][0]["text"]
        return json.loads(result_text)

    async def run_demo(self):
        """Run a comprehensive demo of the MCP server functionality."""
        print("🐍 Hello World MCP Client Demo\n")
        
        try:
            # Connect to server
            await self.connect()
            
            # List available tools
            print("📋 Available Tools:")
            tools = await self.list_tools()
            for tool in tools:
                print(f"  • {tool['name']}: {tool['description']}")
            print()
            
            # Test different scenarios
            test_cases = [
                {"name": "Alice", "style": HelloWorldScenario.SIMPLE.value},
                {"name": "Bob", "style": HelloWorldScenario.FORMAL.value},
                {"name": "Charlie", "style": HelloWorldScenario.CREATIVE.value},
                {"name": "Dave", "style": HelloWorldScenario.TECHNICAL.value},
                {"name": "Eve", "style": HelloWorldScenario.SIMPLE.value, "model": ModelProvider.LLAMA.value}
            ]
            
            print("🎭 Testing Different Greeting Styles:")
            for test_case in test_cases:
                result = await self.call_hello_tool(
                    test_case["name"],
                    test_case.get("style"),
                    test_case.get("model")
                )
                
                print(f"\n  👤 Name: {test_case['name']}")
                print(f"  🎨 Style: {test_case.get('style', 'default')}")
                if test_case.get("model"):
                    print(f"  🤖 Requested Model: {test_case['model']}")
                print(f"  🔀 Model Used: {result['model_used']}")
                print(f"  💬 Message: {result['message']}")
                print(f"  ⏰ Time: {result['timestamp']}")
                print(f"  🎯 Routing Applied: {'Yes' if result['routing_applied'] else 'No'}")
                print(f"  🐍 Implementation: {result['implementation']}")
            
            print("\n✅ Demo completed successfully!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            raise
        finally:
            # Clean up
            if self.server_process:
                self.server_process.terminate()
                await self.server_process.wait()

async def main():
    """Main entry point for the client demo."""
    client = HelloWorldClient()
    await client.run_demo()

if __name__ == "__main__":
    asyncio.run(main())