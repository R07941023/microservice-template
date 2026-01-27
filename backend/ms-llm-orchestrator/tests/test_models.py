import pytest
from pydantic import ValidationError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User, ChatRequest


class TestUser:
    """Tests for User model."""

    def test_valid_user(self):
        user = User(name="Test User", email="test@example.com")
        assert user.name == "Test User"
        assert user.email == "test@example.com"

    def test_user_missing_name(self):
        """User without name should use default None."""
        user = User(email="test@example.com")
        assert user.name is None
        assert user.email == "test@example.com"

    def test_user_missing_email(self):
        """User without email should use default None."""
        user = User(name="Test User")
        assert user.name == "Test User"
        assert user.email is None

    def test_user_empty(self):
        """User without any fields should use defaults."""
        user = User()
        assert user.name is None
        assert user.email is None


class TestChatRequest:
    """Tests for ChatRequest model."""

    def test_valid_chat_request(self):
        request = ChatRequest(prompt="Hello", model="gemini")
        assert request.prompt == "Hello"
        assert request.model == "gemini"

    def test_chat_request_default_model(self):
        request = ChatRequest(prompt="Hello")
        assert request.model == "gemini"

    def test_chat_request_missing_prompt(self):
        with pytest.raises(ValidationError):
            ChatRequest(model="gemini")

    def test_chat_request_custom_model(self):
        request = ChatRequest(prompt="Hello", model="gpt-4")
        assert request.model == "gpt-4"
