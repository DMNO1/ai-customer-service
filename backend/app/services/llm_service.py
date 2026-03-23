"""
大语言模型服务 - 多供应商抽象
支持 OpenAI、Claude、智谱、通义千问
"""

import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx
import json

import openai
from anthropic import Anthropic
from zhipuai import ZhipuAI
from dashscope import Generation

from app.core.config import settings
from app.core.exceptions import LLMException
import structlog

logger = structlog.get_logger()

class LLMProvider(ABC):
    """LLM 提供者抽象基类"""

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """聊天补全"""
        pass

    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天补全"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI 提供者"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return resp.choices[0].message.content

        except openai.RateLimitError as e:
            logger.error("openai_rate_limit", error=str(e))
            raise LLMException("OpenAI 额度不足或触发限流", provider="openai")
        except openai.APIError as e:
            logger.error("openai_api_error", error=str(e))
            raise LLMException(f"OpenAI API 错误: {str(e)}", provider="openai")
        except Exception as e:
            logger.error("openai_unexpected_error", error=str(e))
            raise LLMException(f"OpenAI 调用失败: {str(e)}", provider="openai")

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error("openai_stream_error", error=str(e))
            raise LLMException(f"OpenAI 流式调用失败: {str(e)}", provider="openai")


class ClaudeProvider(LLMProvider):
    """Claude 提供者 (Anthropic)"""

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.model = model
        self.client = Anthropic(api_key=api_key)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        try:
            # Anthropic API 需要特殊格式
            system_msg = ""
            filtered_messages = []

            for msg in messages:
                if msg.get("role") == "system":
                    system_msg = msg.get("content", "")
                else:
                    filtered_messages.append(msg)

            resp = await self.client.messages.create(
                model=self.model,
                system=system_msg,
                messages=filtered_messages,
                temperature=temperature,
                max_tokens=max_tokens or 1024,
                **kwargs
            )
            return resp.content[0].text

        except Anthropic.RateLimitError as e:
            logger.error("claude_rate_limit", error=str(e))
            raise LLMException("Claude 额度不足", provider="claude")
        except Anthropic.APIError as e:
            logger.error("claude_api_error", error=str(e))
            raise LLMException(f"Claude API 错误: {str(e)}", provider="claude")
        except Exception as e:
            logger.error("claude_unexpected_error", error=str(e))
            raise LLMException(f"Claude 调用失败: {str(e)}", provider="claude")

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        try:
            system_msg = ""
            filtered_messages = []
            for msg in messages:
                if msg.get("role") == "system":
                    system_msg = msg.get("content", "")
                else:
                    filtered_messages.append(msg)

            with self.client.messages.stream(
                model=self.model,
                system=system_msg,
                messages=filtered_messages,
                temperature=temperature,
                max_tokens=max_tokens or 1024,
                **kwargs
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error("claude_stream_error", error=str(e))
            raise LLMException(f"Claude 流式调用失败: {str(e)}", provider="claude")


class ZhipuProvider(LLMProvider):
    """智谱 AI 提供者"""

    def __init__(self, api_key: str, model: str = "glm-4"):
        self.model = model
        self.client = ZhipuAI(api_key=api_key)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        try:
            resp = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            )
            return resp.choices[0].message.content

        except Exception as e:
            logger.error("zhipu_error", error=str(e))
            raise LLMException(f"智谱 AI 调用失败: {str(e)}", provider="zhipu")

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        try:
            resp = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                )
            )
            for chunk in resp:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error("zhipu_stream_error", error=str(e))
            raise LLMException(f"智谱 AI 流式调用失败: {str(e)}", provider="zhipu")


class DashscopeProvider(LLMProvider):
    """通义千问提供者"""

    def __init__(self, api_key: str, model: str = "qwen-turbo"):
        self.model = model
        self.api_key = api_key

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        try:
            resp = Generation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 1024,
                result_format='message'
            )
            return resp.output.choices[0].message.content

        except Exception as e:
            logger.error("dashscope_error", error=str(e))
            raise LLMException(f"通义千问调用失败: {str(e)}", provider="dashscope")

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        try:
            resp = Generation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 1024,
                stream=True,
                result_format='message'
            )
            for chunk in resp:
                if chunk.output and chunk.output.choices:
                    yield chunk.output.choices[0].delta.content

        except Exception as e:
            logger.error("dashscope_stream_error", error=str(e))
            raise LLMException(f"通义千问流式调用失败: {str(e)}", provider="dashscope")


class LLMService:
    """LLM 统一服务"""

    _providers = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "zhipu": ZhipuProvider,
        "dashscope": DashscopeProvider
    }

    def __init__(self, default_provider: str = "openai"):
        self.default_provider = default_provider
        self._instances = {}

        # 初始化所有可用的提供者
        for name, cls in self._providers.items():
            api_key = getattr(settings, f"{name}_api_key", None)
            if api_key:
                try:
                    self._instances[name] = cls(api_key=api_key)
                    logger.info("llm_provider_initialized", provider=name)
                except Exception as e:
                    logger.warning("llm_provider_init_failed", provider=name, error=str(e))

        if not self._instances:
            logger.warning("no_llm_providers_configured")

    def get_provider(self, provider: Optional[str] = None) -> LLMProvider:
        """获取指定提供者实例"""
        name = provider or self.default_provider
        if name not in self._instances:
            raise LLMException(
                f"LLM 提供者 '{name}' 未配置或不可用",
                provider=name
            )
        return self._instances[name]

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """统一聊天补全接口"""
        prov = self.get_provider(provider)
        logger.info("llm_chat_completion", provider=provider or self.default_provider)
        return await prov.chat_completion(messages, temperature, max_tokens, **kwargs)

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """统一流式聊天补全接口"""
        prov = self.get_provider(provider)
        logger.info("llm_stream_start", provider=provider or self.default_provider)
        async for chunk in prov.chat_completion_stream(messages, temperature, max_tokens, **kwargs):
            yield chunk

    def list_available_providers(self) -> List[str]:
        """列��所有可用的提供者"""
        return list(self._instances.keys())


# 全局 LLM 服务实例
llm_service = LLMService(default_provider="openai")
