import { Anthropic } from '@anthropic-ai/sdk';
import OpenAI from 'openai';
import axios from 'axios';
import { MODEL_PROVIDERS, DEFAULT_CONFIGS, ERROR_TYPES } from './types.js';

// Model client instances
let anthropicClient = null;
let openaiClient = null;

// Initialize model clients
export function initializeClients() {
  // Initialize Anthropic client
  if (process.env.ANTHROPIC_API_KEY) {
    anthropicClient = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
  }

  // Initialize OpenAI client  
  if (process.env.OPENAI_API_KEY) {
    openaiClient = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  }
}

// Ollama API call
async function callOllama(prompt, model = null, options = {}) {
  const baseURL = process.env.OLLAMA_BASE_URL || DEFAULT_CONFIGS.ollama.baseURL;
  const modelName = model || process.env.OLLAMA_MODEL || DEFAULT_CONFIGS.ollama.model;
  
  try {
    const response = await axios.post(`${baseURL}/api/generate`, {
      model: modelName,
      prompt: prompt,
      stream: false,
      options: {
        temperature: options.temperature || DEFAULT_CONFIGS.ollama.temperature,
        num_predict: options.maxTokens || DEFAULT_CONFIGS.ollama.maxTokens,
      }
    }, {
      timeout: parseInt(process.env.TIMEOUT_MS) || 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    return {
      success: true,
      content: response.data.response,
      model: modelName,
      provider: MODEL_PROVIDERS.OLLAMA,
      usage: {
        prompt_tokens: response.data.prompt_eval_count || 0,
        completion_tokens: response.data.eval_count || 0,
        total_tokens: (response.data.prompt_eval_count || 0) + (response.data.eval_count || 0)
      }
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      errorType: error.code === 'ECONNREFUSED' ? ERROR_TYPES.MODEL_UNAVAILABLE : ERROR_TYPES.API_ERROR,
      provider: MODEL_PROVIDERS.OLLAMA
    };
  }
}

// Claude API call
async function callClaude(prompt, model = null, options = {}) {
  if (!anthropicClient) {
    return {
      success: false,
      error: 'Anthropic API key not configured',
      errorType: ERROR_TYPES.INVALID_REQUEST,
      provider: MODEL_PROVIDERS.CLAUDE
    };
  }

  const modelName = model || process.env.CLAUDE_MODEL || DEFAULT_CONFIGS.claude.model;
  
  try {
    const response = await anthropicClient.messages.create({
      model: modelName,
      max_tokens: options.maxTokens || DEFAULT_CONFIGS.claude.maxTokens,
      temperature: options.temperature || DEFAULT_CONFIGS.claude.temperature,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    });

    return {
      success: true,
      content: response.content[0].text,
      model: modelName,
      provider: MODEL_PROVIDERS.CLAUDE,
      usage: {
        prompt_tokens: response.usage.input_tokens,
        completion_tokens: response.usage.output_tokens,
        total_tokens: response.usage.input_tokens + response.usage.output_tokens
      }
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      errorType: ERROR_TYPES.API_ERROR,
      provider: MODEL_PROVIDERS.CLAUDE
    };
  }
}

// OpenAI API call
async function callOpenAI(prompt, model = null, options = {}) {
  if (!openaiClient) {
    return {
      success: false,
      error: 'OpenAI API key not configured',
      errorType: ERROR_TYPES.INVALID_REQUEST,
      provider: MODEL_PROVIDERS.OPENAI
    };
  }

  const modelName = model || process.env.OPENAI_MODEL || DEFAULT_CONFIGS.openai.model;
  
  try {
    const response = await openaiClient.chat.completions.create({
      model: modelName,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ],
      max_tokens: options.maxTokens || DEFAULT_CONFIGS.openai.maxTokens,
      temperature: options.temperature || DEFAULT_CONFIGS.openai.temperature,
    });

    return {
      success: true,
      content: response.choices[0].message.content,
      model: modelName,
      provider: MODEL_PROVIDERS.OPENAI,
      usage: {
        prompt_tokens: response.usage.prompt_tokens,
        completion_tokens: response.usage.completion_tokens,
        total_tokens: response.usage.total_tokens
      }
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      errorType: ERROR_TYPES.API_ERROR,
      provider: MODEL_PROVIDERS.OPENAI
    };
  }
}

// Main function to call any model
export async function callModel(provider, prompt, model = null, options = {}) {
  switch (provider.toLowerCase()) {
    case MODEL_PROVIDERS.OLLAMA:
      return await callOllama(prompt, model, options);
    case MODEL_PROVIDERS.CLAUDE:
      return await callClaude(prompt, model, options);
    case MODEL_PROVIDERS.OPENAI:
      return await callOpenAI(prompt, model, options);
    default:
      return {
        success: false,
        error: `Unknown provider: ${provider}`,
        errorType: ERROR_TYPES.INVALID_PROVIDER
      };
  }
}

// Get available models for a provider
export async function getAvailableModels(provider) {
  switch (provider.toLowerCase()) {
    case MODEL_PROVIDERS.OLLAMA:
      try {
        const baseURL = process.env.OLLAMA_BASE_URL || DEFAULT_CONFIGS.ollama.baseURL;
        const response = await axios.get(`${baseURL}/api/tags`);
        return {
          success: true,
          models: response.data.models.map(m => m.name),
          provider: MODEL_PROVIDERS.OLLAMA
        };
      } catch (error) {
        return {
          success: false,
          error: error.message,
          provider: MODEL_PROVIDERS.OLLAMA
        };
      }
    case MODEL_PROVIDERS.CLAUDE:
      return {
        success: true,
        models: ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307'],
        provider: MODEL_PROVIDERS.CLAUDE
      };
    case MODEL_PROVIDERS.OPENAI:
      return {
        success: true,
        models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        provider: MODEL_PROVIDERS.OPENAI
      };
    default:
      return {
        success: false,
        error: `Unknown provider: ${provider}`
      };
  }
}