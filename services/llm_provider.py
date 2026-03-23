"""
LLM Provider Abstraction for AI Customer Service System
Supports multiple LLM providers (OpenAI, Claude, Zhipu, etc.)
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from openai import OpenAI
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate chat completion
        :param messages: List of message dictionaries with 'role' and 'content'
        :param kwargs: Additional parameters for the specific provider
        :return: Generated response string
        """
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)
        logger.info("OpenAIProvider initialized successfully")

    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate chat completion using OpenAI
        :param messages: List of message dictionaries with 'role' and 'content'
        :param kwargs: Additional parameters (e.g., model, temperature)
        :return: Generated response string
        """
        try:
            model = kwargs.get("model", "gpt-3.5-turbo")
            temperature = kwargs.get("temperature", 0.7)

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                **{k: v for k, v in kwargs.items() if k not in ["model", "temperature"]}
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise

class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider implementation"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError("Claude API key is required")

        # Import here to avoid dependency if not used
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            logger.info("ClaudeProvider initialized successfully")
        except ImportError:
            logger.error("anthropic package not installed. Please install it with: pip install anthropic")
            raise

    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate chat completion using Claude
        :param messages: List of message dictionaries with 'role' and 'content'
        :param kwargs: Additional parameters (e.g., model, temperature)
        :return: Generated response string
        """
        try:
            model = kwargs.get("model", "claude-3-haiku-20240307")
            temperature = kwargs.get("temperature", 0.7)

            # Convert messages to Claude format
            # Claude expects alternating human/assistant messages
            claude_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    claude_messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    claude_messages.append({"role": "assistant", "content": msg["content"]})
                elif msg["role"] == "system":
                    # Handle system message by adding to the first human message
                    if claude_messages and claude_messages[0]["role"] == "user":
                        claude_messages[0]["content"] = f"{msg['content']}\n\n{claude_messages[0]['content']}"
                    else:
                        claude_messages.insert(0, {"role": "user", "content": msg["content"]})

            response = self.client.messages.create(
                model=model,
                max_tokens=kwargs.get("max_tokens", 1024),
                temperature=temperature,
                messages=claude_messages,
                **{k: v for k, v in kwargs.items() if k not in ["model", "temperature", "max_tokens"]}
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise

class ZhipuProvider(LLMProvider):
    """Zhipu AI provider implementation (GLM models)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError("Zhipu API key is required")

        # Import here to avoid dependency if not used
        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=self.api_key)
            logger.info("ZhipuProvider initialized successfully")
        except ImportError:
            logger.error("zhipuai package not installed. Please install it with: pip install zhipuai")
            raise

    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate chat completion using Zhipu AI
        :param messages: List of message dictionaries with 'role' and 'content'
        :param kwargs: Additional parameters (e.g., model, temperature)
        :return: Generated response string
        """
        try:
            model = kwargs.get("model", "glm-4")
            temperature = kwargs.get("temperature", 0.7)

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                **{k: v for k, v in kwargs.items() if k not in ["model", "temperature"]}
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error calling Zhipu API: {str(e)}")
            raise

class DashScopeProvider(LLMProvider):
    """Alibaba Cloud DashScope provider implementation (Qwen models)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DashScope API key is required")

        # Import here to avoid dependency if not used
        try:
            from dashscope import Generation
            self.client = Generation()
            self.api_key = api_key
            logger.info("DashScopeProvider initialized successfully")
        except ImportError:
            logger.error("dashscope package not installed. Please install it with: pip install dashscope")
            raise

    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate chat completion using DashScope (Qwen)
        :param messages: List of message dictionaries with 'role' and 'content'
        :param kwargs: Additional parameters (e.g., model, temperature)
        :return: Generated response string
        """
        try:
            model = kwargs.get("model", "qwen-turbo")
            temperature = kwargs.get("temperature", 0.7)

            # Convert messages to DashScope format
            dashscope_messages = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "assistant"
                dashscope_messages.append({"role": role, "content": msg["content"]})

            response = self.client.chat(
                model=model,
                messages=dashscope_messages,
                temperature=temperature,
                **{k: v for k, v in kwargs.items() if k not in ["model", "temperature"]}
            )

            return response.output.choices[0].message.content

        except Exception as e:
            logger.error(f"Error calling DashScope API: {str(e)}")
            raise

class LLMProviderFactory:
    """Factory class to create LLM provider instances"""

    PROVIDER_MAP = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "zhipu": ZhipuProvider,
        "dashscope": DashScopeProvider,
    }

    @classmethod
    def create_provider(cls, provider_name: str, **kwargs) -> LLMProvider:
        """
        Create an instance of the specified LLM provider
        :param provider_name: Name of the provider ('openai', 'claude', 'zhipu', etc.)
        :param kwargs: Additional arguments for provider initialization
        :return: Instance of the requested LLM provider
        """
        provider_class = cls.PROVIDER_MAP.get(provider_name.lower())
        if not provider_class:
            available_providers = ", ".join(cls.PROVIDER_MAP.keys())
            raise ValueError(f"Unknown provider: {provider_name}. Available providers: {available_providers}")

        return provider_class(**kwargs)

    @classmethod
    def list_available_providers(cls) -> List[str]:
        """
        List all available LLM providers
        :return: List of available provider names
        """
        return list(cls.PROVIDER_MAP.keys())

class LLMManager:
    """
    Manager class for handling multiple LLM providers
    Provides unified interface for chat completion with provider switching
    """

    def __init__(self):
        """Initialize the LLM Manager"""
        self.providers: Dict[str, LLMProvider] = {}
        self.default_provider: Optional[str] = None
        logger.info("LLMManager initialized")

    def register_provider(self, name: str, provider: LLMProvider):
        """
        Register an LLM provider

        Args:
            name: Provider name (e.g., 'openai', 'claude')
            provider: LLMProvider instance
        """
        self.providers[name] = provider
        logger.info(f"Registered LLM provider: {name}")

        # Set as default if it's the first one
        if self.default_provider is None:
            self.default_provider = name
            logger.info(f"Set default provider to: {name}")

    def set_default_provider(self, name: str):
        """
        Set the default LLM provider

        Args:
            name: Provider name to set as default

        Raises:
            ValueError: If provider is not registered
        """
        if name not in self.providers:
            raise ValueError(f"Provider '{name}' is not registered. Available: {list(self.providers.keys())}")

        self.default_provider = name
        logger.info(f"Default provider set to: {name}")

    def list_providers(self) -> List[str]:
        """
        List all registered providers

        Returns:
            List of provider names
        """
        return list(self.providers.keys())

    def get_default_provider(self) -> Optional[str]:
        """
        Get the current default provider name

        Returns:
            Default provider name or None if none registered
        """
        return self.default_provider

    def chat_completion(self, messages: List[Dict[str, str]], provider: Optional[str] = None, **kwargs) -> str:
        """
        Generate chat completion using specified or default provider

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            provider: Provider name to use (uses default if None)
            **kwargs: Additional parameters for the provider

        Returns:
            Generated response string

        Raises:
            ValueError: If no providers are available or provider not found
        """
        if not self.providers:
            raise ValueError("No LLM providers have been registered")

        # Determine which provider to use
        provider_name = provider or self.default_provider
        if provider_name is None:
            raise ValueError("No default LLM provider set and no provider specified")

        if provider_name not in self.providers:
            available = ", ".join(self.providers.keys())
            raise ValueError(f"Provider '{provider_name}' not found. Available: {available}")

        # Get the provider and call chat_completion
        llm_provider = self.providers[provider_name]
        return llm_provider.chat_completion(messages, **kwargs)

# Backward compatibility aliases
ZhipuAIProvider = ZhipuProvider  # For main_service_enhanced.py compatibility

# Example usage and testing
if __name__ == "__main__":
    # Example of how to use the factory to create providers
    # Note: Actual API keys would be needed to make real calls

    factory = LLMProviderFactory()
    print("Available providers:", factory.list_available_providers())

    # Example usage (would need valid API keys to work):
    # provider = LLMProviderFactory.create_provider("openai", api_key="your-openai-key")
    # messages = [{"role": "user", "content": "Hello, how are you?"}]
    # response = provider.chat_completion(messages)
    # print(response)
