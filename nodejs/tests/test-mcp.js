#!/usr/bin/env node

import { spawn } from 'child_process';
import { HELLO_WORLD_SCENARIOS } from '../shared/types.js';

function testMCP(request) {
  return new Promise((resolve, reject) => {
    const server = spawn('node', ['server/server.js'], {
      cwd: process.cwd(),
      stdio: ['pipe', 'pipe', 'inherit']
    });

    let output = '';
    
    server.stdout.on('data', (data) => {
      output += data.toString();
    });

    server.on('close', () => {
      try {
        // Parse the JSON response
        resolve(JSON.parse(output.trim()));
      } catch (error) {
        reject(error);
      }
    });

    server.on('error', (error) => {
      reject(error);
    });

    server.stdin.write(JSON.stringify(request) + '\n');
    server.stdin.end();
  });
}

async function demo() {
  console.log('🧪 MCP Hello World Test Suite\n');

  try {
    // Test 1: List available tools
    console.log('1. Testing tools/list...');
    const toolsResponse = await testMCP({
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/list'
    });
    console.log('✅ Available tools:', toolsResponse.result.tools[0].name);
    console.log('   Description:', toolsResponse.result.tools[0].description);
    console.log('');

    // Test 2: Test different greeting styles
    const testCases = [
      { name: 'Alice', style: HELLO_WORLD_SCENARIOS.SIMPLE, expectedModel: 'claude' },
      { name: 'Bob', style: HELLO_WORLD_SCENARIOS.FORMAL, expectedModel: 'openai' },
      { name: 'Charlie', style: HELLO_WORLD_SCENARIOS.CREATIVE, expectedModel: 'claude' },
      { name: 'Dave', style: HELLO_WORLD_SCENARIOS.TECHNICAL, expectedModel: 'llama' }
    ];

    for (let i = 0; i < testCases.length; i++) {
      const testCase = testCases[i];
      console.log(`${i + 2}. Testing ${testCase.style} style with ${testCase.name}...`);
      
      const response = await testMCP({
        jsonrpc: '2.0',
        id: i + 2,
        method: 'tools/call',
        params: {
          name: 'hello',
          arguments: {
            name: testCase.name,
            style: testCase.style
          }
        }
      });
      
      const result = JSON.parse(response.result.content[0].text);
      console.log(`✅ Model: ${result.model_used} (expected: ${testCase.expectedModel})`);
      console.log(`   Message: ${result.message}`);
      console.log(`   Routing Applied: ${result.routing_applied}`);
      console.log('');
    }

    // Test 3: Test manual model override
    console.log('6. Testing manual model override...');
    const overrideResponse = await testMCP({
      jsonrpc: '2.0',
      id: 6,
      method: 'tools/call',
      params: {
        name: 'hello',
        arguments: {
          name: 'Eve',
          style: HELLO_WORLD_SCENARIOS.SIMPLE,
          model: 'llama'
        }
      }
    });
    
    const overrideResult = JSON.parse(overrideResponse.result.content[0].text);
    console.log(`✅ Model: ${overrideResult.model_used} (manually specified)`);
    console.log(`   Message: ${overrideResult.message}`);
    console.log(`   Routing Applied: ${overrideResult.routing_applied}`);
    console.log('');

    console.log('🎉 All tests completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

demo().catch(console.error);