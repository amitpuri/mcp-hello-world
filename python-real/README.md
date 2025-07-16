# Real Models MCP Server & Client (Python)

A complete Model Context Protocol (MCP) implementation in Python with **real AI model integrations** - Ollama (local), Claude Sonnet, and GPT-4. This is a production-ready MCP server that actually calls AI models and returns real responses.

## 🚀 Features

- **Real Model Integration**: Actual API calls to Ollama, Claude, and OpenAI
- **Automatic Model Selection**: Intelligent routing based on task type
- **Multiple Providers**: Support for local (Ollama) and cloud (Claude, GPT-4) models
- **Async Architecture**: Full async/await implementation for better performance
- **Interactive Client**: Full-featured chat interface with provider selection
- **Comprehensive Testing**: Test suite that validates real API functionality
- **Error Handling**: Robust error handling for API failures and network issues
- **Usage Tracking**: Token usage and performance metrics
- **Type Safety**: Python type hints and enums for better code quality

## 📁 Project Structure

```
python-real/
├── client/           # Interactive MCP client
│   └── client.py    # Full-featured async chat client
├── server/          # MCP server with real model integration
│   └── server.py    # Production async MCP server with API calls
├── shared/          # Shared utilities and types
│   ├── types.py     # Model providers, routing rules, and utilities
│   └── models.py    # Async API client implementations
├── tests/           # Comprehensive test suite
│   └── test_mcp.py  # Async tests with real API validation
├── .env.example     # Environment configuration template
└── requirements.txt # Dependencies including real API clients
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd python-real
pip install -r requirements.txt
```

### 2. Configure Environment

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

### Interactive Demo
```bash
python client/client.py
```

This starts an interactive chat where you can:
- Chat with auto-selected models based on task type
- Specify providers: `/ollama`, `/claude`, `/openai`
- List available models: `/models ollama`
- Get help: `help`

### Run Tests
```bash
python tests/test_mcp.py
```

Comprehensive async test suite that validates:
- MCP protocol functionality
- Real API integrations
- Error handling
- Model selection logic

### Start MCP Server
```bash
python server/server.py
```

Starts the MCP server for integration with other MCP clients.

## 🤖 Model Selection

The server automatically selects the best model for your task:

| Task Type | Auto-Selected Provider | Example Prompts |
|-----------|----------------------|-----------------|
| **Creative** | Claude | "Write a story...", "Create a poem..." |
| **Analytical** | OpenAI | "Analyze this data...", "Compare these options..." |
| **Coding** | Ollama | "Write a function...", "Debug this code..." |
| **General** | Ollama | General questions and conversations |

You can override this by specifying a provider explicitly.

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
List available models for a provider.

**Parameters:**
- `provider` (required): `ollama`, `claude`, or `openai`

## 🔌 Integration with Kiro IDE

Add to your MCP configuration (`.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "real-models-python": {
      "command": "python",
      "args": ["server/server.py"],
      "cwd": "/path/to/python-real",
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

## 💡 Example Usage

### Interactive Client Examples

```bash
# Auto-selected model (will choose based on task)
You: Write a creative story about AI

# Specific provider
You: /claude Explain the philosophy of consciousness
You: /ollama Write a Python sorting algorithm  
You: /openai Analyze the pros and cons of remote work

# List models
You: /models ollama
```

### API Response Format

```json
{
  "response": "Here's a creative story about AI...",
  "model_info": {
    "provider": "claude",
    "model": "claude-3-5-sonnet-20241022", 
    "task_type": "creative",
    "auto_selected": true
  },
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 150,
    "total_tokens": 165
  },
  "timestamp": "2025-07-16T10:30:00.000Z",
  "implementation": "python"
}
```

## 🧪 Testing

The async test suite validates real functionality:

```bash
python tests/test_mcp.py
```

**Test Coverage:**
- ✅ MCP protocol compliance
- ✅ Real API integrations (with graceful handling of missing keys)
- ✅ Model selection logic
- ✅ Error handling and recovery
- ✅ Parameter validation
- ✅ Usage tracking
- ✅ Python-specific features

**Sample Test Output:**
```
🧪 Real Models MCP Test Suite (Python)
=======================================

1. List available tools...
✅ PASSED (45ms)

2. Chat with auto model selection...
✅ PASSED (1250ms)

3. Chat with Ollama provider...
⚠️ Ollama not available (expected if not running locally)
✅ PASSED (120ms)

4. List models for OpenAI...
✅ PASSED (340ms)

📊 Test Summary: 8/8 tests passed
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Default Ollama model |
| `ANTHROPIC_API_KEY` | - | Claude API key (required for Claude) |
| `CLAUDE_MODEL` | `claude-3-5-sonnet-20241022` | Default Claude model |
| `OPENAI_API_KEY` | - | OpenAI API key (required for GPT-4) |
| `OPENAI_MODEL` | `gpt-4` | Default OpenAI model |
| `MAX_TOKENS` | `1000` | Default max tokens per response |
| `TEMPERATURE` | `0.7` | Default temperature |
| `TIMEOUT_SECONDS` | `30` | Request timeout in seconds |

### Model Routing Rules

You can customize automatic model selection by editing `shared/types.py`:

```python
MODEL_ROUTING: Dict[TaskType, ModelProvider] = {
    TaskType.CREATIVE: ModelProvider.CLAUDE,    # Stories, poems, creative writing
    TaskType.ANALYTICAL: ModelProvider.OPENAI,  # Analysis, comparisons, reasoning
    TaskType.CODING: ModelProvider.OLLAMA,      # Code generation, debugging
    TaskType.GENERAL: ModelProvider.OLLAMA,     # General conversation
}
```

## 🔧 Development

### Python-Specific Features

- **Async/Await**: Full async implementation for better performance
- **Type Hints**: Complete type annotations for better IDE support
- **Enums**: Type-safe enums for providers, task types, and error types
- **Context Managers**: Proper resource management for HTTP clients
- **Exception Handling**: Comprehensive error handling with specific error types

### Adding New Providers

1. Add provider to `shared/types.py` enum
2. Implement async API client in `shared/models.py`
3. Update routing rules
4. Add tests

### Error Handling

The system gracefully handles:
- Missing API keys (falls back to available providers)
- Network timeouts
- Rate limiting
- Invalid model names
- Ollama server not running
- Async operation cancellation

## 🔄 Comparison with Node.js Version

This Python implementation provides identical functionality to the Node.js version with Python-specific enhancements:

| Feature | Node.js | Python | Enhancement |
|---------|---------|---------|-------------|
| MCP Protocol | ✅ | ✅ | Identical |
| Model Integration | ✅ | ✅ | Async/await |
| Error Handling | ✅ | ✅ | Type-safe enums |
| Testing Suite | ✅ | ✅ | Async tests |
| Configuration | ✅ | ✅ | Type hints |
| Performance | Good | Better | Full async |

## 🚨 Important Notes

- **API Keys Required**: You need valid API keys for Claude and OpenAI
- **Ollama Optional**: Ollama is optional but provides free local inference
- **Rate Limits**: Be aware of API rate limits for cloud providers
- **Costs**: Claude and OpenAI charge per token - monitor your usage
- **Network**: Requires internet connection for cloud providers
- **Python 3.7+**: Requires Python 3.7 or higher for async/await support

## 📄 License

MIT License - Use this as a foundation for your own real MCP implementations!

## 🤝 Contributing

This is a production-ready reference implementation. Contributions welcome:

- Additional model providers (Cohere, Hugging Face, etc.)
- Enhanced async patterns
- Performance optimizations
- Additional tools beyond chat
- Better usage tracking and analytics
- Type safety improvements