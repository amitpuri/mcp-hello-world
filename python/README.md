# Hello World MCP Server & Client (Python)

A complete, working Model Context Protocol (MCP) implementation in Python with proper project structure, demonstrating server-client communication with different greeting styles and model routing.

## 🎉 Project Status: Fully Working!

This Python implementation mirrors the Node.js version with all the same functionality:

✅ **Complete MCP Implementation** - Full JSON-RPC protocol handling with proper error management  
✅ **Multiple Greeting Styles** - Simple, formal, creative, and technical greetings  
✅ **Smart Model Routing** - Automatically routes different styles to appropriate models  
✅ **Ollama Integration Ready** - Configured for local model usage  
✅ **Comprehensive Testing** - Full test suite validates all functionality  
✅ **Clean Architecture** - Well-organized code with proper separation of concerns  
✅ **Minimal Dependencies** - Only python-dotenv for .env file support

## 📁 Project Structure

```
python/
├── client/           # MCP client implementation
│   └── client.py    # Working client with JSON-RPC communication
├── server/          # MCP server implementation  
│   └── server.py    # Main MCP server with tool handlers
├── shared/          # Shared types and constants
│   └── types.py     # Greeting styles and model routing rules
├── tests/           # Test suite
│   └── test_mcp.py  # Comprehensive MCP functionality tests
├── .env.example     # Environment configuration template
├── requirements.txt # Project dependencies (python-dotenv)
└── README.md        # This file
```

## ✨ Features

- **MCP Server**: Provides a `hello` tool with multiple greeting styles
- **Working MCP Client**: Demonstrates proper server-client communication
- **Smart Model Routing**: Automatically routes requests to different models based on style
- **Multiple Styles**: Simple, formal, creative, and technical greetings
- **Comprehensive Testing**: Full test suite validating all functionality
- **Environment Configuration**: Customizable via environment variables
- **Error Handling**: Robust error handling with proper JSON-RPC error responses
- **Type Safety**: Uses Python enums and type hints for better code quality

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   cd python
   pip install -r requirements.txt
   ```

2. **Set up environment (optional)**:
   ```bash
   cp .env.example .env
   # Edit .env to customize configuration
   ```

3. **Run the interactive demo**:
   ```bash
   python client/client.py
   ```

4. **Run comprehensive tests**:
   ```bash
   python tests/test_mcp.py
   ```

5. **Start server for MCP clients**:
   ```bash
   python server/server.py
   ```

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `python client/client.py` | Run interactive client demo |
| `python tests/test_mcp.py` | Run comprehensive test suite |
| `python server/server.py` | Start MCP server for external clients |

## 🎭 Greeting Styles

The MCP server supports four different greeting styles:

- **Simple**: `Hello, [Name]!`
- **Formal**: `Good day, [Name]. It is a pleasure to make your acquaintance.`
- **Creative**: `🌟 Greetings and salutations, magnificent [Name]! ✨`
- **Technical**: `print(f'Hello, [Name]')  # Executed successfully`

## 🤖 Model Routing

The server automatically routes different styles to different models:

- **Simple & Creative** → `claude`
- **Formal** → `openai`  
- **Technical** → `llama`

You can override this by specifying a `model` parameter in your requests.

## 🔧 Configuration

Configure the server behavior with environment variables (copy `.env.example` to `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_NAME` | `hello-world-server` | Name of the MCP server |
| `MCP_SERVER_VERSION` | `1.0.0` | Version of the MCP server |
| `DEFAULT_MODEL` | `claude` | Default model to use |
| `ENABLE_MODEL_ROUTING` | `true` | Enable automatic model routing |
| `MAX_NAME_LENGTH` | `50` | Maximum length for names |
| `ENABLE_EMOJI` | `true` | Enable emoji in creative greetings |
| `DEFAULT_GREETING_STYLE` | `simple` | Default greeting style |
| `LLAMA_ENDPOINT` | `http://localhost:11434/v1` | Ollama endpoint URL |

## 🧪 Test Results

When you run `python tests/test_mcp.py`, you'll see comprehensive validation:

```
🧪 Python MCP Hello World Test Suite

1. Testing tools/list...
✅ Available tools: hello

2. Testing simple style with Alice...
✅ Model: claude (expected: claude)
   Message: Hello, Alice!

3. Testing formal style with Bob...
✅ Model: openai (expected: openai)
   Message: Good day, Bob. It is a pleasure to make your acquaintance.

4. Testing creative style with Charlie...
✅ Model: claude (expected: claude)
   Message: 🌟 Greetings and salutations, magnificent Charlie! ✨

5. Testing technical style with Dave...
✅ Model: llama (expected: llama)
   Message: print(f'Hello, Dave')  # Executed successfully

6. Testing manual model override...
✅ Model: llama (manually specified)
   Message: Hello, Eve!

7. Testing error handling...
✅ Invalid method error handled correctly
✅ Invalid tool error handled correctly
✅ Invalid style error handled correctly

🎉 All tests completed successfully!
```

## 🔌 Using with Kiro IDE

To use this MCP server with Kiro IDE:

1. **Add to MCP configuration** (`.kiro/settings/mcp.json`):
```json
{
  "mcpServers": {
    "hello-world-python": {
      "command": "python",
      "args": ["server/server.py"],
      "cwd": "/path/to/mcp-hello-world/python",
      "disabled": false,
      "autoApprove": ["hello"]
    }
  }
}
```

2. **Restart Kiro IDE** or reconnect MCP servers

3. **Use the hello tool** in chat with different parameters

## 🛠️ Development

### Project Architecture

- **Client (`client/client.py`)**: Demonstrates MCP client implementation using asyncio and JSON-RPC
- **Server (`server/server.py`)**: MCP server with tool handlers, model routing, and error handling
- **Shared (`shared/types.py`)**: Common enums and constants used by both client and server
- **Tests (`tests/test_mcp.py`)**: Comprehensive test suite validating all functionality

### Key Implementation Details

- Uses **asyncio** for asynchronous operations in client and tests
- Implements **JSON-RPC 2.0** protocol over stdio for MCP communication
- Includes **comprehensive error handling** with proper JSON-RPC error codes
- Supports **environment-based configuration** for customization
- Uses **Python enums** and **type hints** for better code quality
- Provides **detailed logging** to stderr for debugging

## 📚 API Reference

### Tool: `hello`

**Description**: Generate a hello world message with different styles and model routing

**Parameters**:
- `name` (string, required): Name to greet
- `style` (string, optional): Greeting style - "simple", "formal", "creative", "technical"
- `model` (string, optional): Specific model to use, overrides automatic routing

**Response**:
```json
{
  "message": "Hello, Alice!",
  "style": "simple", 
  "model_used": "claude",
  "timestamp": "2025-07-16T04:18:07.310Z",
  "routing_applied": true,
  "implementation": "python"
}
```

## 🔄 Comparison with Node.js Version

This Python implementation provides identical functionality to the Node.js version:

| Feature | Node.js | Python | Status |
|---------|---------|---------|---------|
| MCP Protocol | ✅ | ✅ | Identical |
| Greeting Styles | ✅ | ✅ | Identical |
| Model Routing | ✅ | ✅ | Identical |
| Error Handling | ✅ | ✅ | Identical |
| Testing Suite | ✅ | ✅ | Identical |
| Configuration | ✅ | ✅ | Identical |
| Dependencies | MCP SDK + dotenv | python-dotenv | Both minimal |

## 🤝 Contributing

This is a reference implementation demonstrating MCP best practices in Python. Feel free to:

- Fork and extend with additional tools
- Modify greeting styles and model routing rules
- Add new test cases
- Improve error handling and logging
- Integrate with different model providers
- Add async/await patterns for better performance

## 📄 License

MIT License - feel free to use this as a starting point for your own Python MCP implementations!