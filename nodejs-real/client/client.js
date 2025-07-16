#!/usr/bin/env node

import { spawn } from 'child_process';
import { createReadStream, createWriteStream } from 'fs';
import { createInterface } from 'readline';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class MCPClient {
  constructor() {
    this.requestId = 1;
    this.serverProcess = null;
    this.isConnected = false;
  }

  async connect() {
    return new Promise((resolve, reject) => {
      // Start the MCP server
      const serverPath = path.join(__dirname, '..', 'server', 'server.js');
      this.serverProcess = spawn('node', [serverPath], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.serverProcess.on('error', (error) => {
        console.error('Failed to start server:', error);
        reject(error);
      });

      this.serverProcess.stderr.on('data', (data) => {
        // Server logs go to stderr, display them for debugging
        console.log('Server:', data.toString().trim());
      });

      // Wait a moment for server to start
      setTimeout(() => {
        this.isConnected = true;
        resolve();
      }, 1000);
    });
  }

  async sendRequest(method, params = {}) {
    if (!this.isConnected) {
      throw new Error('Client not connected to server');
    }

    return new Promise((resolve, reject) => {
      const request = {
        jsonrpc: '2.0',
        id: this.requestId++,
        method,
        params
      };

      let responseData = '';
      
      const onData = (data) => {
        responseData += data.toString();
        
        // Try to parse complete JSON responses
        const lines = responseData.split('\n');
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim();
          if (line) {
            try {
              const response = JSON.parse(line);
              if (response.id === request.id) {
                this.serverProcess.stdout.removeListener('data', onData);
                if (response.error) {
                  reject(new Error(response.error.message || 'Server error'));
                } else {
                  resolve(response.result);
                }
                return;
              }
            } catch (e) {
              // Continue trying to parse
            }
          }
        }
        responseData = lines[lines.length - 1]; // Keep incomplete line
      };

      this.serverProcess.stdout.on('data', onData);

      // Send request
      this.serverProcess.stdin.write(JSON.stringify(request) + '\n');

      // Timeout after 30 seconds
      setTimeout(() => {
        this.serverProcess.stdout.removeListener('data', onData);
        reject(new Error('Request timeout'));
      }, 30000);
    });
  }

  async listTools() {
    return await this.sendRequest('tools/list');
  }

  async callTool(name, args) {
    return await this.sendRequest('tools/call', { name, arguments: args });
  }

  async disconnect() {
    if (this.serverProcess) {
      this.serverProcess.kill();
      this.isConnected = false;
    }
  }
}

// Interactive demo
async function runDemo() {
  console.log('🤖 Real Models MCP Client Demo');
  console.log('===============================\n');

  const client = new MCPClient();
  
  try {
    console.log('Connecting to MCP server...');
    await client.connect();
    console.log('✅ Connected!\n');

    // List available tools
    console.log('📋 Available tools:');
    const tools = await client.listTools();
    tools.tools.forEach(tool => {
      console.log(`  • ${tool.name}: ${tool.description}`);
    });
    console.log();

    // Interactive chat loop
    const rl = createInterface({
      input: process.stdin,
      output: process.stdout
    });

    console.log('💬 Interactive Chat (type "quit" to exit, "help" for commands)');
    console.log('You can specify provider with: /ollama, /claude, /openai');
    console.log('Example: /claude Tell me a creative story about AI\n');

    while (true) {
      const input = await new Promise(resolve => {
        rl.question('You: ', resolve);
      });

      if (input.toLowerCase() === 'quit' || input.toLowerCase() === 'exit') {
        break;
      }

      if (input.toLowerCase() === 'help') {
        console.log('\nAvailable commands:');
        console.log('  /ollama <prompt>  - Use Ollama (local)');
        console.log('  /claude <prompt>  - Use Claude');
        console.log('  /openai <prompt>  - Use OpenAI GPT-4');
        console.log('  /models <provider> - List models for provider');
        console.log('  help             - Show this help');
        console.log('  quit/exit        - Exit the demo\n');
        continue;
      }

      if (input.startsWith('/models ')) {
        const provider = input.substring(8).trim();
        try {
          console.log(`\n🔍 Getting models for ${provider}...`);
          const result = await client.callTool('list_models', { provider });
          const data = JSON.parse(result.content[0].text);
          console.log(`\n📋 Available ${data.provider} models:`);
          data.models.forEach(model => console.log(`  • ${model}`));
          console.log();
        } catch (error) {
          console.log(`❌ Error: ${error.message}\n`);
        }
        continue;
      }

      let provider = null;
      let prompt = input;

      // Check for provider prefix
      if (input.startsWith('/')) {
        const parts = input.split(' ');
        const providerCmd = parts[0].substring(1);
        if (['ollama', 'claude', 'openai'].includes(providerCmd)) {
          provider = providerCmd;
          prompt = parts.slice(1).join(' ');
        }
      }

      if (!prompt.trim()) {
        console.log('Please enter a prompt.\n');
        continue;
      }

      try {
        console.log('\n🤔 Thinking...');
        const startTime = Date.now();
        
        const args = { prompt };
        if (provider) args.provider = provider;

        const result = await client.callTool('chat', args);
        const data = JSON.parse(result.content[0].text);
        
        const duration = Date.now() - startTime;

        if (data.error) {
          console.log(`❌ Error: ${data.error}\n`);
        } else {
          console.log(`\n🤖 ${data.model_info.provider.toUpperCase()} (${data.model_info.model}):`);
          console.log(data.response);
          console.log(`\n📊 Usage: ${data.usage.total_tokens} tokens | ${duration}ms`);
          if (data.model_info.auto_selected) {
            console.log(`🎯 Auto-selected for task: ${data.model_info.task_type}`);
          }
          console.log();
        }
      } catch (error) {
        console.log(`❌ Error: ${error.message}\n`);
      }
    }

    rl.close();

  } catch (error) {
    console.error('Demo error:', error);
  } finally {
    await client.disconnect();
    console.log('\n👋 Goodbye!');
  }
}

// Example API calls
async function runExamples() {
  console.log('🧪 Real Models MCP Examples');
  console.log('============================\n');

  const client = new MCPClient();
  
  try {
    await client.connect();

    // Example 1: Auto-selected model for creative task
    console.log('1. Creative task (auto-selected model):');
    let result = await client.callTool('chat', {
      prompt: 'Write a short creative story about a robot learning to paint'
    });
    let data = JSON.parse(result.content[0].text);
    console.log(`   Model: ${data.model_info.provider} (${data.model_info.model})`);
    console.log(`   Response: ${data.response.substring(0, 100)}...\n`);

    // Example 2: Specific provider - Ollama
    console.log('2. Coding task with Ollama:');
    result = await client.callTool('chat', {
      prompt: 'Write a Python function to calculate fibonacci numbers',
      provider: 'ollama'
    });
    data = JSON.parse(result.content[0].text);
    console.log(`   Model: ${data.model_info.provider} (${data.model_info.model})`);
    console.log(`   Response: ${data.response.substring(0, 100)}...\n`);

    // Example 3: List models
    console.log('3. Available Ollama models:');
    result = await client.callTool('list_models', { provider: 'ollama' });
    data = JSON.parse(result.content[0].text);
    console.log(`   Models: ${data.models.join(', ')}\n`);

  } catch (error) {
    console.error('Examples error:', error);
  } finally {
    await client.disconnect();
  }
}

// Main execution
if (process.argv.includes('--examples')) {
  runExamples();
} else {
  runDemo();
}