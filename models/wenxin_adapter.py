"""
百度文心一言 (ERNIE Bot) 模型适配器
使用百度千帆大模型平台 API
"""
import os
import requests
from typing import Iterator, Optional
from .base import BaseModel


class WenxinAdapter(BaseModel):
    """
    百度文心一言模型适配器
    
    需要环境变量:
    - WENXIN_API_KEY: 百度智能云应用的 API Key
    - WENXIN_SECRET_KEY: 百度智能云应用的 Secret Key
    """
    
    API_BASE_URL = "https://aip.baidubce.com"
    DEFAULT_MODEL = "ernie-bot-4"  # 可选: ernie-bot, ernie-bot-4, ernie-bot-turbo, ernie-speed
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("WENXIN_API_KEY")
        self.secret_key = secret_key or os.getenv("WENXIN_SECRET_KEY")
        self.model = model or os.getenv("WENXIN_MODEL", self.DEFAULT_MODEL)
        self._access_token: Optional[str] = None
        
        if not self.api_key or not self.secret_key:
            raise ValueError("WENXIN_API_KEY and WENXIN_SECRET_KEY must be provided")
    
    def _get_access_token(self) -> str:
        """获取百度 API 访问令牌"""
        if self._access_token:
            return self._access_token
            
        url = f"{self.API_BASE_URL}/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "access_token" not in result:
                raise RuntimeError(f"Failed to get access token: {result}")
            
            self._access_token = result["access_token"]
            return self._access_token
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to obtain access token: {e}")
    
    def _get_model_endpoint(self) -> str:
        """获取模型对应的 API 端点"""
        model_endpoints = {
            "ernie-bot": "completions",
            "ernie-bot-4": "completions_pro",
            "ernie-bot-turbo": "eb-instant",
            "ernie-speed": "ernie-speed"
        }
        endpoint = model_endpoints.get(self.model, "completions_pro")
        return f"{self.API_BASE_URL}/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{endpoint}"
    
    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        """
        生成文本回复
        
        Args:
            prompt: 用户输入的问题
            context: 可选的上下文信息
            
        Returns:
            模型生成的回复文本
        """
        access_token = self._get_access_token()
        url = f"{self._get_model_endpoint()}?access_token={access_token}"
        
        # 构建消息列表
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "messages": messages,
            "temperature": 0.8,
            "top_p": 0.8,
            "penalty_score": 1.0,
            "stream": False
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            if "error_code" in result:
                raise RuntimeError(f"Wenxin API error: {result.get('error_msg', 'Unknown error')}")
            
            return result.get("result", "")
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to generate response: {e}")
    
    def generate_stream(self, prompt: str, context: Optional[str] = None) -> Iterator[str]:
        """
        流式生成文本回复
        
        Args:
            prompt: 用户输入的问题
            context: 可选的上下文信息
            
        Yields:
            模型生成的文本片段
        """
        access_token = self._get_access_token()
        url = f"{self._get_model_endpoint()}?access_token={access_token}"
        
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "messages": messages,
            "temperature": 0.8,
            "top_p": 0.8,
            "stream": True
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # 移除 'data: ' 前缀
                        if data == '[DONE]':
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            if "result" in chunk:
                                yield chunk["result"]
                        except json.JSONDecodeError:
                            continue
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to stream response: {e}")
    
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        try:
            self._get_access_token()
            return True
        except Exception:
            return False
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "provider": "baidu",
            "name": "文心一言",
            "model": self.model,
            "capabilities": ["chat", "streaming"],
            "max_tokens": 8192
        }
