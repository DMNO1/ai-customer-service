"""
LLM Provider for AI Customer Service System
Handles multiple LLM providers (OpenAI, Claude, etc.)
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import os

try:
    from openai import OpenAI
    import anthropic
except ImportError as e:
    logging.error(f"Missing required packages for LLM providers: {e}")
    raise


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers
    """
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict], **kwargs) -> str:
        """
        Generate chat completion
        
        Args:
            messages: List of messages in the conversation
            **kwargs: Additional parameters for the specific provider
            
        Returns:
            Generated response text
        """
        pass


class OpenAIProvider(LLMProvider):
    """
    OpenAI API provider implementation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY environment variable
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
        logging.info("OpenAIProvider initialized")
    
    def chat_completion(self, messages: List[Dict], model: str = "gpt-3.5-turbo", **kwargs) -> str:
        """
        Generate chat completion using OpenAI
        
        Args:
            messages: List of messages in the conversation
            model: Model to use (default: gpt-3.5-turbo)
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error in OpenAI chat completion: {str(e)}")
            raise


class ClaudeProvider(LLMProvider):
    """
    Anthropic Claude API provider implementation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude provider
        
        Args:
            api_key: Claude API key. If None, will use ANTHROPIC_API_KEY environment variable
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Claude API key not provided and ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        logging.info("ClaudeProvider initialized")
    
    def chat_completion(self, messages: List[Dict], model: str = "claude-3-opus-20240229", **kwargs) -> str:
        """
        Generate chat completion using Claude
        
        Args:
            messages: List of messages in the conversation
            model: Model to use (default: claude-3-opus-20240229)
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            # Convert messages to Claude format
            # Claude expects alternating "user" and "assistant" roles
            formatted_messages = []
            for msg in messages:
                if msg['role'] in ['user', 'assistant', 'system']:
                    # Handle system message separately
                    if msg['role'] == 'system':
                        # Add to system parameter instead of messages
                        kwargs['system'] = msg['content']
                    else:
                        formatted_messages.append({
                            'role': msg['role'],
                            'content': msg['content']
                        })
            
            response = self.client.messages.create(
                model=model,
                messages=formatted_messages,
                max_tokens=kwargs.pop('max_tokens', 1000),
                **kwargs
            )
            
            return response.content[0].text
            
        except Exception as e:
            logging.error(f"Error in Claude chat completion: {str(e)}")
            raise


class ZhipuAIProvider(LLMProvider):
    """
    ZhipuAI (ChatGLM) provider implementation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ZhipuAI provider
        
        Args:
            api_key: ZhipuAI API key. If None, will use ZHIPU_API_KEY environment variable
        """
        self.api_key = api_key or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError("ZhipuAI API key not provided and ZHIPU_API_KEY environment variable not set")
        
        # Import ZhipuAI library dynamically
        try:
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("zhipuai package is required for ZhipuAI provider. Install with: pip install zhipuai")
        
        logging.info("ZhipuAIProvider initialized")
    
    def chat_completion(self, messages: List[Dict], model: str = "glm-4", **kwargs) -> str:
        """
        Generate chat completion using ZhipuAI
        
        Args:
            messages: List of messages in the conversation
            model: Model to use (default: glm-4)
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error in ZhipuAI chat completion: {str(e)}")
            raise


class DashScopeProvider(LLMProvider):
    """
    DashScope (Alibaba Tongyi) provider implementation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize DashScope provider
        
        Args:
            api_key: DashScope API key. If None, will use DASHSCOPE_API_KEY environment variable
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DashScope API key not provided and DASHSCOPE_API_KEY environment variable not set")
        
        # Import DashScope library dynamically
        try:
            import dashscope
            dashscope.api_key = self.api_key
            self.dashscope = dashscope
        except ImportError:
            raise ImportError("dashscope package is required for DashScope provider. Install with: pip install dashscope")
        
        logging.info("DashScopeProvider initialized")
    
    def chat_completion(self, messages: List[Dict], model: str = "qwen-max", **kwargs) -> str:
        """
        Generate chat completion using DashScope
        
        Args:
            messages: List of messages in the conversation
            model: Model to use (default: qwen-max)
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            response = self.dashscope.ChatCompletion.create(
                model=model,
                messages=messages,
                **kwargs
            )
            
            return response.output.text
            
        except Exception as e:
            logging.error(f"Error in DashScope chat completion: {str(e)}")
            raise


class LLMManager:
    """
    Manager class to handle multiple LLM providers
    """
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        logging.info("LLMManager initialized")
    
    def register_provider(self, name: str, provider: LLMProvider):
        """
        Register an LLM provider
        
        Args:
            name: Name of the provider
            provider: Instance of LLMProvider
        """
        self.providers[name] = provider
        if self.default_provider is None:
            self.default_provider = name
        logging.info(f"Registered LLM provider: {name}")
    
    def set_default_provider(self, name: str):
        """
        Set the default provider
        
        Args:
            name: Name of the provider to set as default
        """
        if name not in self.providers:
            raise ValueError(f"Provider {name} not registered")
        self.default_provider = name
        logging.info(f"Set default LLM provider to: {name}")
    
    def chat_completion(self, messages: List[Dict], provider: Optional[str] = None, **kwargs) -> str:
        """
        Generate chat completion using the specified or default provider
        
        Args:
            messages: List of messages in the conversation
            provider: Name of provider to use (uses default if None)
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        if provider is None:
            provider = self.default_provider
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not registered or available")
        
        return self.providers[provider].chat_completion(messages, **kwargs)
    
    def list_providers(self) -> List[str]:
        """
        List available providers
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())


# Initialize logging
logging.basicConfig(level=logging.INFO)


def test_llm_providers():
    """
    Test function for LLM providers
    """
    print("Testing LLM Providers...")
    
    # Example usage would go here
    manager = LLMManager()
    
    # Register providers based on available keys
    if os.getenv("OPENAI_API_KEY"):
        manager.register_provider("openai", OpenAIProvider())
    
    if os.getenv("ANTHROPIC_API_KEY"):
        manager.register_provider("anthropic", ClaudeProvider())
    
    if os.getenv("ZHIPU_API_KEY"):
        manager.register_provider("zhipu", ZhipuAIProvider())
    
    if os.getenv("DASHSCOPE_API_KEY"):
        manager.register_provider("dashscope", DashScopeProvider())
    
    print(f"Available providers: {manager.list_providers()}")


if __name__ == "__main__":
    test_llm_providers()