"""
Model API clients for Ollama, Claude, and OpenAI with FastMCP integration.
"""

import asyncio
from datetime import datetime
from typing import Dict, Optional, Any

import httpx
from anthropic import Anthropic
from openai import OpenAI

from .types import (
    ModelProvider, 
    ErrorType, 
    Config,
    Usage,
    ErrorResponse,
    get_env_config
)

class ModelClients:
    """Manages API clients for all model providers."""
    
    def __init__(self):
        self.config = get_env_config()
        self.anthropic_client = None
        self.openai_client = None
        self.http_client = httpx.AsyncClient(timeout=self.config.timeout_seconds)
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize API clients based on available credentials."""
        # Initialize Anthropic client
        if self.config.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=self.config.anthropic_api_key)
        
        # Initialize OpenAI client
        if self.config.openai_api_key:
            self.openai_client = OpenAI(api_key=self.config.openai_api_key)
    
    async def call_ollama(self, prompt: str, model: Optional[str] = None, options: Optional[Dict] = None) -> Dict:
        """Call Ollama API."""
        if options is None:
            options = {}
        
        model_name = model or self.config.ollama_model
        base_url = self.config.ollama_base_url
        
        try:
            response = await self.http_client.post(
                f"{base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": options.get("temperature", self.config.temperature),
                        "num_predict": options.get("max_tokens", self.config.max_tokens),
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "content": data["response"],
                "model": model_name,
                "provider": ModelProvider.OLLAMA.value,
                "usage": Usage(
                    prompt_tokens=data.get("prompt_eval_count", 0),
                    completion_tokens=data.get("eval_count", 0),
                    total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                ).dict()
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": "Ollama server not available. Make sure Ollama is running on localhost:11434",
                "error_type": ErrorType.MODEL_UNAVAILABLE.value,
                "provider": ModelProvider.OLLAMA.value
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": ErrorType.API_ERROR.value,
                "provider": ModelProvider.OLLAMA.value
            }
    
    async def call_claude(self, prompt: str, model: Optional[str] = None, options: Optional[Dict] = None) -> Dict:
        """Call Claude API."""
        if not self.anthropic_client:
            return {
                "success": False,
                "error": "Anthropic API key not configured",
                "error_type": ErrorType.INVALID_REQUEST.value,
                "provider": ModelProvider.CLAUDE.value
            }
        
        if options is None:
            options = {}
        
        model_name = model or self.config.claude_model
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.anthropic_client.messages.create(
                    model=model_name,
                    max_tokens=options.get("max_tokens", self.config.max_tokens),
                    temperature=options.get("temperature", self.config.temperature),
                    messages=[{"role": "user", "content": prompt}]
                )
            )
            
            return {
                "success": True,
                "content": response.content[0].text,
                "model": model_name,
                "provider": ModelProvider.CLAUDE.value,
                "usage": Usage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens
                ).dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": ErrorType.API_ERROR.value,
                "provider": ModelProvider.CLAUDE.value
            }
    
    async def call_openai(self, prompt: str, model: Optional[str] = None, options: Optional[Dict] = None) -> Dict:
        """Call OpenAI API."""
        if not self.openai_client:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "error_type": ErrorType.INVALID_REQUEST.value,
                "provider": ModelProvider.OPENAI.value
            }
        
        if options is None:
            options = {}
        
        model_name = model or self.config.openai_model
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.openai_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=options.get("max_tokens", self.config.max_tokens),
                    temperature=options.get("temperature", self.config.temperature)
                )
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model_name,
                "provider": ModelProvider.OPENAI.value,
                "usage": Usage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens
                ).dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": ErrorType.API_ERROR.value,
                "provider": ModelProvider.OPENAI.value
            }
    
    async def call_model(self, provider: str, prompt: str, model: Optional[str] = None, options: Optional[Dict] = None) -> Dict:
        """Call any model provider."""
        try:
            provider_enum = ModelProvider(provider.lower())
        except ValueError:
            return {
                "success": False,
                "error": f"Unknown provider: {provider}",
                "error_type": ErrorType.INVALID_PROVIDER.value
            }
        
        if provider_enum == ModelProvider.OLLAMA:
            return await self.call_ollama(prompt, model, options)
        elif provider_enum == ModelProvider.CLAUDE:
            return await self.call_claude(prompt, model, options)
        elif provider_enum == ModelProvider.OPENAI:
            return await self.call_openai(prompt, model, options)
        else:
            return {
                "success": False,
                "error": f"Provider {provider} not implemented",
                "error_type": ErrorType.INVALID_PROVIDER.value
            }
    
    async def get_available_models(self, provider: str) -> Dict:
        """Get available models for a provider."""
        try:
            provider_enum = ModelProvider(provider.lower())
        except ValueError:
            return {
                "success": False,
                "error": f"Unknown provider: {provider}"
            }
        
        if provider_enum == ModelProvider.OLLAMA:
            try:
                base_url = self.config.ollama_base_url
                response = await self.http_client.get(f"{base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                
                return {
                    "success": True,
                    "models": [model["name"] for model in data["models"]],
                    "provider": ModelProvider.OLLAMA.value
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "provider": ModelProvider.OLLAMA.value
                }
        elif provider_enum == ModelProvider.CLAUDE:
            return {
                "success": True,
                "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
                "provider": ModelProvider.CLAUDE.value
            }
        elif provider_enum == ModelProvider.OPENAI:
            return {
                "success": True,
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "provider": ModelProvider.OPENAI.value
            }
        else:
            return {
                "success": False,
                "error": f"Provider {provider} not implemented"
            }
    
    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()

# Global instance
_model_clients = None

def get_model_clients() -> ModelClients:
    """Get or create the global model clients instance."""
    global _model_clients
    if _model_clients is None:
        _model_clients = ModelClients()
    return _model_clients