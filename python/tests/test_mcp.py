#!/usr/bin/env python3
"""
Comprehensive MCP Test Suite (Python Implementation)

Tests all functionality of the Hello World MCP server:
- Tool discovery and listing
- All greeting styles with proper model routing
- Manual model override functionality
- Error handling and edge cases
- JSON-RPC protocol compliance
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.types import HelloWorldScenario, ModelProvider, DEFAULT_ROUTING_RULES

class MCPTester:
    """Comprehensive MCP server tester."""
    
    def __init__(self):
        """Initialize the tester."""
        self.server_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "server", 
            "server.py"
        )

    async def test_mcp(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a single request to the MCP server and get response."""
        process = await asyncio.create_subprocess_exec(
            sys.executable, self.server_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Send request
        request_json = json.dumps(request) + '\n'
        stdout, stderr = await process.communicate(request_json.encode())
        
        # Parse response
        output = stdout.decode().strip()
        if not output:
            error_output = stderr.decode().strip()
            raise Exception(f"No output from server. Error: {error_output}")
        
        return json.loads(output)

    async def test_tools_list(self) -> Dict[str, Any]:
        """Test the tools/list functionality."""
        print("1. Testing tools/list...")
        response = await self.test_mcp({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        })
        
        # Validate response structure
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) > 0
        
        tool = response["result"]["tools"][0]
        assert tool["name"] == "hello"
        assert "description" in tool
        assert "inputSchema" in tool
        
        print(f"✅ Available tools: {tool['name']}")
        print(f"   Description: {tool['description']}")
        print()
        
        return response

    async def test_greeting_styles(self) -> List[Dict[str, Any]]:
        """Test all greeting styles with automatic model routing."""
        print("2-5. Testing greeting styles with model routing...")
        
        test_cases = [
            {
                "name": "Alice", 
                "style": HelloWorldScenario.SIMPLE.value,
                "expected_model": DEFAULT_ROUTING_RULES[HelloWorldScenario.SIMPLE].value
            },
            {
                "name": "Bob", 
                "style": HelloWorldScenario.FORMAL.value,
                "expected_model": DEFAULT_ROUTING_RULES[HelloWorldScenario.FORMAL].value
            },
            {
                "name": "Charlie", 
                "style": HelloWorldScenario.CREATIVE.value,
                "expected_model": DEFAULT_ROUTING_RULES[HelloWorldScenario.CREATIVE].value
            },
            {
                "name": "Dave", 
                "style": HelloWorldScenario.TECHNICAL.value,
                "expected_model": DEFAULT_ROUTING_RULES[HelloWorldScenario.TECHNICAL].value
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_cases, 2):
            print(f"{i}. Testing {test_case['style']} style with {test_case['name']}...")
            
            response = await self.test_mcp({
                "jsonrpc": "2.0",
                "id": i,
                "method": "tools/call",
                "params": {
                    "name": "hello",
                    "arguments": {
                        "name": test_case["name"],
                        "style": test_case["style"]
                    }
                }
            })
            
            # Parse result
            result = json.loads(response["result"]["content"][0]["text"])
            results.append(result)
            
            # Validate result
            assert result["model_used"] == test_case["expected_model"]
            assert result["style"] == test_case["style"]
            assert result["routing_applied"] == True
            assert result["implementation"] == "python"
            assert test_case["name"] in result["message"]
            
            print(f"✅ Model: {result['model_used']} (expected: {test_case['expected_model']})")
            print(f"   Message: {result['message']}")
            print(f"   Routing Applied: {result['routing_applied']}")
            print()
        
        return results

    async def test_manual_model_override(self) -> Dict[str, Any]:
        """Test manual model override functionality."""
        print("6. Testing manual model override...")
        
        response = await self.test_mcp({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "hello",
                "arguments": {
                    "name": "Eve",
                    "style": HelloWorldScenario.SIMPLE.value,
                    "model": ModelProvider.LLAMA.value
                }
            }
        })
        
        result = json.loads(response["result"]["content"][0]["text"])
        
        # Validate manual override
        assert result["model_used"] == ModelProvider.LLAMA.value
        assert result["routing_applied"] == False
        assert result["style"] == HelloWorldScenario.SIMPLE.value
        assert "Eve" in result["message"]
        
        print(f"✅ Model: {result['model_used']} (manually specified)")
        print(f"   Message: {result['message']}")
        print(f"   Routing Applied: {result['routing_applied']}")
        print()
        
        return result

    async def test_error_handling(self) -> None:
        """Test error handling for invalid requests."""
        print("7. Testing error handling...")
        
        # Test invalid method
        response = await self.test_mcp({
            "jsonrpc": "2.0",
            "id": 7,
            "method": "invalid/method"
        })
        
        assert "error" in response
        assert response["error"]["code"] == -32601
        print("✅ Invalid method error handled correctly")
        
        # Test invalid tool
        response = await self.test_mcp({
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "invalid_tool",
                "arguments": {}
            }
        })
        
        assert "error" in response
        assert response["error"]["code"] == -32601
        print("✅ Invalid tool error handled correctly")
        
        # Test invalid style
        response = await self.test_mcp({
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "hello",
                "arguments": {
                    "name": "Test",
                    "style": "invalid_style"
                }
            }
        })
        
        assert "error" in response
        assert response["error"]["code"] == -32602
        print("✅ Invalid style error handled correctly")
        print()

    async def run_comprehensive_tests(self):
        """Run the complete test suite."""
        print("🧪 Python MCP Hello World Test Suite\n")
        
        try:
            # Test 1: Tools list
            await self.test_tools_list()
            
            # Tests 2-5: Greeting styles
            await self.test_greeting_styles()
            
            # Test 6: Manual model override
            await self.test_manual_model_override()
            
            # Test 7-9: Error handling
            await self.test_error_handling()
            
            print("🎉 All tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise

async def main():
    """Main entry point for the test suite."""
    tester = MCPTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())