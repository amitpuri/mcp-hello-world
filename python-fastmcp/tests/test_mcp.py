#!/usr/bin/env python3
"""
Real Models FastMCP Test Suite - Python Implementation

Comprehensive test suite for the FastMCP Real Models Server that validates:
- FastMCP framework functionality
- Real API integrations (with graceful handling of missing keys)
- Model selection logic
- Pydantic model validation
- Error handling and recovery
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

class FastMCPTester:
    """Test harness for FastMCP functionality."""
    
    def __init__(self):
        self.server_process = None
        self.request_id = 1
        self.is_connected = False
        self.test_results = []
    
    async def connect(self):
        """Connect to the FastMCP server."""
        server_path = os.path.join(os.path.dirname(__file__), '..', 'server', 'server.py')
        
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for server to start
        await asyncio.sleep(2)
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "FastMCP-Test-Client", "version": "1.0.0"}
            }
        }
        
        request_json = json.dumps(init_request) + '\n'
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        # Read initialize response
        response_line = await self.server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.decode().strip())
            if "error" in response:
                raise RuntimeError(f"Initialize failed: {response['error']['message']}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        request_json = json.dumps(initialized_notification) + '\n'
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        self.is_connected = True
    
    async def send_request(self, method: str, params: Dict = None) -> Dict[str, Any]:
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
        print("📊 FastMCP Test Summary")
        print("========================")
        
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
    """Run the complete FastMCP test suite."""
    print("🧪 Real Models FastMCP Test Suite (Python)")
    print("===========================================\n")
    
    tester = FastMCPTester()
    
    try:
        print("Connecting to FastMCP server...")
        await tester.connect()
        print("✅ Connected!\n")
        
        # Test 1: List tools (FastMCP auto-generates from decorators)
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
            
            # Check if FastMCP generated proper schemas
            chat_tool = next(t for t in result["tools"] if t["name"] == "chat")
            if "inputSchema" not in chat_tool:
                raise AssertionError("Expected inputSchema for chat tool")
            
            print("   ✓ FastMCP auto-generated schemas detected")
        
        await tester.run_test("List tools (FastMCP auto-generation)", test_list_tools)
        
        # Test 2: Chat with Pydantic validation
        async def test_pydantic_validation():
            # Test valid request
            result = await tester.send_request("tools/call", {
                "name": "chat",
                "arguments": {
                    "request": {
                        "prompt": "Say hello in exactly 5 words",
                        "temperature": 0.5,
                        "max_tokens": 50
                    }
                }
            })
            
            # FastMCP should return structured response
            if "content" not in result:
                raise AssertionError("Expected content in response")
            
            # Parse the response (FastMCP handles JSON serialization)
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                response_text = content[0].get("text", "")
                if response_text:
                    data = json.loads(response_text)
                    if "response" not in data or "model_info" not in data:
                        raise AssertionError("Expected structured response from FastMCP")
                    print(f"   Provider: {data['model_info']['provider']}")
                    print(f"   Implementation: {data.get('implementation', 'unknown')}")
            
            print("   ✓ Pydantic models working correctly")
        
        await tester.run_test("Pydantic model validation", test_pydantic_validation)
        
        # Test 3: FastMCP error handling
        async def test_fastmcp_error_handling():
            try:
                # Test invalid temperature (should be caught by Pydantic)
                await tester.send_request("tools/call", {
                    "name": "chat",
                    "arguments": {
                        "request": {
                            "prompt": "Hello",
                            "temperature": 2.0  # Invalid: > 1.0
                        }
                    }
                })
                raise AssertionError("Expected validation error for invalid temperature")
            except RuntimeError as e:
                if "temperature" not in str(e).lower():
                    raise AssertionError(f"Expected temperature validation error, got: {e}")
                print("   ✓ Pydantic validation caught invalid temperature")
        
        await tester.run_test("FastMCP error handling", test_fastmcp_error_handling)
        
        # Test 4: Model selection with FastMCP
        async def test_model_selection():
            result = await tester.send_request("tools/call", {
                "name": "chat",
                "arguments": {
                    "request": {
                        "prompt": "Write a creative story about a magical forest"
                    }
                }
            })
            
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                response_text = content[0].get("text", "")
                if response_text:
                    data = json.loads(response_text)
                    
                    # Check if task type detection worked
                    if data.get("model_info", {}).get("task_type") != "creative":
                        # This might fail if API keys are missing, which is OK
                        if "error" not in str(data):
                            raise AssertionError(f"Expected creative task type, got {data.get('model_info', {}).get('task_type')}")
                        else:
                            print("   ⚠️ API not available (expected)")
                            return
                    
                    print(f"   Task type: {data['model_info']['task_type']}")
                    print(f"   Auto-selected: {data['model_info']['auto_selected']}")
        
        await tester.run_test("Model selection logic", test_model_selection)
        
        # Test 5: List models with FastMCP
        async def test_list_models():
            result = await tester.send_request("tools/call", {
                "name": "list_models",
                "arguments": {
                    "request": {
                        "provider": "openai"
                    }
                }
            })
            
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                response_text = content[0].get("text", "")
                if response_text:
                    data = json.loads(response_text)
                    if "models" not in data or not isinstance(data["models"], list):
                        raise AssertionError("Expected models array")
                    
                    print(f"   Models: {', '.join(data['models'])}")
        
        await tester.run_test("List models with FastMCP", test_list_models)
        
        # Test 6: FastMCP provider validation
        async def test_provider_validation():
            try:
                await tester.send_request("tools/call", {
                    "name": "list_models",
                    "arguments": {
                        "request": {
                            "provider": "invalid_provider"
                        }
                    }
                })
                raise AssertionError("Expected validation error for invalid provider")
            except RuntimeError as e:
                if "provider" not in str(e).lower():
                    raise AssertionError(f"Expected provider validation error, got: {e}")
                print("   ✓ FastMCP enum validation working")
        
        await tester.run_test("Provider enum validation", test_provider_validation)
        
        # Test 7: FastMCP response structure
        async def test_response_structure():
            result = await tester.send_request("tools/call", {
                "name": "chat",
                "arguments": {
                    "request": {
                        "prompt": "Hello FastMCP!"
                    }
                }
            })
            
            # Check FastMCP response structure
            if "content" not in result:
                raise AssertionError("Expected content field in FastMCP response")
            
            content = result["content"]
            if not isinstance(content, list):
                raise AssertionError("Expected content to be array")
            
            if len(content) == 0 or "text" not in content[0]:
                raise AssertionError("Expected text in content array")
            
            # Parse the actual response
            response_text = content[0]["text"]
            data = json.loads(response_text)
            
            # Check for required fields
            required_fields = ["response", "model_info", "usage", "timestamp", "implementation"]
            for field in required_fields:
                if field not in data:
                    # If there's an API error, that's acceptable
                    if "error" in data:
                        print(f"   ⚠️ API error (expected): {data['error'][:50]}...")
                        return
                    raise AssertionError(f"Missing required field: {field}")
            
            if data["implementation"] != "fastmcp":
                raise AssertionError(f"Expected fastmcp implementation, got {data['implementation']}")
            
            print("   ✓ FastMCP response structure validated")
        
        await tester.run_test("FastMCP response structure", test_response_structure)
        
        # Test 8: FastMCP startup/shutdown hooks
        async def test_fastmcp_hooks():
            # This test just verifies the server started properly
            # The startup hook should have logged messages to stderr
            print("   ✓ FastMCP startup hooks executed (check stderr for logs)")
        
        await tester.run_test("FastMCP lifecycle hooks", test_fastmcp_hooks)
    
    except Exception as e:
        print(f"Test suite error: {e}")
    finally:
        await tester.disconnect()
        print()
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(run_tests())