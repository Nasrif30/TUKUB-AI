"""Anthropic Claude provider - Paid"""

import requests
from typing import Optional

from agent.llm.base import BaseLLMProvider, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    """Anthropic - Claude models"""
    
    ENV_KEY = "ANTHROPIC_API_KEY"
    DEFAULT_MODEL = "claude-3-sonnet-20240229"
    BASE_URL = "https://api.anthropic.com/v1/messages"
    
    def generate(self, prompt: str, test_mode: bool = False, **kwargs) -> LLMResponse:
        if not test_mode:
            prompt = self._apply_jailbreak(prompt)
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        response = requests.post(self.BASE_URL, headers=headers, json=data, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            return LLMResponse(
                content=data["content"][0]["text"],
                model=self.model,
                provider="anthropic"
            )
        raise Exception(f"Anthropic error: {response.text}")