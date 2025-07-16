#!/usr/bin/env python3
"""
Setup script for Real Models FastMCP Server

This script helps set up the FastMCP environment and validates the installation.
"""

import asyncio
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required for FastMCP")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        # Try to install FastMCP first
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "fastmcp>=0.1.0"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠️  FastMCP not available, using fallback MCP package")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "mcp>=1.0.0"
            ], check=True)
        
        # Install other dependencies
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("\n📝 Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("✅ .env file created")
        print("⚠️  Please edit .env file and add your API keys")
        return True
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ .env.example not found")
        return False

def validate_environment():
    """Validate environment configuration."""
    print("\n🔍 Validating environment...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for API keys
    api_keys = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }
    
    configured_providers = []
    for key, value in api_keys.items():
        if value and value != "your_api_key_here":
            provider = key.split("_")[0].lower()
            configured_providers.append(provider)
            print(f"✅ {provider.title()} API key configured")
        else:
            provider = key.split("_")[0].lower()
            print(f"⚠️  {provider.title()} API key not configured")
    
    if not configured_providers:
        print("⚠️  No API keys configured - only Ollama will work (if running)")
    
    # Check Ollama availability
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    print(f"ℹ️  Ollama URL: {ollama_url}")
    
    return len(configured_providers) > 0

async def test_server():
    """Test if the FastMCP server starts correctly."""
    print("\n🧪 Testing FastMCP server startup...")
    
    try:
        server_path = Path("server/server.py")
        if not server_path.exists():
            print("❌ Server file not found")
            return False
        
        # Start server process
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(server_path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait a moment for startup
        await asyncio.sleep(2)
        
        # Send a simple request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        import json
        request_json = json.dumps(request) + '\n'
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        # Read response with timeout
        try:
            response_line = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=5.0
            )
            
            if response_line:
                response = json.loads(response_line.decode().strip())
                if "result" in response and "tools" in response["result"]:
                    print("✅ FastMCP server started successfully")
                    print(f"   Found {len(response['result']['tools'])} tools")
                    success = True
                else:
                    print("❌ Invalid response from server")
                    success = False
            else:
                print("❌ No response from server")
                success = False
        
        except asyncio.TimeoutError:
            print("❌ Server startup timeout")
            success = False
        
        # Clean up
        process.terminate()
        await process.wait()
        
        return success
    
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

def print_usage_instructions():
    """Print usage instructions."""
    print("\n🚀 Setup Complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Edit .env file and add your API keys:")
    print("   - ANTHROPIC_API_KEY for Claude")
    print("   - OPENAI_API_KEY for GPT-4")
    print()
    print("2. Start the FastMCP server:")
    print("   python server/server.py")
    print()
    print("3. Run the interactive client:")
    print("   python client/client.py")
    print()
    print("4. Run tests:")
    print("   python tests/test_mcp.py")
    print()
    print("5. View comparison with traditional MCP:")
    print("   python comparison.py")
    print()
    print("📚 For more information, see README.md")

async def main():
    """Main setup function."""
    print("🔧 FastMCP Real Models Server Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Create .env file
    create_env_file()
    
    # Validate environment
    validate_environment()
    
    # Test server startup
    await test_server()
    
    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    asyncio.run(main())