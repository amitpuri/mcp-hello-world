# Hello World MCP Server & Client

A complete, working Model Context Protocol (MCP) implementation with proper project structure, demonstrating server-client communication with different greeting styles and model routing.

## 🎉 Project Status: Fully Working!

This project has been restructured and tested to ensure everything works perfectly:

✅ **Fixed MCP Client** - Replaced broken MCP SDK client with robust JSON-RPC implementation  
✅ **Ollama Integration** - Updated endpoint to work with local Ollama models  
✅ **Clean Structure** - Organized code into logical folders with proper separation  
✅ **Comprehensive Testing** - Full test suite validates all functionality  
✅ **Complete Documentation** - Detailed usage examples and API reference  
✅ **Multiple Scripts** - Convenient npm commands for all use cases

## 📁 Project Structure

```
nodejs/
├── client/           # MCP client implementation
│   └── client.js    # Working client with JSON-RPC communication
├── server/          # MCP server implementation  
│   └── server.js    # MCP server with tool handlers
├── shared/          # Shared types and constants
│   └── types.js     # Greeting styles and model routing rules
├── tests/           # Test suite
│   └── test-mcp.js  # Comprehensive MCP functionality tests
├── .env.example     # Environment configuration (Ollama endpoint)
└── package.json     # Project dependencies and scripts
```

## ✨ Features

- **MCP Server**: Provides a `hello` tool with multiple greeting styles
- **Working MCP Client**: Demonstrates proper server-client communication
- **Smart Model Routing**: Automatically routes requests to different models based on style
- **Ollama Integration**: Configured to work with local Ollama models
- **Multiple Styles**: Simple, formal, creative, and technical greetings
- **Comprehensive Testing**: Full test suite validating all functionality

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up environment (optional)**:
   ```bash
   cp .env.example .env
   # Edit .env to customize configuration
   ```

3. **Run the interactive demo**:
   ```bash
   npm run demo
   ```

4. **Run comprehensive tests**:
   ```bash
   npm test
   ```

5. **Start server for MCP clients**:
   ```bash
   npm start
   ```

## 📋 Available Scripts

| Script | Description |
|--------|-------------|
| `npm run demo` | Run interactive client demo |
| `npm run client` | Same as demo |
| `npm test` | Run comprehensive test suite |
| `npm start` | Start MCP server for external clients |
| `npm run server` | Same as start |

## Usage Examples

### Client Demo
The client demo showcases all features:
- Lists available tools
- Tests different greeting styles
- Demonstrates model routing
- Shows explicit model selection

### Server Standalone
When running the server standalone, it communicates via stdio using JSON-RPC:

```bash
# List tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node server/server.js

# Call hello tool
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"hello","arguments":{"name":"World","style":"creative"}}}' | node server/server.js
```

## Greeting Styles

- **simple**: Basic "Hello, Name!" greeting
- **formal**: Professional greeting
- **creative**: Fun greeting with emojis
- **technical**: Code-style greeting

## Model Routing

The server automatically routes requests to different models based on style:
- Simple → Claude
- Formal → OpenAI  
- Creative → Claude
- Technical → Llama

You can override this by specifying a `model` parameter explicitly.

## 🔧 Configuration

The project uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```bash
# Ollama endpoint (default: http://localhost:11434/v1)
LLAMA_ENDPOINT=http://localhost:11434/v1

# Server configuration
MCP_SERVER_NAME=hello-world-server
MCP_SERVER_VERSION=1.0.0
DEFAULT_MODEL=claude
ENABLE_MODEL_ROUTING=true
MAX_NAME_LENGTH=50
ENABLE_EMOJI=true
DEFAULT_GREETING_STYLE=simple
```

## 🧪 Test Results

When you run `npm test`, you'll see comprehensive validation:

```
🧪 MCP Hello World Test Suite

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
   Message: console.log('Hello, Dave'); // Executed successfully

6. Testing manual model override...
✅ Model: llama (manually specified)
   Message: Hello, Eve!

🎉 All tests completed successfully!
```

## 🔌 Using with Kiro IDE

To use this MCP server with Kiro IDE:

1. **Add to MCP configuration** (`.kiro/settings/mcp.json`):
```json
{
  "mcpServers": {
    "hello-world": {
      "command": "node",
      "args": ["server/server.js"],
      "cwd": "/path/to/mcp-hello-world/nodejs",
      "disabled": false,
      "autoApprove": ["hello"]
    }
  }
}
```

2. **Restart Kiro IDE** or reconnect MCP servers

3. **Use the hello tool** in chat by calling it with different parameters

## 🛠️ Development

### Project Architecture

- **Client (`client/index.js`)**: Demonstrates MCP client implementation using direct JSON-RPC communication
- **Server (`server/index.js`)**: MCP server with tool handlers and model routing logic
- **Shared (`shared/types.js`)**: Common constants and routing rules used by both client and server
- **Tests (`tests/test-mcp.js`)**: Comprehensive test suite validating all functionality

### Key Implementation Details

- Uses **JSON-RPC 2.0** protocol over stdio for MCP communication
- Implements proper **error handling** and **process cleanup**
- Supports **asynchronous tool execution** with proper response formatting
- Includes **model routing logic** based on greeting style
- Provides **comprehensive logging** for debugging

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
  "routing_applied": true
}
```

## 🤝 Contributing

This is a reference implementation demonstrating MCP best practices. Feel free to:

- Fork and extend with additional tools
- Modify greeting styles and model routing rules
- Add new test cases
- Improve error handling and logging
- Integrate with different model providers

## 📄 License

MIT License - feel free to use this as a starting point for your own MCP implementations!