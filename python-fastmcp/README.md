# Real Models FastMCP Server (Python)

A modern Model Context Protocol (MCP) implementation using **FastMCP** framework with **real AI model integrations** - Ollama (local), Claude Sonnet, and GPT-4. This is a production-ready MCP server built with FastMCP's decorator-based approach for cleaner, more maintainable code.

## ✅ Status: Fully Working

This FastMCP server is **fully operational** and tested with all three AI providers:
- **Ollama (llama3.2)** ✅ - Local model working
- **Claude Sonnet** ✅ - API integration working  
- **OpenAI GPT-4** ✅ - API integration working

All features including automatic model selection, error handling, and usage tracking are functional.

### 📊 Performance Benchmarks (Tested)
- **Claude Sonnet**: ~1.1s response time, 21 tokens
- **OpenAI GPT-4**: ~2.6s response time, 18 tokens  
- **Ollama (local)**: ~6.8s response time, 37 tokens

### 🎯 Quick Test
```bash
# Start the interactive client
python client/client.py

# Try these commands:
/ollama hello world     # Uses local Ollama
/claude hello world     # Uses Claude API
/openai hello world     # Uses OpenAI API
hello world             # Auto-selects best model
```

## 🚀 Features

- **FastMCP Framework**: Modern decorator-based MCP server development
- **Real Model Integration**: Actual API calls to Ollama, Claude, and OpenAI
- **Automatic Model Selection**: Intelligent routing based on task type
- **Multiple Providers**: Support for local (Ollama) and cloud (Claude, GPT-4) models
- **Clean Architecture**: Simplified code with FastMCP decorators
- **Interactive Client**: Full-featured chat interface with provider selection
- **Comprehensive Testing**: Test suite that validates real API functionality
- **Error Handling**: Robust error handling for API failures and network issues
- **Usage Tracking**: Token usage and performance metrics
- **Type Safety**: Python type hints and Pydantic models

## 📁 Project Structure

```
python-fastmcp/
├── server/          # FastMCP server with real model integration
│   └── server.py    # Production FastMCP server with decorators
├── client/          # Interactive client with enhanced UI
│   └── client.py    # Full-featured async chat client with colors
├── shared/          # Shared utilities and types
│   ├── types.py     # Model providers, routing rules, and Pydantic models
│   └── models.py    # Async API client implementations
├── tests/           # Comprehensive test suite
│   └── test_mcp.py  # FastMCP tests with real API validation
├── setup.py         # Automated setup and validation script
├── demo.py          # Comprehensive demonstration of FastMCP features
├── comparison.py    # FastMCP vs Traditional MCP comparison
├── QUICKSTART.md    # 5-minute getting started guide
├── .env.example     # Environment configuration template
└── requirements.txt # Dependencies including FastMCP
```

## 🛠️ Setup

### Quick Setup (Recommended)

```bash
cd python-fastmcp
python setup.py
```

The setup script will:
- Check Python version compatibility
- Install FastMCP and dependencies
- Create .env file from template
- Validate configuration
- Test server startup

### Manual Setup

#### 1. Install Dependencies

```bash
cd python-fastmcp
pip install -r requirements.txt
```

#### 2. Configure Environment

Copy the environment template and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Ollama Configuration (for local models)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Anthropic Claude Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# OpenAI Configuration  
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
```

### 3. Set Up Model Providers

#### Ollama (Local - Optional)
Install and start Ollama for local model support:
```bash
# Install Ollama (see https://ollama.ai)
# Pull a model
ollama pull llama3.2
```

#### Claude (Anthropic)
Get your API key from: https://console.anthropic.com/settings/keys

#### OpenAI (GPT-4)
Get your API key from: https://platform.openai.com/api-keys

## 🚀 Usage

### Start FastMCP Server
```bash
python server/server.py
```

### Interactive Client
```bash
python client/client.py
```

### Run Comprehensive Demo
```bash
python demo.py
```

### Run Tests
```bash
python tests/test_mcp.py
```

### Compare with Traditional MCP
```bash
python comparison.py
```

## 🔌 Integration with Kiro IDE

Add to your MCP configuration (`.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "real-models-fastmcp": {
      "command": "python",
      "args": ["server/server.py"],
      "cwd": "/path/to/python-fastmcp",
      "env": {
        "ANTHROPIC_API_KEY": "your_key_here",
        "OPENAI_API_KEY": "your_key_here"
      },
      "disabled": false,
      "autoApprove": ["chat", "list_models"]
    }
  }
}
```

## 🤖 Model Selection

The server automatically selects the best model for your task:

| Task Type | Auto-Selected Provider | Example Prompts |
|-----------|----------------------|-----------------|
| **Creative** | Claude | "Write a story...", "Create a poem..." |
| **Analytical** | OpenAI | "Analyze this data...", "Compare these options..." |
| **Coding** | Ollama | "Write a function...", "Debug this code..." |
| **General** | Ollama | General questions and conversations |

## 📋 Available Tools

### `chat`
Chat with AI models with automatic or manual provider selection.

**Parameters:**
- `prompt` (required): Your message/question
- `provider` (optional): `ollama`, `claude`, or `openai`
- `model` (optional): Specific model name
- `temperature` (optional): 0.0-1.0, controls randomness
- `max_tokens` (optional): Maximum response length

**Example:**
```json
{
  "name": "chat",
  "arguments": {
    "prompt": "Explain quantum computing in simple terms",
    "provider": "claude",
    "temperature": 0.7
  }
}
```

### `list_models`
List available models for a specific provider.

**Parameters:**
- `provider` (required): `ollama`, `claude`, or `openai`

**Example:**
```json
{
  "name": "list_models",
  "arguments": {
    "provider": "openai"
  }
}
```

## 🔄 FastMCP Advantages

This FastMCP implementation provides several advantages over traditional MCP servers:

| Feature | Traditional MCP | FastMCP | Enhancement |
|---------|-----------------|---------|-------------|
| Code Structure | Manual JSON handling | Decorators | Cleaner code |
| Type Safety | Manual validation | Pydantic models | Automatic validation |
| Error Handling | Manual try/catch | Built-in handling | Less boilerplate |
| Documentation | Manual schemas | Auto-generated | Self-documenting |
| Development Speed | Verbose setup | Minimal setup | Faster development |

## 🚨 Important Notes

- **FastMCP Framework**: Uses modern Python decorators for cleaner code
- **API Keys Required**: You need valid API keys for Claude and OpenAI
- **Ollama Optional**: Ollama is optional but provides free local inference
- **Rate Limits**: Be aware of API rate limits for cloud providers
- **Costs**: Claude and OpenAI charge per token - monitor your usage
- **Network**: Requires internet connection for cloud providers
- **Python 3.8+**: Requires Python 3.8 or higher for FastMCP support

## 📄 License

MIT License - Use this as a foundation for your own FastMCP implementations!

## 🤝 Contributing

This is a production-ready FastMCP reference implementation. Contributions welcome:

- Additional model providers (Cohere, Hugging Face, etc.)
- Enhanced FastMCP patterns
- Performance optimizations
- Additional tools beyond chat
- Better usage tracking and analytics