#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import dotenv from 'dotenv';
import { 
  MODEL_PROVIDERS, 
  MODEL_ROUTING, 
  TASK_TYPES,
  validateModelRequest 
} from '../shared/types.js';
import { initializeClients, callModel, getAvailableModels } from '../shared/models.js';

// Load environment variables
dotenv.config();

// Initialize model clients
initializeClients();

// Create MCP server
const server = new Server(
  {
    name: process.env.MCP_SERVER_NAME || 'real-models-server',
    version: process.env.MCP_SERVER_VERSION || '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Helper function to determine task type from prompt
function determineTaskType(prompt) {
  const lowerPrompt = prompt.toLowerCase();
  
  if (lowerPrompt.includes('code') || lowerPrompt.includes('program') || lowerPrompt.includes('function')) {
    return TASK_TYPES.CODING;
  }
  if (lowerPrompt.includes('creative') || lowerPrompt.includes('story') || lowerPrompt.includes('poem')) {
    return TASK_TYPES.CREATIVE;
  }
  if (lowerPrompt.includes('analyze') || lowerPrompt.includes('compare') || lowerPrompt.includes('evaluate')) {
    return TASK_TYPES.ANALYTICAL;
  }
  
  return TASK_TYPES.GENERAL;
}

// Helper function to select model based on task type
function selectModelForTask(taskType, preferredProvider = null) {
  if (preferredProvider && MODEL_PROVIDERS[preferredProvider.toUpperCase()]) {
    return preferredProvider.toLowerCase();
  }
  
  return MODEL_ROUTING[taskType] || MODEL_ROUTING.default;
}

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'chat',
        description: 'Chat with AI models (Ollama, Claude, or GPT-4) with automatic or manual model selection',
        inputSchema: {
          type: 'object',
          properties: {
            prompt: {
              type: 'string',
              description: 'The message/prompt to send to the AI model',
            },
            provider: {
              type: 'string',
              description: 'Model provider: ollama, claude, or openai (optional - will auto-select based on task)',
              enum: ['ollama', 'claude', 'openai']
            },
            model: {
              type: 'string',
              description: 'Specific model name (optional - will use provider default)',
            },
            temperature: {
              type: 'number',
              description: 'Temperature for response generation (0.0-1.0, default: 0.7)',
              minimum: 0,
              maximum: 1
            },
            maxTokens: {
              type: 'number',
              description: 'Maximum tokens in response (default: 1000)',
              minimum: 1,
              maximum: 4000
            }
          },
          required: ['prompt'],
        },
      },
      {
        name: 'list_models',
        description: 'List available models for a specific provider',
        inputSchema: {
          type: 'object',
          properties: {
            provider: {
              type: 'string',
              description: 'Model provider: ollama, claude, or openai',
              enum: ['ollama', 'claude', 'openai']
            }
          },
          required: ['provider'],
        },
      }
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'chat': {
        const { prompt, provider, model, temperature, maxTokens } = args;
        
        if (!prompt) {
          throw new Error('Prompt is required');
        }

        // Determine task type and select appropriate provider
        const taskType = determineTaskType(prompt);
        const selectedProvider = provider || selectModelForTask(taskType);
        
        // Validate the request
        const validation = validateModelRequest(selectedProvider, model);
        if (!validation.valid) {
          throw new Error(validation.error);
        }

        // Prepare options
        const options = {};
        if (temperature !== undefined) options.temperature = temperature;
        if (maxTokens !== undefined) options.maxTokens = maxTokens;

        // Call the model
        const result = await callModel(selectedProvider, prompt, model, options);
        
        if (!result.success) {
          throw new Error(`${result.provider} API error: ${result.error}`);
        }

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                response: result.content,
                model_info: {
                  provider: result.provider,
                  model: result.model,
                  task_type: taskType,
                  auto_selected: !provider
                },
                usage: result.usage,
                timestamp: new Date().toISOString()
              }, null, 2)
            }
          ],
        };
      }

      case 'list_models': {
        const { provider } = args;
        
        if (!provider) {
          throw new Error('Provider is required');
        }

        const result = await getAvailableModels(provider);
        
        if (!result.success) {
          throw new Error(`Failed to get models for ${provider}: ${result.error}`);
        }

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                provider: result.provider,
                models: result.models,
                timestamp: new Date().toISOString()
              }, null, 2)
            }
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    // Log error to stderr for debugging
    console.error(`Error in tool ${name}:`, error.message);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error.message,
            tool: name,
            timestamp: new Date().toISOString()
          }, null, 2)
        }
      ],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  // Log server start to stderr (won't interfere with MCP communication)
  console.error(`Real Models MCP Server started - ${new Date().toISOString()}`);
  console.error(`Configured providers: ${Object.values(MODEL_PROVIDERS).join(', ')}`);
}

// Handle process termination gracefully
process.on('SIGINT', async () => {
  console.error('Shutting down server...');
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.error('Shutting down server...');
  process.exit(0);
});

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});