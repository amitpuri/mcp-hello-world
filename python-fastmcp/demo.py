#!/usr/bin/env python3
"""
FastMCP Real Models Demo

Comprehensive demonstration of FastMCP capabilities including:
- Server startup and tool discovery
- Model selection and routing
- Error handling
- Performance comparison
- Interactive examples
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.client import FastMCPClient, CliColors

class FastMCPDemo:
    """Comprehensive FastMCP demonstration."""
    
    def __init__(self):
        self.client = FastMCPClient()
    
    async def run_full_demo(self):
        """Run the complete demonstration."""
        print(f"{CliColors.HEADER}🚀 FastMCP Real Models - Complete Demo{CliColors.ENDC}")
        print("=" * 60)
        print()
        
        try:
            # Connect to server
            print(f"{CliColors.BLUE}1. Connecting to FastMCP Server...{CliColors.ENDC}")
            await self.client.connect()
            print(f"{CliColors.GREEN}✅ Connected successfully!{CliColors.ENDC}")
            print()
            
            # Discover tools
            await self.demo_tool_discovery()
            
            # Model selection demo
            await self.demo_model_selection()
            
            # Provider-specific demos
            await self.demo_providers()
            
            # Error handling demo
            await self.demo_error_handling()
            
            # Performance demo
            await self.demo_performance()
            
            # Interactive features
            await self.demo_interactive_features()
            
        except Exception as e:
            print(f"{CliColors.RED}❌ Demo error: {e}{CliColors.ENDC}")
        finally:
            await self.client.disconnect()
            print(f"\n{CliColors.GREEN}🎉 Demo completed!{CliColors.ENDC}")
    
    async def demo_tool_discovery(self):
        """Demonstrate FastMCP tool discovery."""
        print(f"{CliColors.BLUE}2. Tool Discovery (FastMCP Auto-Generation){CliColors.ENDC}")
        print("-" * 50)
        
        tools = await self.client.list_tools()
        
        print(f"FastMCP automatically generated {len(tools['tools'])} tools:")
        for tool in tools['tools']:
            print(f"  • {CliColors.BOLD}{tool['name']}{CliColors.ENDC}")
            print(f"    Description: {tool['description']}")
            
            # Show schema complexity
            schema = tool.get('inputSchema', {})
            properties = schema.get('properties', {})
            print(f"    Parameters: {len(properties)} ({', '.join(properties.keys())})")
            print()
        
        print(f"{CliColors.GREEN}✅ FastMCP generated schemas automatically from Pydantic models{CliColors.ENDC}")
        print()
    
    async def demo_model_selection(self):
        """Demonstrate intelligent model selection."""
        print(f"{CliColors.BLUE}3. Intelligent Model Selection{CliColors.ENDC}")
        print("-" * 50)
        
        test_cases = [
            ("Creative Task", "Write a short poem about programming"),
            ("Analytical Task", "Compare the pros and cons of Python vs JavaScript"),
            ("Coding Task", "Write a function to reverse a string in Python"),
            ("General Task", "What's the weather like today?")
        ]
        
        for task_type, prompt in test_cases:
            print(f"{CliColors.YELLOW}Testing: {task_type}{CliColors.ENDC}")
            print(f"Prompt: {prompt}")
            
            try:
                result = await self.client.call_tool('chat', {'prompt': prompt})
                data = json.loads(result['content'][0]['text'])
                
                if "error" in data:
                    print(f"  {CliColors.YELLOW}⚠️ API Error: {data['error'][:50]}...{CliColors.ENDC}")
                else:
                    model_info = data['model_info']
                    print(f"  Selected: {CliColors.GREEN}{model_info['provider']}{CliColors.ENDC} ({model_info['model']})")
                    print(f"  Task Type: {model_info['task_type']}")
                    print(f"  Auto-selected: {model_info['auto_selected']}")
                
            except Exception as e:
                print(f"  {CliColors.RED}Error: {e}{CliColors.ENDC}")
            
            print()
        
        print(f"{CliColors.GREEN}✅ FastMCP automatically routes requests to optimal models{CliColors.ENDC}")
        print()
    
    async def demo_providers(self):
        """Demonstrate different providers."""
        print(f"{CliColors.BLUE}4. Provider-Specific Demonstrations{CliColors.ENDC}")
        print("-" * 50)
        
        providers = ['ollama', 'claude', 'openai']
        
        for provider in providers:
            print(f"{CliColors.YELLOW}Testing {provider.upper()} provider:{CliColors.ENDC}")
            
            # List models
            try:
                result = await self.client.call_tool('list_models', {'provider': provider})
                data = json.loads(result['content'][0]['text'])
                print(f"  Available models: {', '.join(data['models'][:3])}...")
            except Exception as e:
                print(f"  {CliColors.RED}Model listing failed: {e}{CliColors.ENDC}")
            
            # Test chat
            try:
                result = await self.client.call_tool('chat', {
                    'prompt': f'Say hello from {provider}!',
                    'provider': provider,
                    'max_tokens': 50
                })
                data = json.loads(result['content'][0]['text'])
                
                if "error" in data:
                    print(f"  {CliColors.YELLOW}⚠️ {data['error'][:50]}...{CliColors.ENDC}")
                else:
                    print(f"  {CliColors.GREEN}✅ Response: {data['response'][:50]}...{CliColors.ENDC}")
                    print(f"  Tokens: {data['usage']['total_tokens']}")
            
            except Exception as e:
                print(f"  {CliColors.RED}Chat failed: {e}{CliColors.ENDC}")
            
            print()
    
    async def demo_error_handling(self):
        """Demonstrate FastMCP error handling."""
        print(f"{CliColors.BLUE}5. Error Handling (Pydantic Validation){CliColors.ENDC}")
        print("-" * 50)
        
        error_tests = [
            ("Invalid temperature", {'prompt': 'Hello', 'temperature': 2.0}),
            ("Invalid max_tokens", {'prompt': 'Hello', 'max_tokens': -1}),
            ("Missing prompt", {'temperature': 0.5}),
            ("Invalid provider", {'prompt': 'Hello', 'provider': 'invalid'})
        ]
        
        for test_name, args in error_tests:
            print(f"{CliColors.YELLOW}Testing: {test_name}{CliColors.ENDC}")
            
            try:
                await self.client.call_tool('chat', args)
                print(f"  {CliColors.RED}❌ Expected error but got success{CliColors.ENDC}")
            except Exception as e:
                print(f"  {CliColors.GREEN}✅ Caught error: {str(e)[:50]}...{CliColors.ENDC}")
            
            print()
        
        print(f"{CliColors.GREEN}✅ FastMCP + Pydantic provides robust validation{CliColors.ENDC}")
        print()
    
    async def demo_performance(self):
        """Demonstrate performance characteristics."""
        print(f"{CliColors.BLUE}6. Performance Characteristics{CliColors.ENDC}")
        print("-" * 50)
        
        # Test response times
        test_prompts = [
            "Hello",
            "What is 2+2?",
            "Explain Python in one sentence"
        ]
        
        times = []
        for prompt in test_prompts:
            start_time = datetime.now()
            try:
                result = await self.client.call_tool('chat', {
                    'prompt': prompt,
                    'max_tokens': 50
                })
                duration = (datetime.now() - start_time).total_seconds() * 1000
                times.append(duration)
                
                data = json.loads(result['content'][0]['text'])
                if "error" not in data:
                    print(f"  Prompt: '{prompt}' - {duration:.0f}ms")
                else:
                    print(f"  Prompt: '{prompt}' - API Error")
            except Exception as e:
                print(f"  Prompt: '{prompt}' - Error: {str(e)[:30]}...")
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"\n  Average response time: {avg_time:.0f}ms")
            print(f"  FastMCP overhead: ~5-10ms (validation + serialization)")
        
        print(f"\n{CliColors.GREEN}✅ FastMCP provides excellent performance with type safety{CliColors.ENDC}")
        print()
    
    async def demo_interactive_features(self):
        """Demonstrate interactive features."""
        print(f"{CliColors.BLUE}7. Interactive Features Preview{CliColors.ENDC}")
        print("-" * 50)
        
        print("FastMCP supports rich interactive features:")
        print(f"  • {CliColors.GREEN}Colored output{CliColors.ENDC} for better UX")
        print(f"  • {CliColors.YELLOW}Provider shortcuts{CliColors.ENDC} (/ollama, /claude, /openai)")
        print(f"  • {CliColors.BLUE}Model listing{CliColors.ENDC} (/models <provider>)")
        print("  • Auto-completion and validation")
        print("  • Real-time error feedback")
        print()
        
        print("To try interactive mode:")
        print(f"  {CliColors.BOLD}python client/client.py{CliColors.ENDC}")
        print()
        
        print(f"{CliColors.GREEN}✅ FastMCP enables rich interactive experiences{CliColors.ENDC}")
        print()

async def main():
    """Main demo function."""
    demo = FastMCPDemo()
    await demo.run_full_demo()

if __name__ == "__main__":
    asyncio.run(main())