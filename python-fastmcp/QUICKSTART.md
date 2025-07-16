# FastMCP Quick Start Guide

Get up and running with FastMCP Real Models Server in 5 minutes!

## ✅ Status: Ready to Use
This FastMCP server is fully configured and tested. All three providers (Ollama, Claude, OpenAI) are working correctly.

## 🚀 Quick Start (5 minutes)

### 1. Setup
```bash
cd python-fastmcp
python setup.py
```

### 2. Add API Keys
Edit `.env` file:
```bash
ANTHROPIC_API_KEY=your_claude_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 3. Start Server
```bash
python server/server.py
```

### 4. Try Interactive Client
```bash
# In another terminal
python client/client.py
```

## 💬 Quick Examples

### Auto Model Selection
```
You: Write a creative story about AI
# → Automatically uses Claude for creative tasks
```

### Specific Provider
```
You: /ollama Write a Python function to sort a list
# → Uses Ollama for coding tasks
```

### List Models
```
You: /models openai
# → Shows available OpenAI models
```

## 🧪 Test Everything
```bash
python demo.py
```

## 🔧 Troubleshooting

### Server won't start?
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r requirements.txt`

### API errors?
- Verify API keys in `.env` file
- Check internet connection
- Try Ollama locally: `ollama pull llama3.2`

### Import errors?
- Make sure you're in the `python-fastmcp` directory
- Try: `pip install fastmcp` or `pip install mcp`

## 📚 Next Steps

1. **Read the full README.md** for detailed documentation
2. **Run comparison.py** to see FastMCP vs traditional MCP
3. **Explore the code** in `server/server.py` to see FastMCP decorators
4. **Add your own tools** using `@app.tool()` decorators

## 🎯 Key FastMCP Benefits

- **Less Code**: 50 lines vs 200+ for traditional MCP
- **Type Safety**: Pydantic models catch errors early
- **Auto Schemas**: No manual JSON schema writing
- **Better DX**: Modern Python patterns and IDE support

Happy coding with FastMCP! 🚀