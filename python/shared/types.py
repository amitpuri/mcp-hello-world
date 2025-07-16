"""
Shared types and constants for MCP Hello World project (Python implementation)
"""

from enum import Enum
from typing import Dict

class ModelProvider(str, Enum):
    """Available model providers."""
    CLAUDE = "claude"
    OPENAI = "openai"
    LLAMA = "llama"

class HelloWorldScenario(str, Enum):
    """Available greeting scenarios."""
    SIMPLE = "simple"
    FORMAL = "formal"
    CREATIVE = "creative"
    TECHNICAL = "technical"

# Default routing rules mapping scenarios to models
DEFAULT_ROUTING_RULES: Dict[HelloWorldScenario, ModelProvider] = {
    HelloWorldScenario.SIMPLE: ModelProvider.CLAUDE,
    HelloWorldScenario.FORMAL: ModelProvider.OPENAI,
    HelloWorldScenario.CREATIVE: ModelProvider.CLAUDE,
    HelloWorldScenario.TECHNICAL: ModelProvider.LLAMA,
}

# Greeting message templates for each scenario
GREETING_TEMPLATES: Dict[HelloWorldScenario, str] = {
    HelloWorldScenario.SIMPLE: "Hello, {name}!",
    HelloWorldScenario.FORMAL: "Good day, {name}. It is a pleasure to make your acquaintance.",
    HelloWorldScenario.CREATIVE: "🌟 Greetings and salutations, magnificent {name}! ✨",
    HelloWorldScenario.TECHNICAL: "print(f'Hello, {name}')  # Executed successfully",
}