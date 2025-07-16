# Real Models MCP Server & Client

A complete Model Context Protocol (MCP) implementation with **real AI model integrations** - Ollama (local), Claude Sonnet, and GPT-4. This is a production-ready MCP server that actually calls AI models and returns real responses.

## 🚀 Features

- **Real Model Integration**: Actual API calls to Ollama, Claude, and OpenAI
- **Automatic Model Selection**: Intelligent routing based on task type
- **Multiple Providers**: Support for local (Ollama) and cloud (Claude, GPT-4) models
- **Interactive Client**: Full-featured chat interface with provider selection
- **Comprehensive Testing**: Test suite that validates real API functionality
- **Error Handling**: Robust error handling for API failures and network issues
- **Usage Tracking**: Token usage and performance metrics
- **Flexible Configuration**: Environment-based configuration for all providers

## 📁 Project Structure

```
nodejs-real/
├── client/           # Interactive MCP client
│   └── client.js    # Full-featured chat client with provider selection
├── server/          # MCP server with real model integration
│   └── server.js    # Production MCP server with API calls
├── shared/          # Shared utilities and types
│   ├── types.js     # Model providers, routing rules, and utilities
│   └── models.js    # API client implementations for all providers
├── tests/           # Comprehensive test suite
│   └── test-mcp.js  # Tests with real API validation
├── .env.example     # Environment configuration template
└── package.json     # Dependencies including real API clients
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd nodejs-real
npm install
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
npm run demo
```

This starts an interactive chat where you can:
- Chat with auto-selected models based on task type
- Specify providers: `/ollama`, `/claude`, `/openai`
- List available models: `/models ollama`
- Get help: `help`

### Run Tests
```bash
npm test
```

Comprehensive test suite that validates:
- MCP protocol functionality
- Real API integrations
- Error handling
- Model selection logic

### Start MCP Server
```bash
npm start
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
- `maxTokens` (optional): Maximum response length

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
    "real-models": {
      "command": "node",
      "args": ["server/server.js"],
      "cwd": "/path/to/nodejs-real",
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
  "timestamp": "2025-07-16T10:30:00.000Z"
}
```

## 🧪 Testing

The test suite validates real functionality:

```bash
npm test
```

**Test Coverage:**
- ✅ MCP protocol compliance
- ✅ Real API integrations (with graceful handling of missing keys)
- ✅ Model selection logic
- ✅ Error handling and recovery
- ✅ Parameter validation
- ✅ Usage tracking

**Sample Test Output:**
```
🧪 Real Models MCP Test Suite
==============================

1. List available tools...
✅ PASSED (45ms)

2. Chat with auto model selection...
✅ PASSED (1250ms)

3. Chat with Ollama provider...
⚠️ Ollama not available (expected if not running locally)
✅ PASSED (120ms)

4. List models for OpenAI...
✅ PASSED (340ms)

📊 Test Summary: 7/7 tests passed
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
| `TIMEOUT_MS` | `30000` | Request timeout in milliseconds |

### Model Routing Rules

You can customize automatic model selection by editing `shared/types.js`:

```javascript
export const MODEL_ROUTING = {
  creative: MODEL_PROVIDERS.CLAUDE,    // Stories, poems, creative writing
  analytical: MODEL_PROVIDERS.OPENAI,  // Analysis, comparisons, reasoning
  coding: MODEL_PROVIDERS.OLLAMA,      // Code generation, debugging
  general: MODEL_PROVIDERS.OLLAMA,     // General conversation
  default: MODEL_PROVIDERS.OLLAMA      // Fallback
};
```

## 🔧 Development

### Adding New Providers

1. Add provider to `shared/types.js`
2. Implement API client in `shared/models.js`
3. Update routing rules
4. Add tests

### Error Handling

The system gracefully handles:
- Missing API keys (falls back to available providers)
- Network timeouts
- Rate limiting
- Invalid model names
- Ollama server not running

## 🚨 Important Notes

- **API Keys Required**: You need valid API keys for Claude and OpenAI
- **Ollama Optional**: Ollama is optional but provides free local inference
- **Rate Limits**: Be aware of API rate limits for cloud providers
- **Costs**: Claude and OpenAI charge per token - monitor your usage
- **Network**: Requires internet connection for cloud providers

## 📄 License

MIT License - Use this as a foundation for your own real MCP implementations!

## 🤝 Contributing

This is a production-ready reference implementation. Contributions welcome:

- Additional model providers (Cohere, Hugging Face, etc.)
- Enhanced error handling
- Performance optimizations
- Additional tools beyond chat
- Better usage tracking and analytics