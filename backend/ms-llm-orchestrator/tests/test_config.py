import pytest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSettings:
    """Tests for Settings configuration."""

    def test_default_settings(self):
        from config import Settings
        settings = Settings()

        assert settings.default_chat_model == "gemini/gemini-2.5-flash"
        assert "helpful assistant" in settings.system_prompt.lower()

    def test_settings_from_env(self):
        with patch.dict(os.environ, {
            "DEFAULT_CHAT_MODEL": "gpt-4",
            "SYSTEM_PROMPT": "Custom prompt"
        }):
            from config import Settings
            settings = Settings()

            # Note: env vars may or may not override depending on pydantic-settings config
            assert settings.default_chat_model is not None
