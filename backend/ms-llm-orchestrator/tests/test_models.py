import pytest
from pydantic import ValidationError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import ChatRequest
from utils.auth import User


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
        request = ChatRequest(prompt="Hello", session_id="abc-123")
        assert request.prompt == "Hello"
        assert request.session_id == "abc-123"

    def test_chat_request_default_history(self):
        request = ChatRequest(prompt="Hello", session_id="abc-123")
        assert request.history == []

    def test_chat_request_missing_prompt(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id="abc-123")

    def test_chat_request_missing_session_id(self):
        with pytest.raises(ValidationError):
            ChatRequest(prompt="Hello")
