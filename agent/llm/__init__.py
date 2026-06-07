"""LLM Provider auto-discovery and registry"""

import os
from typing import Dict, Type, Optional

from agent.llm.base import BaseLLMProvider


_PROVIDERS: Dict[str, Type[BaseLLMProvider]] = {}
_API_KEYS: Dict[str, Optional[str]] = {}   # provider -> env var name (or None)


def register(name: str, provider_class: Type[BaseLLMProvider], env_key: Optional[str]):
    """Register a provider class with its env var name."""
    _PROVIDERS[name] = provider_class
    _API_KEYS[name] = env_key


def _resolve_key(provider: str) -> Optional[str]:
    """
    Try to find a usable API key for `provider`:
        1. Environment variable
        2. Stored key (via key_manager / config set)
    Returns None if neither is available.
    """
    env_var = _API_KEYS.get(provider)
    if env_var:
        val = os.environ.get(env_var)
        if val:
            return val
    # Fall back to key_manager store
    try:
        from config.key_manager import key_manager
        stored = key_manager.get_stored_key(provider)
        if stored:
            return stored
    except ImportError:
        pass
    return None


def detect_providers() -> Dict[str, bool]:
    """
    Detect which providers have an API key available (env var OR stored).
    Ollama is always available (local).
    """
    result = {}
    for name, env_key in _API_KEYS.items():
        if env_key is None:              # local provider (ollama)
            result[name] = True
        else:
            result[name] = bool(_resolve_key(name))
    return result


def get_available_providers() -> Dict[str, Type[BaseLLMProvider]]:
    """Return provider classes that have a usable API key."""
    available = {}
    for name, env_key in _API_KEYS.items():
        if env_key is None:              # local
            available[name] = _PROVIDERS[name]
        elif _resolve_key(name):
            available[name] = _PROVIDERS[name]
    return available


def get_provider(name: str) -> Optional[Type[BaseLLMProvider]]:
    """Get a provider class by name."""
    return _PROVIDERS.get(name)


def list_providers() -> Dict[str, Type[BaseLLMProvider]]:
    """List all registered providers."""
    return dict(_PROVIDERS)


def get_default_provider() -> str:
    """
    Return the best available provider.

    Priority:
        1. First cloud provider with a key (env var or stored)
        2. Ollama (local, always available)
    """
    for name in ["nvidia", "groq", "openrouter", "openai", "anthropic", "huggingface"]:
        if _resolve_key(name):
            return name
    return "ollama"