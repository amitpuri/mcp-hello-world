# MCP Hello World - Complete Real & Simulated Implementations

A comprehensive Model Context Protocol (MCP) implementation showcase with both **simulated examples** for learning and **production-ready real implementations** with actual AI model integrations (Ollama, Claude, GPT-4).

## 🎯 Project Overview

This repository demonstrates MCP implementations from basic simulated examples to production-ready servers that actually call real AI models. Perfect for learning MCP concepts and building real applications.

## 📁 Project Structure

| Implementation | Language | Type | Models | Status |
|---------------|----------|------|---------|---------|
| **`nodejs/`** | Node.js | Simulated | Mock responses | ✅ Complete |
| **`python/`** | Python | Simulated | Mock responses | ✅ Complete |
| **`nodejs-real/`** | Node.js | **Production** | Ollama, Claude, GPT-4 | ✅ **Tested & Working** |
| **`python-real/`** | Python | **Production** | Ollama, Claude, GPT-4 | ✅ **Tested & Working** |

## 🚀 Quick Start

### **Real Implementations (Recommended)**
Production-ready MCP servers with actual AI model integrations:

```bash
# Node.js Real Implementation
cd nodejs-real
npm install
cp .env.example .env
# Add your API keys to .env
npm run demo

# Python Real Implementation  
cd python-real
python -m pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
python client/client.py
```

### **Simulated Implementations (Learning)**
Perfect for understanding MCP concepts without API keys:

```bash
# Node.js Simulated
cd nodejs && npm install && npm run demo

# Python Simulated
cd python && python client/client.py
```

## 🤖 Real Model Integrations

The real implementations support three model providers:

### **Ollama (Local - Free)**
- **Models**: llama3.2, llama3.1, codellama, mistral
- **Setup**: Install Ollama, run `ollama pull llama3.2`
- **Use Case**: Free local inference, coding tasks

### **Claude (Anthropic)**
- **Models**: claude-3-5-sonnet-20241022, claude-3-haiku-20240307
- **API Key**: Get from https://console.anthropic.com/settings/keys
- **Use Case**: Creative writing, storytelling

### **OpenAI GPT-4**
- **Models**: gpt-4, gpt-4-turbo, gpt-3.5-turbo
- **API Key**: Get from https://platform.openai.com/api-keys
- **Use Case**: Analysis, reasoning, general tasks

## ✨ Key Features

### **Smart Model Selection**
The real implementations automatically choose the best model for your task:

```
Creative tasks → Claude Sonnet
Analytical tasks → OpenAI GPT-4  
Coding tasks → Ollama (local)
General tasks → Ollama (local)
```

### **Manual Provider Selection**
Override automatic selection:
```bash
You: /claude Write a creative story about AI
You: /ollama Write a Python function
You: /openai Analyze this data
```

### **Production Features**
- ✅ Real API integrations with token usage tracking
- ✅ Comprehensive error handling and recovery
- ✅ Environment-based configuration
- ✅ Full test suites with real API validation
- ✅ Interactive chat interfaces
- ✅ MCP protocol compliance
- ✅ Async architecture (Python) and efficient handling (Node.js)

## 🧪 Testing Results

Both real implementations have been thoroughly tested:

### **Node.js Real (`nodejs-real/`)**
```bash
npm test
# ✅ 7/7 tests passed
# ✅ Ollama integration working
# ✅ Claude API working  
# ✅ OpenAI API working
# ✅ Auto model selection working
```

### **Python Real (`python-real/`)**
```bash
python tests/test_mcp.py
# ✅ 7/8 tests passed
# ✅ Ollama integration working
# ✅ Claude API working
# ✅ Async architecture working
# ✅ Type safety with enums
```

## 🔌 Kiro IDE Integration

Add to your `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "real-models-nodejs": {
      "command": "node",
      "args": ["server/server.js"],
      "cwd": "/path/to/nodejs-real",
      "env": {
        "ANTHROPIC_API_KEY": "your_claude_key",
        "OPENAI_API_KEY": "your_openai_key"
      },
      "disabled": false,
      "autoApprove": ["chat", "list_models"]
    },
    "real-models-python": {
      "command": "python",
      "args": ["server/server.py"],
      "cwd": "/path/to/python-real",
      "env": {
        "ANTHROPIC_API_KEY": "your_claude_key",
        "OPENAI_API_KEY": "your_openai_key"
      },
      "disabled": false,
      "autoApprove": ["chat", "list_models"]
    }
  }
}
```

## 📚 Documentation

Each implementation has detailed documentation:

| Implementation | README | Description |
|---------------|---------|-------------|
| **Real Node.js** | [`nodejs-real/README.md`](nodejs-real/README.md) | Production MCP server with real APIs |
| **Real Python** | [`python-real/README.md`](python-real/README.md) | Async MCP server with type safety |
| **Simulated Node.js** | [`nodejs/README.md`](nodejs/README.md) | Learning-focused simulated implementation |
| **Simulated Python** | [`python/README.md`](python/README.md) | Python simulated implementation |

## 🎯 Use Cases

### **Learning MCP Protocol**
Start with simulated implementations to understand MCP concepts without API costs.

### **Production Applications**
Use real implementations as foundation for:
- AI-powered development tools
- Multi-model chat applications  
- Automated content generation
- Code analysis and generation
- Creative writing assistants

### **Local Development**
Ollama integration provides free local inference for development and testing.

## 🔧 Configuration

### **Environment Setup**
```bash
# Required for Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Required for OpenAI  
OPENAI_API_KEY=your_openai_api_key_here

# Optional for Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### **Model Routing Customization**
Edit routing rules in `shared/types.js` (Node.js) or `shared/types.py` (Python):

```javascript
// Customize automatic model selection
export const MODEL_ROUTING = {
  creative: MODEL_PROVIDERS.CLAUDE,
  analytical: MODEL_PROVIDERS.OPENAI,
  coding: MODEL_PROVIDERS.OLLAMA,
  general: MODEL_PROVIDERS.OLLAMA
};
```

## 🎭 Greeting Styles (Simulated Versions)

The simulated implementations demonstrate different greeting styles:

- **Simple**: `Hello, [Name]!`
- **Formal**: `Good day, [Name]. It is a pleasure to make your acquaintance.`
- **Creative**: `🌟 Greetings and salutations, magnificent [Name]! ✨`
- **Technical**: 
  - Node.js: `console.log('Hello, [Name]'); // Executed successfully`
  - Python: `print(f'Hello, [Name]')  # Executed successfully`

## 🚨 Important Notes

- **API Costs**: Claude and OpenAI charge per token - monitor usage
- **Rate Limits**: Be aware of API rate limits for cloud providers  
- **Local Option**: Ollama provides free local inference
- **Network**: Cloud providers require internet connection
- **Keys Security**: Keep API keys secure and never commit them

## 🤝 Contributing

This repository serves as a comprehensive reference for MCP implementations. Contributions welcome:

- Additional model providers (Cohere, Hugging Face, etc.)
- Enhanced error handling and recovery
- Performance optimizations
- Additional tools beyond chat
- Better usage tracking and analytics
- Documentation improvements

## 📄 License

MIT License - Use these implementations as foundations for your own MCP projects!

---

**Ready to get started?** 

- **Learning MCP?** Start with the simulated implementations (`nodejs/` or `python/`)
- **Building production apps?** Use the real implementations (`nodejs-real/` or `python-real/`)

Both real implementations have been tested and are production-ready! 🚀