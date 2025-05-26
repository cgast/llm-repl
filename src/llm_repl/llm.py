"""
LLM provider interfaces for LLM-REPL.

This module provides a unified interface for interacting with different
LLM providers (OpenAI, Anthropic, etc.) and manages the API keys and
configuration.
"""

import os
from abc import ABC, abstractmethod
import json
from typing import Any, Dict, List, Optional, Union
import yaml

# Default configuration path
CONFIG_PATH = os.path.expanduser("~/.llm-repl/config.yaml")


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def generate(self, 
                 prompt: str, 
                 model: str, 
                 temperature: float = 0.7, 
                 max_tokens: Optional[int] = None) -> str:
        """Generate a response from the LLM.
        
        Args:
            prompt: The input prompt
            model: The model to use
            temperature: The sampling temperature
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated text response
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get a list of available models from this provider.
        
        Returns:
            List of model identifiers
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (if None, tries to get from environment)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY "
                "environment variable or provide it in the configuration."
            )
        
        # Import openai here to avoid making it a hard dependency
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "OpenAI package not found. Please install it with: "
                "pip install openai"
            )
    
    def generate(self, 
                 prompt: str, 
                 model: str = "gpt-4", 
                 temperature: float = 0.7,
                 max_tokens: Optional[int] = None) -> str:
        """Generate a response using OpenAI's API.
        
        Args:
            prompt: The input prompt
            model: The model to use
            temperature: The sampling temperature
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response from OpenAI: {e}")
            return f"Error: {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models.
        
        Returns:
            List of model identifiers
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"Error fetching OpenAI models: {e}")
            return ["gpt-4", "gpt-3.5-turbo"]  # Fallback to common models


class MockProvider(LLMProvider):
    """Mock provider for testing without API calls."""
    
    def generate(self, 
                 prompt: str, 
                 model: str = "mock", 
                 temperature: float = 0.7,
                 max_tokens: Optional[int] = None) -> str:
        """Generate a mock response.
        
        Args:
            prompt: The input prompt
            model: Ignored in mock provider
            temperature: Ignored in mock provider
            max_tokens: Ignored in mock provider
            
        Returns:
            A simple mock response
        """
        return f"Mock response to: {prompt[:50]}..."
    
    def get_available_models(self) -> List[str]:
        """Get mock models.
        
        Returns:
            List with a single mock model
        """
        return ["mock"]


# Global provider instance
_provider = None


def get_llm_provider() -> LLMProvider:
    """Get the configured LLM provider.
    
    Returns:
        An instance of the configured LLM provider
    """
    global _provider
    
    if _provider is None:
        # Initialize the provider from config
        try:
            provider_config = _load_config().get("provider", {})
            provider_type = provider_config.get("type", "mock")
            
            if provider_type == "openai":
                api_key = provider_config.get("api_key")
                _provider = OpenAIProvider(api_key)
            else:
                # Default to mock provider if not configured
                _provider = MockProvider()
                
        except Exception as e:
            print(f"Error initializing LLM provider: {e}")
            print("Falling back to mock provider")
            _provider = MockProvider()
    
    return _provider


def _load_config() -> Dict[str, Any]:
    """Load configuration from file.
    
    Returns:
        Configuration dictionary
    """
    if not os.path.exists(CONFIG_PATH):
        # Create default config
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        default_config = {
            "provider": {
                "type": "mock",
                # "type": "openai",
                # "api_key": "your-api-key-here"
            }
        }
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False)
        return default_config
    
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def set_provider(provider_type: str, **kwargs) -> None:
    """Set the LLM provider.
    
    Args:
        provider_type: The type of provider ("openai", "mock", etc.)
        **kwargs: Provider-specific configuration
    """
    global _provider
    
    if provider_type == "openai":
        _provider = OpenAIProvider(**kwargs)
    elif provider_type == "mock":
        _provider = MockProvider()
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    # Update the configuration
    config = _load_config()
    config["provider"] = {"type": provider_type, **kwargs}
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
