"""
TUKUB AI - API Key Manager
Persistent storage of provider API keys in ~/.tukub/keys.json.

Priority order when resolving a key:
    1. Environment variable  (e.g. OPENAI_API_KEY)
    2. Keys saved via `tukub config set` (stored in ~/.tukub/keys.json)
    3. Provider-level hardcoded fallback (only NVIDIA has one)
"""

import json
import os
import stat
from pathlib import Path
from typing import Dict, Optional


# Location of the key store
_KEY_FILE = Path.home() / ".tukub" / "keys.json"

# Map provider name -> env var
PROVIDER_ENV_VARS: Dict[str, Optional[str]] = {
    "ollama": None,                    # local, no key needed
    "groq": "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "nvidia": "NVIDIA_API_KEY",
    "huggingface": "HUGGINGFACE_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}

# Human-readable info per provider
PROVIDER_INFO: Dict[str, Dict] = {
    "ollama": {
        "label": "Ollama (Local)",
        "type": "local",
        "cost": "Free",
        "url": "https://ollama.com",
        "note": "No API key needed — Ollama runs locally.",
        "default_model": "llama3.2",
        "models": ["llama3.2", "llama3.1", "mistral", "codellama", "phi3", "gemma2"],
    },
    "groq": {
        "label": "Groq Cloud",
        "type": "cloud",
        "cost": "Free tier",
        "url": "https://console.groq.com",
        "note": "Get your free API key at console.groq.com",
        "default_model": "llama3-70b-8192",
        "models": ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
    },
    "openrouter": {
        "label": "OpenRouter",
        "type": "cloud",
        "cost": "Free credits + paid",
        "url": "https://openrouter.ai/keys",
        "note": "200+ models. Free credits available at openrouter.ai",
        "default_model": "google/gemini-2.0-flash-exp:free",
        "models": [
            "google/gemini-2.0-flash-exp:free",
            "mistralai/mistral-7b-instruct:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o",
        ],
    },
    "nvidia": {
        "label": "NVIDIA NIM",
        "type": "cloud",
        "cost": "Free tier",
        "url": "https://build.nvidia.com",
        "note": "Free API key at build.nvidia.com — includes reasoning models.",
        "default_model": "nvidia/nemotron-3-ultra-550b-a55b",
        "models": [
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "meta/llama3-70b-instruct",
        ],
    },
    "huggingface": {
        "label": "Hugging Face",
        "type": "cloud",
        "cost": "Free tier",
        "url": "https://huggingface.co/settings/tokens",
        "note": "Get your access token at huggingface.co/settings/tokens",
        "default_model": "mistralai/Mistral-7B-Instruct-v0.2",
        "models": ["mistralai/Mistral-7B-Instruct-v0.2", "meta-llama/Llama-2-7b-chat-hf"],
    },
    "openai": {
        "label": "OpenAI",
        "type": "cloud",
        "cost": "Paid",
        "url": "https://platform.openai.com/api-keys",
        "note": "Get your API key at platform.openai.com/api-keys",
        "default_model": "gpt-4o",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "anthropic": {
        "label": "Anthropic",
        "type": "cloud",
        "cost": "Paid",
        "url": "https://console.anthropic.com",
        "note": "Get your API key at console.anthropic.com",
        "default_model": "claude-3-sonnet-20240229",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
    },
}


class KeyManager:
    """Manages persistent API key storage for all LLM providers."""

    def __init__(self, key_file: Path = _KEY_FILE):
        self.key_file = key_file
        self._data: Dict[str, str] = {}
        self._load()

    # ------------------------------------------------------------------
    # Internal I/O
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load keys from disk (creates file if missing)."""
        if self.key_file.exists():
            try:
                with open(self.key_file, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._data = {}
        else:
            self._data = {}

    def _save(self) -> None:
        """Persist keys to disk with restricted permissions."""
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.key_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
        # Restrict to owner read/write only (600) where supported
        try:
            os.chmod(self.key_file, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass  # Windows may not support chmod, that's fine

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_key(self, provider: str, key: str) -> None:
        """Save or update an API key for a provider."""
        self._data[provider] = key.strip()
        self._save()

    def get_stored_key(self, provider: str) -> Optional[str]:
        """Return the stored key for a provider (does NOT check env vars)."""
        return self._data.get(provider)

    def remove_key(self, provider: str) -> bool:
        """Remove a stored key. Returns True if it existed."""
        if provider in self._data:
            del self._data[provider]
            self._save()
            return True
        return False

    def list_stored(self) -> Dict[str, str]:
        """Return all stored provider → key mappings (raw)."""
        return dict(self._data)

    def has_key(self, provider: str) -> bool:
        """True if a key is stored for this provider (ignores env vars)."""
        return provider in self._data and bool(self._data[provider])

    def resolve_key(self, provider: str) -> Optional[str]:
        """
        Resolve the best available API key for a provider.

        Priority: env var → stored key → None
        (Caller's code may have additional hardcoded fallbacks.)
        """
        env_var = PROVIDER_ENV_VARS.get(provider)
        if env_var:
            env_val = os.environ.get(env_var)
            if env_val:
                return env_val
        return self._data.get(provider)

    def get_status(self, provider: str) -> Dict:
        """
        Return a status dict for a provider:
            source: 'local' | 'env' | 'stored' | 'none'
            key_preview: first 8 chars + '...' or None
            available: bool
        """
        if provider == "ollama":
            return {"source": "local", "key_preview": None, "available": True}

        env_var = PROVIDER_ENV_VARS.get(provider)
        env_val = os.environ.get(env_var) if env_var else None
        stored_val = self._data.get(provider)

        if env_val:
            return {
                "source": "env",
                "key_preview": _mask(env_val),
                "available": True,
            }
        if stored_val:
            return {
                "source": "stored",
                "key_preview": _mask(stored_val),
                "available": True,
            }
        return {"source": "none", "key_preview": None, "available": False}

    def get_all_statuses(self) -> Dict[str, Dict]:
        """Return status dicts for every known provider."""
        return {p: self.get_status(p) for p in PROVIDER_INFO}

    def set_default_model(self, provider: str, model: str) -> None:
        """Persist a preferred model for a provider."""
        model_key = f"_model_{provider}"
        self._data[model_key] = model
        self._save()

    def get_default_model(self, provider: str) -> Optional[str]:
        """Return the user-preferred model or None."""
        return self._data.get(f"_model_{provider}")


def _mask(key: str) -> str:
    """Mask an API key showing only the first 8 chars."""
    if not key:
        return ""
    visible = key[:8]
    return f"{visible}{'*' * min(len(key) - 8, 24)}"


# Module-level singleton
key_manager = KeyManager()
