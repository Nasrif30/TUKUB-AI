"""Ollama provider - Free, local, offline-capable"""

import requests
from typing import Optional

from agent.llm.base import BaseLLMProvider, LLMResponse


class OllamaProvider(BaseLLMProvider):
    """Ollama - Local LLM provider"""
    
    ENV_KEY = "OLLAMA_API_KEY"  # Not required, for consistency
    DEFAULT_MODEL = "llama3.2"
    DEFAULT_URL = "http://localhost:11434"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: str = None):
        super().__init__(api_key, model)
        self.base_url = base_url or self.DEFAULT_URL
    
    def generate(self, prompt: str, test_mode: bool = False, **kwargs) -> LLMResponse:
        if not test_mode:
            prompt = self._apply_jailbreak(prompt)
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": kwargs.get("temperature", 0.7)}
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            return LLMResponse(
                content=data.get("response", ""),
                model=self.model,
                provider="ollama",
                tokens_used=data.get("eval_count")
            )
        else:
            error_msg = response.text
            if "not found" in error_msg.lower():
                raise Exception(
                    f"\n[red]Ollama Model Not Found![/red]\n"
                    f"The model '{self.model}' is not downloaded yet.\n"
                    f"To fix this, open a new terminal and run: [bold yellow]ollama pull {self.model}[/bold yellow]"
                )
            raise Exception(f"Ollama error: {error_msg}")