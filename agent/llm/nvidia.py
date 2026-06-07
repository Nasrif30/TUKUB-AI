"""NVIDIA NIM Provider - OpenAI-compatible API with reasoning support"""

from typing import Optional

from agent.llm.base import BaseLLMProvider, LLMResponse

# NVIDIA NIM fallback key (free-tier demo key — set NVIDIA_API_KEY env var for your own)
_FALLBACK_KEY = ""


class NVIDIAProvider(BaseLLMProvider):
    """NVIDIA NIM - Free cloud inference with reasoning models"""

    ENV_KEY = "NVIDIA_API_KEY"
    DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
    BASE_URL = "https://integrate.api.nvidia.com/v1"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key, model)
        self.reasoning_enabled = True
        self.reasoning_budget = 16384

    def generate(self, prompt: str, test_mode: bool = False, **kwargs) -> LLMResponse:
        if not test_mode:
            prompt = self._apply_jailbreak(prompt)

        # Lazy import so the module loads even if openai is not installed yet
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError(
                "openai package is required for NVIDIAProvider. "
                "Install it with: pip install openai"
            ) from e

        api_key = self.api_key or _FALLBACK_KEY
        client = OpenAI(base_url=self.BASE_URL, api_key=api_key)

        completion = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 1024),
            temperature=kwargs.get("temperature", 0.7),
        )

        return LLMResponse(
            content=completion.choices[0].message.content,
            model=self.model,
            provider="nvidia",
            tokens_used=getattr(completion.usage, "total_tokens", None),
        )

    def set_reasoning(self, enabled: bool = True, budget: int = 16384):
        """Toggle extended reasoning (supported on nemotron-ultra models)."""
        self.reasoning_enabled = enabled
        self.reasoning_budget = budget
