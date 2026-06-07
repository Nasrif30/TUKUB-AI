"""OpenRouter provider - Access 200+ LLM models"""

import requests
from typing import Optional, List, Dict

from agent.llm.base import BaseLLMProvider, LLMResponse


class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter Provider - Access 200+ LLM models including:
    - Free models: google/gemini-2.0-flash-exp:free, mistralai/mistral-7b-instruct:free
    - Paid models: anthropic/claude-3.5-sonnet, openai/gpt-4o, meta-llama/llama-3.3-70b-instruct
    """
    
    ENV_KEY = "OPENROUTER_API_KEY"
    DEFAULT_MODEL = "google/gemini-2.0-flash-exp:free"
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None,
                 site_url: str = None, site_name: str = None):
        super().__init__(api_key, model)
        self.site_url = site_url or "http://localhost"
        self.site_name = site_name or "TUKUB AI"
    
    def generate(self, prompt: str, test_mode: bool = False, **kwargs) -> LLMResponse:
        if not test_mode:
            prompt = self._apply_jailbreak(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096)
        }
        
        response = requests.post(self.BASE_URL, headers=headers, json=data, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data.get("model", self.model),
                provider="openrouter",
                tokens_used=data.get("usage", {}).get("total_tokens")
            )
        elif response.status_code == 402:
            raise Exception("OpenRouter: Insufficient credits. Add credits or switch to free model.")
        else:
            raise Exception(f"OpenRouter error ({response.status_code}): {response.text}")
    
    @classmethod
    def list_free_models(cls) -> List[str]:
        """List free models available on OpenRouter"""
        return [
            "google/gemini-2.0-flash-exp:free",
            "google/gemini-flash-1.5:free",
            "mistralai/mistral-7b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free",
            "qwen/qwen-2.5-7b-instruct:free",
            "meta-llama/llama-3.2-3b-instruct:free"
        ]
    
    @classmethod
    def list_paid_models(cls) -> List[Dict]:
        """List popular paid models"""
        return [
            {"name": "anthropic/claude-3.5-sonnet", "description": "Claude 3.5 Sonnet"},
            {"name": "openai/gpt-4o", "description": "GPT-4o"},
            {"name": "meta-llama/llama-3.3-70b-instruct", "description": "Llama 3.3 70B"},
            {"name": "deepseek/deepseek-chat", "description": "DeepSeek Chat"}
        ]