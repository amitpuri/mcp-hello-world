// Model providers and their configurations
export const MODEL_PROVIDERS = {
  OLLAMA: 'ollama',
  CLAUDE: 'claude', 
  OPENAI: 'openai'
};

// Available models for each provider
export const AVAILABLE_MODELS = {
  [MODEL_PROVIDERS.OLLAMA]: ['llama3.2', 'llama3.1', 'codellama', 'mistral'],
  [MODEL_PROVIDERS.CLAUDE]: ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307'],
  [MODEL_PROVIDERS.OPENAI]: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
};

// Model routing rules based on task type
export const MODEL_ROUTING = {
  creative: MODEL_PROVIDERS.CLAUDE,
  analytical: MODEL_PROVIDERS.OPENAI,
  coding: MODEL_PROVIDERS.OLLAMA,
  general: MODEL_PROVIDERS.OLLAMA,
  default: MODEL_PROVIDERS.OLLAMA
};

// Task types for automatic model selection
export const TASK_TYPES = {
  CREATIVE: 'creative',
  ANALYTICAL: 'analytical', 
  CODING: 'coding',
  GENERAL: 'general'
};

// Default configurations for each provider
export const DEFAULT_CONFIGS = {
  [MODEL_PROVIDERS.OLLAMA]: {
    baseURL: 'http://localhost:11434',
    model: 'llama3.2',
    maxTokens: 1000,
    temperature: 0.7
  },
  [MODEL_PROVIDERS.CLAUDE]: {
    model: 'claude-3-5-sonnet-20241022',
    maxTokens: 1000,
    temperature: 0.7
  },
  [MODEL_PROVIDERS.OPENAI]: {
    model: 'gpt-4',
    maxTokens: 1000,
    temperature: 0.7
  }
};

// Error types
export const ERROR_TYPES = {
  INVALID_PROVIDER: 'INVALID_PROVIDER',
  MODEL_UNAVAILABLE: 'MODEL_UNAVAILABLE',
  API_ERROR: 'API_ERROR',
  TIMEOUT: 'TIMEOUT',
  INVALID_REQUEST: 'INVALID_REQUEST'
};

// Utility functions
export function getProviderForModel(modelName) {
  for (const [provider, models] of Object.entries(AVAILABLE_MODELS)) {
    if (models.includes(modelName)) {
      return provider;
    }
  }
  return null;
}

export function getDefaultModelForProvider(provider) {
  const models = AVAILABLE_MODELS[provider];
  return models ? models[0] : null;
}

export function validateModelRequest(provider, model) {
  if (!MODEL_PROVIDERS[provider.toUpperCase()]) {
    return { valid: false, error: `Invalid provider: ${provider}` };
  }
  
  const availableModels = AVAILABLE_MODELS[provider];
  if (model && !availableModels.includes(model)) {
    return { valid: false, error: `Model ${model} not available for provider ${provider}` };
  }
  
  return { valid: true };
}