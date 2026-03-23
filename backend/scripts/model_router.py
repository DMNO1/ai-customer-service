"""
Model Router
管理和路由不同AI模型的请求。
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import openai
import anthropic
import requests

# 加载环境变量
load_dotenv()

class ModelRouter:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # 初始化客户端
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        if self.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
    
    def route_to_model(self, model_name: str, prompt: str, **kwargs) -> Optional[str]:
        """
        根据模型名称将请求路由到相应的AI模型。
        
        Args:
            model_name: 模型名称 (e.g., 'gpt-4', 'claude-2', 'llama2').
            prompt: 要发送给模型的提示。
            **kwargs: 模型特定的参数。
            
        Returns:
            模型生成的响应文本，如果失败则返回None。
        """
        try:
            if model_name.startswith("gpt"):
                return self._call_openai(model_name, prompt, **kwargs)
            elif model_name.startswith("claude"):
                return self._call_anthropic(model_name, prompt, **kwargs)
            else:
                # 假设是Ollama支持的模型
                return self._call_ollama(model_name, prompt, **kwargs)
        except Exception as e:
            print(f"Error calling model {model_name}: {e}")
            return None
    
    def _call_openai(self, model: str, prompt: str, **kwargs) -> str:
        """调用OpenAI API"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message['content']
    
    def _call_anthropic(self, model: str, prompt: str, **kwargs) -> str:
        """调用Anthropic API"""
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        response = self.anthropic_client.completions.create(
            model=model,
            prompt=prompt,
            **kwargs
        )
        return response.completion
    
    def _call_ollama(self, model: str, prompt: str, **kwargs) -> str:
        """调用本地Ollama实例"""
        response = requests.post(
            f"{self.ollama_base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
        )
        response.raise_for_status()
        return response.json()["response"]

# 用于测试的主函数
if __name__ == "__main__":
    router = ModelRouter()
    
    # 测试不同的模型（需要配置相应的API密钥）
    # print(router.route_to_model("gpt-3.5-turbo", "Hello, how are you?"))
    # print(router.route_to_model("claude-2", "Hello, how are you?"))
    # print(router.route_to_model("llama2", "Hello, how are you?"))