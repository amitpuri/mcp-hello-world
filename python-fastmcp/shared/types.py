"""
Model providers, routing rules, and Pydantic models for FastMCP implementation.
"""

import os
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, validator

class ModelProvider(str, Enum):
    """Available model providers."""
    OLLAMA = "ollama"
    CLAUDE = "claude"
    OPENAI = "openai"

class TaskType(str, Enum):
    """Task types for automatic model selection."""
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    CODING = "coding"
    GENERAL = "general"

class ErrorType(str, Enum):
    """Error types for API responses."""
    INVALID_PROVIDER = "INVALID_PROVIDER"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    API_ERROR = "API_ERROR"
    TIMEOUT = "TIMEOUT"
    INVALID_REQUEST = "INVALID_REQUEST"

# Available models for each provider
AVAILABLE_MODELS: Dict[ModelProvider, List[str]] = {
    ModelProvider.OLLAMA: ["llama3.2", "llama3.1", "codellama", "mistral"],
    ModelProvider.CLAUDE: ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
    ModelProvider.OPENAI: ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
}

# Model routing rules based on task type
MODEL_ROUTING: Dict[TaskType, ModelProvider] = {
    TaskType.CREATIVE: ModelProvider.CLAUDE,
    TaskType.ANALYTICAL: ModelProvider.OPENAI,
    TaskType.CODING: ModelProvider.OLLAMA,
    TaskType.GENERAL: ModelProvider.OLLAMA
}

class ChatRequest(BaseModel):
    """Pydantic model for chat requests."""
    prompt: str = Field(..., description="The message/prompt to send to the AI model")
    provider: Optional[ModelProvider] = Field(None, description="Model provider (optional - will auto-select)")
    model: Optional[str] = Field(None, description="Specific model name (optional)")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Temperature for response generation")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="Maximum tokens in response")

class ListModelsRequest(BaseModel):
    """Pydantic model for list models requests."""
    provider: ModelProvider = Field(..., description="Model provider")

class ModelInfo(BaseModel):
    """Model information in responses."""
    provider: str
    model: str
    task_type: str
    auto_selected: bool

class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    model_info: ModelInfo
    usage: Usage
    timestamp: str
    implementation: str = "fastmcp"

class ListModelsResponse(BaseModel):
    """List models response model."""
    provider: str
    models: List[str]
    timestamp: str

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    error_type: str
    provider: Optional[str] = None

def get_provider_for_model(model_name: str) -> Optional[ModelProvider]:
    """Get the provider for a specific model name."""
    for provider, models in AVAILABLE_MODELS.items():
        if model_name in models:
            return provider
    return None

def get_default_model_for_provider(provider: ModelProvider) -> Optional[str]:
    """Get the default model for a provider."""
    models = AVAILABLE_MODELS.get(provider)
    return models[0] if models else None

def validate_model_request(provider: str, model: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Validate a model request."""
    try:
        provider_enum = ModelProvider(provider.lower())
    except ValueError:
        return False, f"Invalid provider: {provider}"
    
    if model:
        available_models = AVAILABLE_MODELS[provider_enum]
        if model not in available_models:
            return False, f"Model {model} not available for provider {provider}"
    
    return True, None

def determine_task_type(prompt: str) -> TaskType:
    """Determine task type from prompt content."""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['code', 'program', 'function', 'debug', 'algorithm']):
        return TaskType.CODING
    elif any(word in prompt_lower for word in ['creative', 'story', 'poem', 'imagine', 'write']):
        return TaskType.CREATIVE
    elif any(word in prompt_lower for word in ['analyze', 'compare', 'evaluate', 'assess', 'examine']):
        return TaskType.ANALYTICAL
    else:
        return TaskType.GENERAL

def select_model_for_task(task_type: TaskType, preferred_provider: Optional[str] = None) -> ModelProvider:
    """Select the best model provider for a task type."""
    if preferred_provider:
        try:
            return ModelProvider(preferred_provider.lower())
        except ValueError:
            pass  # Fall back to automatic selection
    
    return MODEL_ROUTING.get(task_type, ModelProvider.OLLAMA)

class Config(BaseModel):
    """Configuration model."""
    server_name: str = "real-models-fastmcp-server"
    server_version: str = "1.0.0"
    enable_model_routing: bool = True
    default_model: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    anthropic_api_key: Optional[str] = None
    claude_model: str = "claude-3-5-sonnet-20241022"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout_seconds: int = 30
    log_level: str = "INFO"
    enable_debug: bool = False

def get_env_config() -> Config:
    """Get configuration from environment variables."""
    return Config(
        server_name=os.getenv("MCP_SERVER_NAME", "real-models-fastmcp-server"),
        server_version=os.getenv("MCP_SERVER_VERSION", "1.0.0"),
        enable_model_routing=os.getenv("ENABLE_MODEL_ROUTING", "true").lower() != "false",
        default_model=os.getenv("DEFAULT_MODEL", "ollama"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        claude_model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4"),
        max_tokens=int(os.getenv("MAX_TOKENS", "1000")),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "30")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        enable_debug=os.getenv("ENABLE_DEBUG", "false").lower() != "false"
    )