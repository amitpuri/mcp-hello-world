#!/usr/bin/env node

import { spawn } from 'child_process';
import { HELLO_WORLD_SCENARIOS } from '../shared/types.js';

class HelloWorldClient {
  constructor() {
    this.requestId = 1;
  }

  async connect() {
    // Spawn the server process
    this.serverProcess = spawn('node', ['server/server.js'], {
      cwd: process.cwd(),
      stdio: ['pipe', 'pipe', 'pipe']
    });

    this.serverProcess.stderr.on('data', (data) => {
      console.log('Server:', data.toString().trim());
    });

    this.serverProcess.on('error', (error) => {
      console.error('Server error:', error);
    });

    console.log('✅ Connected to Hello World MCP Server');
    return this.serverProcess;
  }

  async sendRequest(method, params = {}) {
    return new Promise((resolve, reject) => {
      const request = {
        jsonrpc: '2.0',
        id: this.requestId++,
        method,
        params
      };

      let response = '';
      
      const onData = (data) => {
        response += data.toString();
        try {
          const parsed = JSON.parse(response);
          this.serverProcess.stdout.off('data', onData);
          resolve(parsed);
        } catch (e) {
          // Continue collecting data
        }
      };

      this.serverProcess.stdout.on('data', onData);
      this.serverProcess.stdin.write(JSON.stringify(request) + '\n');
    });
  }

  async listTools() {
    const response = await this.sendRequest('tools/list');
    return response.result.tools;
  }

  async callHelloTool(name, style, model) {
    const args = { name };
    if (style) args.style = style;
    if (model) args.model = model;

    const response = await this.sendRequest('tools/call', {
      name: 'hello',
      arguments: args
    });

    return JSON.parse(response.result.content[0].text);
  }

  async runDemo() {
    console.log('🚀 Hello World MCP Client Demo\n');

    try {
      await this.connect();

      // List available tools
      console.log('📋 Available Tools:');
      const tools = await this.listTools();
      tools.forEach(tool => {
        console.log(`  • ${tool.name}: ${tool.description}`);
      });
      console.log('');

      // Test different scenarios
      const testCases = [
        { name: 'Alice', style: HELLO_WORLD_SCENARIOS.SIMPLE },
        { name: 'Bob', style: HELLO_WORLD_SCENARIOS.FORMAL },
        { name: 'Charlie', style: HELLO_WORLD_SCENARIOS.CREATIVE },
        { name: 'Dave', style: HELLO_WORLD_SCENARIOS.TECHNICAL },
        { name: 'Eve', style: HELLO_WORLD_SCENARIOS.SIMPLE, model: 'llama' }
      ];

      console.log('🎭 Testing Different Greeting Styles:');
      for (const testCase of testCases) {
        const result = await this.callHelloTool(testCase.name, testCase.style, testCase.model);
        
        console.log(`\n  👤 Name: ${testCase.name}`);
        console.log(`  🎨 Style: ${testCase.style}`);
        if (testCase.model) console.log(`  🤖 Requested Model: ${testCase.model}`);
        console.log(`  🔀 Model Used: ${result.model_used}`);
        console.log(`  💬 Message: ${result.message}`);
        console.log(`  ⏰ Time: ${result.timestamp}`);
        console.log(`  🎯 Routing Applied: ${result.routing_applied ? 'Yes' : 'No'}`);
      }

      console.log('\n✅ Demo completed successfully!');
      
      // Clean up
      this.serverProcess.kill();

    } catch (error) {
      console.error('❌ Demo failed:', error.message);
      if (this.serverProcess) {
        this.serverProcess.kill();
      }
      process.exit(1);
    }
  }
}

// Run the demo if this file is executed directly
import { fileURLToPath } from 'url';
import { resolve } from 'path';

const currentFile = fileURLToPath(import.meta.url);
const executedFile = resolve(process.argv[1]);

if (currentFile === executedFile) {
  const client = new HelloWorldClient();
  client.runDemo().catch(console.error);
}

export { HelloWorldClient };