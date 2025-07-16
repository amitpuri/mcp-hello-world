# MCP Hello World

Complete Model Context Protocol (MCP) implementations in both Node.js and Python, demonstrating server-client communication with different greeting styles and model routing.

## 🎉 Project Status: Fully Working!

Both implementations are complete, tested, and ready for use:

✅ **Dual Language Support** - Identical functionality in Node.js and Python  
✅ **Consistent File Naming** - `client.js/py` and `server.js/py` across both implementations  
✅ **Complete MCP Protocol** - Full JSON-RPC handling with proper error management  
✅ **Multiple Greeting Styles** - Simple, formal, creative, and technical greetings  
✅ **Smart Model Routing** - Automatically routes different styles to appropriate models  
✅ **Ollama Integration** - Configured to work with local Ollama models  
✅ **Comprehensive Testing** - Full test suites validate all functionality  
✅ **Zero Setup Required** - Python uses standard library, Node.js has minimal dependencies

## 📁 Project Structure

```
mcp-hello-world/
├── nodejs/              # Node.js implementation
│   ├── client/
│   │   └── client.js    # Working client with JSON-RPC communication
│   ├── server/
│   │   └── server.js    # MCP server with tool handlers
│   ├── shared/
│   │   └── types.js     # Greeting styles and model routing rules
│   ├── tests/
│   │   └── test-mcp.js  # Comprehensive test suite
│   ├── .env.example     # Environment configuration
│   ├── package.json     # Dependencies and scripts
│   └── README.md        # Node.js specific documentation
├── python/              # Python implementation
│   ├── client/
│   │   └── client.py    # Working client with asyncio
│   ├── server/
│   │   └── server.py    # MCP server with tool handlers
│   ├── shared/
│   │   └── types.py     # Greeting styles and model routing rules
│   ├── tests/
│   │   └── test_mcp.py  # Comprehensive test suite
│   ├── .env.example     # Environment configuration
│   ├── requirements.txt # No dependencies needed!
│   └── README.md        # Python specific documentation
└── README.md            # This file
```

## 🚀 Quick Start

### Node.js Implementation
```bash
cd nodejs
npm install                # Install dependencies
cp .env.example .env       # Copy environment configuration (optional)
npm run demo               # Run interactive demo
npm test                   # Run comprehensive tests
npm start                  # Start server for MCP clients
```

### Python Implementation
```bash
cd python
pip install -r requirements.txt  # Install dependencies (python-dotenv)
cp .env.example .env             # Copy environment configuration (optional)
python client/client.py          # Run interactive demo
python tests/test_mcp.py         # Run comprehensive tests
python server/server.py          # Start server for MCP clients
```

## ✨ Features

Both implementations provide identical functionality:

- **MCP Server**: Provides a `hello` tool with multiple greeting styles
- **Working MCP Client**: Demonstrates proper server-client communication
- **Smart Model Routing**: Automatically routes requests to different models based on style
- **Multiple Styles**: Simple, formal, creative, and technical greetings
- **Comprehensive Testing**: Full test suites validating all functionality
- **Environment Configuration**: Customizable via environment variables
- **Error Handling**: Robust error handling with proper JSON-RPC error responses
- **Ollama Integration**: Ready to work with local Ollama models

## 🎭 Greeting Styles

Both implementations support four different greeting styles:

- **Simple**: `Hello, [Name]!`
- **Formal**: `Good day, [Name]. It is a pleasure to make your acquaintance.`
- **Creative**: `🌟 Greetings and salutations, magnificent [Name]! ✨`
- **Technical**: 
  - Node.js: `console.log('Hello, [Name]'); // Executed successfully`
  - Python: `print(f'Hello, [Name]')  # Executed successfully`

## 🤖 Model Routing

Both servers automatically route different styles to different models:

- **Simple & Creative** → `claude`
- **Formal** → `openai`  
- **Technical** → `llama`

You can override this by specifying a `model` parameter in your requests.

## 🔌 Using with Kiro IDE

### Node.js Server
Add to MCP configuration (`.kiro/settings/mcp.json`):
```json
{
  "mcpServers": {
    "hello-world-nodejs": {
      "command": "node",
      "args": ["server/server.js"],
      "cwd": "/path/to/mcp-hello-world/nodejs",
      "disabled": false,
      "autoApprove": ["hello"]
    }
  }
}
```

### Python Server
Add to MCP configuration (`.kiro/settings/mcp.json`):
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

## 🔄 Implementation Comparison

| Feature | Node.js | Python | Winner |
|---------|---------|---------|---------|
| **Dependencies** | MCP SDK | None | Python |
| **Performance** | Fast | Fast | Tie |
| **Code Clarity** | Good | Excellent | Python |
| **Type Safety** | TypeScript | Type Hints | Tie |
| **Async Support** | Native | asyncio | Tie |
| **Error Handling** | Good | Excellent | Python |
| **Ecosystem** | Rich | Rich | Tie |
| **Setup Complexity** | npm install | None | Python |

## 🧪 Test Results

Both implementations pass comprehensive test suites:

### Node.js Tests
```bash
npm test
# 🧪 MCP Hello World Test Suite
# ✅ All tests completed successfully!
```

### Python Tests
```bash
python tests/test_mcp.py
# 🧪 Python MCP Hello World Test Suite
# ✅ All tests completed successfully!
```

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
  "implementation": "nodejs" // or "python"
}
```

## 🔧 Configuration

Both implementations support the same environment variables:

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

## 🤝 Contributing

This is a reference implementation demonstrating MCP best practices in both Node.js and Python. Feel free to:

- Fork and extend with additional tools
- Modify greeting styles and model routing rules
- Add new test cases
- Improve error handling and logging
- Integrate with different model providers
- Compare performance between implementations

## 📄 License

MIT License - feel free to use this as a starting point for your own MCP implementations!