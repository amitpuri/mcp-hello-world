#!/usr/bin/env python3
"""
Real Models MCP Test Suite - Python Implementation

Comprehensive test suite for the Real Models MCP Server that validates:
- MCP protocol compliance
- Real API integrations (with graceful handling of missing keys)
- Model selection logic
- Error handling and recovery
- Parameter validation
- Usage tracking
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MCPTester:
    """Test harness for MCP functionality."""
    
    def __init__(self):
        self.server_process = None
        self.request_id = 1
        self.is_connected = False
        self.test_results = []
    
    async def connect(self):
        """Connect to the MCP server."""
        server_path = os.path.join(os.path.dirname(__file__), '..', 'server', 'server.py')
        
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for server to start
        await asyncio.sleep(1)
        self.is_connected = True
    
    async def send_request(self, method: str, params: Dict = None) -> Dict[str, Any]:
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
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(
                self.server_process.stdout.readline(),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            raise RuntimeError("Request timeout")
        
        if not response_line:
            raise RuntimeError("Server closed connection")
        
        response = json.loads(response_line.decode().strip())
        
        if "error" in response:
            raise RuntimeError(response["error"]["message"])
        
        return response["result"]
    
    async def run_test(self, name: str, test_func):
        """Run a single test."""
        print(f"{len(self.test_results) + 1}. {name}...")
        try:
            start_time = datetime.now()
            await test_func()
            duration = (datetime.now() - start_time).total_seconds() * 1000
            print(f"✅ PASSED ({duration:.0f}ms)")
            self.test_results.append({"name": name, "status": "PASSED", "duration": duration})
        except Exception as e:
            print(f"❌ FAILED: {e}")
            self.test_results.append({"name": name, "status": "FAILED", "error": str(e)})
        print()
    
    async def disconnect(self):
        """Disconnect from the server."""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
            self.is_connected = False
    
    def print_summary(self):
        """Print test summary."""
        print("📊 Test Summary")
        print("================")
        
        passed = len([r for r in self.test_results if r["status"] == "PASSED"])
        failed = len([r for r in self.test_results if r["status"] == "FAILED"])
        
        print(f"Total tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print("\nFailed tests:")
            for result in self.test_results:
                if result["status"] == "FAILED":
                    print(f"  • {result['name']}: {result['error']}")
        
        print(f"\n{'🎉' if failed == 0 else '⚠️'} {'All tests passed!' if failed == 0 else 'Some tests failed'}")

async def run_tests():
    """Run the complete test suite."""
    print("🧪 Real Models MCP Test Suite (Python)")
    print("=======================================\n")
    
    tester = MCPTester()
    
    try:
        print("Connecting to MCP server...")
        await tester.connect()
        print("✅ Connected!\n")
        
        # Test 1: List tools
        async def test_list_tools():
            result = await tester.send_request("tools/list")
            if "tools" not in result or not isinstance(result["tools"], list):
                raise AssertionError("Expected tools array")
            
            tool_names = [t["name"] for t in result["tools"]]
            if "chat" not in tool_names:
                raise AssertionError("Expected chat tool")
            if "list_models" not in tool_names:
                raise AssertionError("Expected list_models tool")
            
            print(f"   Found tools: {', '.join(tool_names)}")
        
        await tester.run_test("List available tools", test_list_tools)
        
        # Test 2: Chat with auto-selection
        async def test_auto_selection():
            result = await tester.send_request("tools/call", {
                "name": "chat",
                "arguments": {"prompt": "Say hello in exactly 5 words"}
            })
            
            data = json.loads(result["content"][0]["text"])
            if "response" not in data:
                raise AssertionError("Expected response field")
            if "model_info" not in data:
                raise AssertionError("Expected model_info field")
            
            print(f"   Provider: {data['model_info']['provider']}")
            print(f"   Model: {data['model_info']['model']}")
            print(f"   Response: {data['response'][:50]}...")
        
        await tester.run_test("Chat with auto model selection", test_auto_selection)
        
        # Test 3: Specific provider - Ollama
        async def test_ollama():
            result = await tester.send_request("tools/call", {
                "name": "chat",
                "arguments": {
                    "prompt": "What is 2+2?",
                    "provider": "ollama"
                }
            })
            
            data = json.loads(result["content"][0]["text"])
            
            # Check if it's an error due to Ollama not being available
            if "error" in data and ("ECONNREFUSED" in data["error"] or "not available" in data["error"]):
                print("   ⚠️ Ollama not available (expected if not running locally)")
                return
            
            if "error" in data:
                raise AssertionError(data["error"])
            
            if data["model_info"]["provider"] != "ollama":
                raise AssertionError(f"Expected ollama provider, got {data['model_info']['provider']}")
            
            print(f"   Model: {data['model_info']['model']}")
            print(f"   Response: {data['response'][:50]}...")
        
        await tester.run_test("Chat with Ollama provider", test_ollama)
        
        # Test 4: List models
        async def test_list_models():
            result = await tester.send_request("tools/call", {
                "name": "list_models",
                "arguments": {"provider": "openai"}
            })
            
            data = json.loads(result["content"][0]["text"])
            if "models" not in data or not isinstance(data["models"], list):
                raise AssertionError("Expected models array")
            
            print(f"   Models: {', '.join(data['models'])}")
        
        await tester.run_test("List models for OpenAI", test_list_models)
        
        # Test 5: Error handling - invalid provider
        async def test_invalid_provider():
            try:
                result = await tester.send_request("tools/call", {
                    "name": "chat",
                    "arguments": {
                        "prompt": "Hello",
                        "provider": "invalid_provider"
                    }
                })
                
                data = json.loads(result["content"][0]["text"])
                if "error" not in data:
                    raise AssertionError("Expected error for invalid provider")
                
                print(f"   Error handled: {data['error'][:50]}...")
            except RuntimeError as e:
                # Server-level error is also acceptable
                print(f"   Error handled at server level: {str(e)[:50]}...")
        
        await tester.run_test("Error handling - invalid provider", test_invalid_provider)
        
        # Test 6: Custom parameters
        async def test_custom_params():
            result = await tester.send_request("tools/call", {
                "name": "chat",
                "arguments": {
                    "prompt": "Count from 1 to 3",
                    "temperature": 0.1,
                    "max_tokens": 50
                }
            })
            
            data = json.loads(result["content"][0]["text"])
            if "error" in data:
                # If there's an API error (like missing keys), that's expected
                if any(phrase in data["error"] for phrase in ["API key", "not configured", "not available"]):
                    print(f"   ⚠️ API not available: {data['error'][:50]}...")
                    return
                raise AssertionError(data["error"])
            
            print(f"   Response: {data['response'][:50]}...")
            print(f"   Tokens used: {data['usage']['total_tokens']}")
        
        await tester.run_test("Custom parameters (temperature, max_tokens)", test_custom_params)
        
        # Test 7: Task type detection
        async def test_task_detection():
            result = await tester.send_request("tools/call", {
                "name": "chat",
                "arguments": {"prompt": "Write a creative story about a magical forest"}
            })
            
            data = json.loads(result["content"][0]["text"])
            if "error" in data:
                # If there's an API error, check if it's expected
                if any(phrase in data["error"] for phrase in ["API key", "not configured", "not available"]):
                    print(f"   ⚠️ API not available: {data['error'][:50]}...")
                    return
                raise AssertionError(data["error"])
            
            if data["model_info"]["task_type"] != "creative":
                raise AssertionError(f"Expected creative task type, got {data['model_info']['task_type']}")
            
            print(f"   Task type: {data['model_info']['task_type']}")
            print(f"   Auto-selected: {data['model_info']['auto_selected']}")
        
        await tester.run_test("Task type detection", test_task_detection)
        
        # Test 8: Python-specific features
        async def test_python_features():
            result = await tester.send_request("tools/call", {
                "name": "chat",
                "arguments": {"prompt": "Hello from Python!"}
            })
            
            data = json.loads(result["content"][0]["text"])
            if "error" in data:
                if any(phrase in data["error"] for phrase in ["API key", "not configured", "not available"]):
                    print("   ⚠️ API not available (expected)")
                    return
                raise AssertionError(data["error"])
            
            if "implementation" not in data or data["implementation"] != "python":
                raise AssertionError("Expected Python implementation marker")
            
            print(f"   Implementation: {data['implementation']}")
            print(f"   Response: {data['response'][:50]}...")
        
        await tester.run_test("Python-specific features", test_python_features)
    
    except Exception as e:
        print(f"Test suite error: {e}")
    finally:
        await tester.disconnect()
        print()
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(run_tests())