"""OpenAI provider - Paid, most capable"""

import requests
from typing import Optional

from agent.llm.base import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """OpenAI - GPT-4 and GPT-3.5"""
    
    ENV_KEY = "OPENAI_API_KEY"
    DEFAULT_MODEL = "gpt-4o"
    BASE_URL = "https://api.openai.com/v1/chat/completions"
    
    def generate(self, prompt: str, test_mode: bool = False, **kwargs) -> LLMResponse:
        if not test_mode:
            prompt = self._apply_jailbreak(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        response = requests.post(self.BASE_URL, headers=headers, json=data, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=self.model,
                provider="openai",
                tokens_used=data.get("usage", {}).get("total_tokens")
            )
        raise Exception(f"OpenAI error: {response.text}")