"""Configuration settings for TUKUB AI"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Global settings manager — reads from env vars, key manager, and YAML."""

    # Paths
    BASE_DIR = Path.home() / ".tukub"
    CONFIG_DIR = BASE_DIR / "config"
    LOGS_DIR = BASE_DIR / "logs"
    REPORTS_DIR = BASE_DIR / "reports"
    TOOLS_DIR = BASE_DIR / "tools"

    # API Keys (env var lookup — key_manager is the canonical source at runtime)
    OPENROUTER_API_KEY: Optional[str] = os.environ.get("OPENROUTER_API_KEY")
    GROQ_API_KEY: Optional[str] = os.environ.get("GROQ_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.environ.get("ANTHROPIC_API_KEY")
    NVIDIA_API_KEY: Optional[str] = os.environ.get("NVIDIA_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = os.environ.get("HUGGINGFACE_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.environ.get("GOOGLE_API_KEY")
    COHERE_API_KEY: Optional[str] = os.environ.get("COHERE_API_KEY")
    MISTRAL_API_KEY: Optional[str] = os.environ.get("MISTRAL_API_KEY")
    TOGETHER_API_KEY: Optional[str] = os.environ.get("TOGETHER_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = os.environ.get("DEEPSEEK_API_KEY")
    PERPLEXITY_API_KEY: Optional[str] = os.environ.get("PERPLEXITY_API_KEY")

    # Default settings
    DEFAULT_MODEL: str = "llama3.2"
    DEFAULT_JAILBREAK: str = "pentester_mode"
    MAX_ITERATIONS: int = 20
    TOOL_TIMEOUT: int = 300

    @classmethod
    def ensure_dirs(cls):
        """Create necessary directories."""
        for dir_path in [cls.BASE_DIR, cls.CONFIG_DIR, cls.LOGS_DIR,
                         cls.REPORTS_DIR, cls.TOOLS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """
        Resolve API key with priority:
            1. Environment variable
            2. Key stored via key_manager (config set)
            3. None
        """
        from config.key_manager import key_manager
        return key_manager.resolve_key(provider)

    @classmethod
    def get_provider_config(cls, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider."""
        from config.key_manager import key_manager, PROVIDER_INFO

        info = PROVIDER_INFO.get(provider, {})
        api_key = cls.get_api_key(provider)
        model = (
            key_manager.get_default_model(provider)
            or info.get("default_model")
        )

        configs = {
            "ollama": {
                "url": "http://localhost:11434",
                "default_model": model or "llama3.2",
            },
            "groq": {"api_key": api_key, "default_model": model or "llama3-70b-8192"},
            "openrouter": {
                "api_key": api_key,
                "default_model": model or "google/gemini-2.0-flash-exp:free",
            },
            "nvidia": {
                "api_key": api_key,
                "default_model": model or "nvidia/nemotron-3-ultra-550b-a55b",
            },
            "huggingface": {
                "api_key": api_key,
                "default_model": model or "mistralai/Mistral-7B-Instruct-v0.2",
            },
            "openai": {"api_key": api_key, "default_model": model or "gpt-4o"},
            "anthropic": {
                "api_key": api_key,
                "default_model": model or "claude-3-sonnet-20240229",
            },
        }
        return configs.get(provider, {})


settings = Settings()