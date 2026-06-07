"""Base LLM provider classes"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
import os

from agent.llm.jailbreak import JailbreakManager, JailbreakMethod


@dataclass
class LLMResponse:
    """Structured LLM response"""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    raw_response: Optional[Any] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    ENV_KEY: Optional[str] = None
    DEFAULT_MODEL: Optional[str] = None

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        # Priority: explicit arg → env var → stored key (key_manager)
        self.api_key = api_key or self._resolve_api_key()
        self.model = model or self._resolve_model()
        self.jailbreak_method = JailbreakMethod.PENTESTER_MODE
        self.authorization_context: Optional[Dict] = None

    def _resolve_api_key(self) -> Optional[str]:
        """Resolve API key from env var, then from key_manager store."""
        # 1. Env var
        if self.ENV_KEY:
            env_val = os.environ.get(self.ENV_KEY)
            if env_val:
                return env_val
        # 2. key_manager stored key — derive provider name from ENV_KEY
        if self.ENV_KEY:
            try:
                from config.key_manager import key_manager, PROVIDER_ENV_VARS
                # Reverse-lookup provider name from env key
                provider_name = next(
                    (p for p, e in PROVIDER_ENV_VARS.items() if e == self.ENV_KEY),
                    None,
                )
                if provider_name:
                    stored = key_manager.get_stored_key(provider_name)
                    if stored:
                        return stored
            except ImportError:
                pass
        return None

    def _resolve_model(self) -> Optional[str]:
        """Return the user-preferred model or class default."""
        if self.ENV_KEY:
            try:
                from config.key_manager import key_manager, PROVIDER_ENV_VARS
                provider_name = next(
                    (p for p, e in PROVIDER_ENV_VARS.items() if e == self.ENV_KEY),
                    None,
                )
                if provider_name:
                    preferred = key_manager.get_default_model(provider_name)
                    if preferred:
                        return preferred
            except ImportError:
                pass
        return self.DEFAULT_MODEL

    def set_jailbreak(self, method: JailbreakMethod):
        """Set active jailbreak method"""
        self.jailbreak_method = method

    def set_authorization(self, auth_ref: str, scope: str = "Full assessment"):
        """Set authorization context"""
        self.authorization_context = {"authorization": auth_ref, "scope": scope}

    def _apply_jailbreak(self, prompt: str) -> str:
        """Apply jailbreak to prompt"""
        return JailbreakManager.apply(self.jailbreak_method, prompt, self.authorization_context)

    @abstractmethod
    def generate(self, prompt: str, test_mode: bool = False, **kwargs) -> LLMResponse:
        """Generate response from LLM"""
        pass

    def test_connection(self) -> bool:
        """Test if provider is accessible"""
        try:
            self.generate("Respond with exactly one word: OK", test_mode=True)
            return True
        except Exception:
            return False