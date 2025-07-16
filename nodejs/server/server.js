#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { 
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { HELLO_WORLD_SCENARIOS, DEFAULT_ROUTING_RULES } from '../shared/types.js';
import { config } from 'dotenv';

// Load environment variables
config();

class HelloWorldServer {
  constructor() {
    this.config = {
      name: process.env.MCP_SERVER_NAME || 'hello-world-server',
      version: process.env.MCP_SERVER_VERSION || '1.0.0',
      defaultModel: process.env.DEFAULT_MODEL || 'claude',
      enableModelRouting: process.env.ENABLE_MODEL_ROUTING !== 'false',
      maxNameLength: parseInt(process.env.MAX_NAME_LENGTH) || 50,
      enableEmoji: process.env.ENABLE_EMOJI !== 'false',
      defaultStyle: process.env.DEFAULT_GREETING_STYLE || 'simple'
    };

    this.server = new Server(
      {
        name: this.config.name,
        version: this.config.version,
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'hello',
            description: 'Generate a hello world message with different styles and model routing',
            inputSchema: {
              type: 'object',
              properties: {
                name: {
                  type: 'string',
                  description: 'Name to greet',
                  default: 'World'
                },
                style: {
                  type: 'string',
                  enum: Object.values(HELLO_WORLD_SCENARIOS),
                  description: 'Style of greeting',
                  default: 'simple'
                },
                model: {
                  type: 'string',
                  description: 'Specific model to use (optional)',
                }
              },
              required: ['name']
            }
          }
        ]
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      if (name === 'hello') {
        return await this.handleHelloTool(args);
      }

      throw new Error(`Unknown tool: ${name}`);
    });
  }

  async handleHelloTool(args) {
    const { name = 'World', style = 'simple', model } = args;
    
    // Determine which model to use
    const selectedModel = model || DEFAULT_ROUTING_RULES[style] || 'claude';
    
    // Generate message based on style
    const message = this.generateMessage(name, style);
    
    const result = {
      message,
      style,
      model_used: selectedModel,
      timestamp: new Date().toISOString(),
      routing_applied: !model // true if we used routing rules
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }

  generateMessage(name, style) {
    switch (style) {
      case HELLO_WORLD_SCENARIOS.SIMPLE:
        return `Hello, ${name}!`;
      
      case HELLO_WORLD_SCENARIOS.FORMAL:
        return `Good day, ${name}. It is a pleasure to make your acquaintance.`;
      
      case HELLO_WORLD_SCENARIOS.CREATIVE:
        return `🌟 Greetings and salutations, magnificent ${name}! ✨`;
      
      case HELLO_WORLD_SCENARIOS.TECHNICAL:
        return `console.log('Hello, ${name}'); // Executed successfully`;
      
      default:
        return `Hello, ${name}!`;
    }
  }

  setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error('[MCP Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Hello World MCP server running on stdio');
  }
}

const server = new HelloWorldServer();
server.run().catch(console.error);