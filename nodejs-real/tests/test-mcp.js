#!/usr/bin/env node

import { spawn } from 'child_process';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class MCPTester {
  constructor() {
    this.requestId = 1;
    this.serverProcess = null;
    this.isConnected = false;
    this.testResults = [];
  }

  async connect() {
    return new Promise((resolve, reject) => {
      const serverPath = path.join(__dirname, '..', 'server', 'server.js');
      this.serverProcess = spawn('node', [serverPath], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.serverProcess.on('error', (error) => {
        reject(error);
      });

      this.serverProcess.stderr.on('data', (data) => {
        // Suppress server logs during testing
      });

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
        responseData = lines[lines.length - 1];
      };

      this.serverProcess.stdout.on('data', onData);
      this.serverProcess.stdin.write(JSON.stringify(request) + '\n');

      setTimeout(() => {
        this.serverProcess.stdout.removeListener('data', onData);
        reject(new Error('Request timeout'));
      }, 30000);
    });
  }

  async runTest(name, testFn) {
    console.log(`${this.testResults.length + 1}. ${name}...`);
    try {
      const startTime = Date.now();
      await testFn();
      const duration = Date.now() - startTime;
      console.log(`✅ PASSED (${duration}ms)`);
      this.testResults.push({ name, status: 'PASSED', duration });
    } catch (error) {
      console.log(`❌ FAILED: ${error.message}`);
      this.testResults.push({ name, status: 'FAILED', error: error.message });
    }
    console.log();
  }

  async disconnect() {
    if (this.serverProcess) {
      this.serverProcess.kill();
      this.isConnected = false;
    }
  }

  printSummary() {
    console.log('📊 Test Summary');
    console.log('================');
    
    const passed = this.testResults.filter(r => r.status === 'PASSED').length;
    const failed = this.testResults.filter(r => r.status === 'FAILED').length;
    
    console.log(`Total tests: ${this.testResults.length}`);
    console.log(`Passed: ${passed}`);
    console.log(`Failed: ${failed}`);
    
    if (failed > 0) {
      console.log('\nFailed tests:');
      this.testResults
        .filter(r => r.status === 'FAILED')
        .forEach(r => console.log(`  • ${r.name}: ${r.error}`));
    }
    
    console.log(`\n${failed === 0 ? '🎉' : '⚠️'} ${failed === 0 ? 'All tests passed!' : 'Some tests failed'}`);
  }
}

async function runTests() {
  console.log('🧪 Real Models MCP Test Suite');
  console.log('==============================\n');

  const tester = new MCPTester();
  
  try {
    console.log('Connecting to MCP server...');
    await tester.connect();
    console.log('✅ Connected!\n');

    // Test 1: List tools
    await tester.runTest('List available tools', async () => {
      const result = await tester.sendRequest('tools/list');
      if (!result.tools || !Array.isArray(result.tools)) {
        throw new Error('Expected tools array');
      }
      
      const toolNames = result.tools.map(t => t.name);
      if (!toolNames.includes('chat')) {
        throw new Error('Expected chat tool');
      }
      if (!toolNames.includes('list_models')) {
        throw new Error('Expected list_models tool');
      }
      
      console.log(`   Found tools: ${toolNames.join(', ')}`);
    });

    // Test 2: Chat with auto-selection
    await tester.runTest('Chat with auto model selection', async () => {
      const result = await tester.sendRequest('tools/call', {
        name: 'chat',
        arguments: {
          prompt: 'Say hello in exactly 5 words'
        }
      });
      
      const data = JSON.parse(result.content[0].text);
      if (!data.response) {
        throw new Error('Expected response field');
      }
      if (!data.model_info) {
        throw new Error('Expected model_info field');
      }
      
      console.log(`   Provider: ${data.model_info.provider}`);
      console.log(`   Model: ${data.model_info.model}`);
      console.log(`   Response: ${data.response.substring(0, 50)}...`);
    });

    // Test 3: Specific provider - Ollama (if available)
    await tester.runTest('Chat with Ollama provider', async () => {
      const result = await tester.sendRequest('tools/call', {
        name: 'chat',
        arguments: {
          prompt: 'What is 2+2?',
          provider: 'ollama'
        }
      });
      
      const data = JSON.parse(result.content[0].text);
      
      // Check if it's an error due to Ollama not being available
      if (data.error && data.error.includes('ECONNREFUSED')) {
        console.log('   ⚠️ Ollama not available (expected if not running locally)');
        return;
      }
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      if (data.model_info.provider !== 'ollama') {
        throw new Error(`Expected ollama provider, got ${data.model_info.provider}`);
      }
      
      console.log(`   Model: ${data.model_info.model}`);
      console.log(`   Response: ${data.response.substring(0, 50)}...`);
    });

    // Test 4: List models for a provider
    await tester.runTest('List models for OpenAI', async () => {
      const result = await tester.sendRequest('tools/call', {
        name: 'list_models',
        arguments: {
          provider: 'openai'
        }
      });
      
      const data = JSON.parse(result.content[0].text);
      if (!data.models || !Array.isArray(data.models)) {
        throw new Error('Expected models array');
      }
      
      console.log(`   Models: ${data.models.join(', ')}`);
    });

    // Test 5: Error handling - invalid provider
    await tester.runTest('Error handling - invalid provider', async () => {
      const result = await tester.sendRequest('tools/call', {
        name: 'chat',
        arguments: {
          prompt: 'Hello',
          provider: 'invalid_provider'
        }
      });
      
      const data = JSON.parse(result.content[0].text);
      if (!data.error) {
        throw new Error('Expected error for invalid provider');
      }
      
      console.log(`   Error handled: ${data.error.substring(0, 50)}...`);
    });

    // Test 6: Temperature and maxTokens parameters
    await tester.runTest('Custom parameters (temperature, maxTokens)', async () => {
      const result = await tester.sendRequest('tools/call', {
        name: 'chat',
        arguments: {
          prompt: 'Count from 1 to 3',
          temperature: 0.1,
          maxTokens: 50
        }
      });
      
      const data = JSON.parse(result.content[0].text);
      if (data.error) {
        // If there's an API error (like missing keys), that's expected
        if (data.error.includes('API key') || data.error.includes('ECONNREFUSED')) {
          console.log(`   ⚠️ API not available: ${data.error.substring(0, 50)}...`);
          return;
        }
        throw new Error(data.error);
      }
      
      console.log(`   Response: ${data.response.substring(0, 50)}...`);
      console.log(`   Tokens used: ${data.usage.total_tokens}`);
    });

    // Test 7: Task type detection
    await tester.runTest('Task type detection', async () => {
      const result = await tester.sendRequest('tools/call', {
        name: 'chat',
        arguments: {
          prompt: 'Write a creative story about a magical forest'
        }
      });
      
      const data = JSON.parse(result.content[0].text);
      if (data.error) {
        // If there's an API error, check if it's expected
        if (data.error.includes('API key') || data.error.includes('ECONNREFUSED')) {
          console.log(`   ⚠️ API not available: ${data.error.substring(0, 50)}...`);
          return;
        }
        throw new Error(data.error);
      }
      
      if (data.model_info.task_type !== 'creative') {
        throw new Error(`Expected creative task type, got ${data.model_info.task_type}`);
      }
      
      console.log(`   Task type: ${data.model_info.task_type}`);
      console.log(`   Auto-selected: ${data.model_info.auto_selected}`);
    });

  } catch (error) {
    console.error('Test suite error:', error);
  } finally {
    await tester.disconnect();
    console.log();
    tester.printSummary();
  }
}

// Run the tests
runTests();