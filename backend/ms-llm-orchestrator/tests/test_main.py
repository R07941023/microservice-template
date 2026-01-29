import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestStreamChat:
    """Tests for /stream-chat endpoint."""

    def test_stream_chat_without_agent(self, client, sample_chat_request, valid_jwt_token):
        """Test stream chat returns error when agent not initialized."""
        with patch("main.app_state") as mock_state:
            mock_state.langchain_agent = None

            response = client.post(
                "/stream-chat",
                json=sample_chat_request,
                headers={"Authorization": valid_jwt_token}
            )

            assert response.status_code == 200
            data = response.json()
            assert "error" in data

    def test_stream_chat_success(self, client, sample_chat_request, valid_jwt_token, mock_langchain_agent):
        """Test successful stream chat."""
        async def mock_astream(*args, **kwargs):
            class MockMessage:
                content = "Hello!"
            yield MockMessage(), {"langgraph_node": "model"}

        mock_langchain_agent.astream = mock_astream

        with patch("main.app_state") as mock_state:
            mock_state.langchain_agent = mock_langchain_agent
            mock_state.langfuse_handler = MagicMock()

            response = client.post(
                "/stream-chat",
                json=sample_chat_request,
                headers={"Authorization": valid_jwt_token}
            )

            assert response.status_code == 200

    def test_stream_chat_without_auth(self, client, sample_chat_request, mock_langchain_agent):
        """Test stream chat without authorization header."""
        with patch("main.app_state") as mock_state:
            mock_state.langchain_agent = mock_langchain_agent
            mock_state.langfuse_handler = MagicMock()

            response = client.post("/stream-chat", json=sample_chat_request)

            # Should still work, but user will be None
            assert response.status_code == 200

    def test_stream_chat_missing_prompt(self, client, valid_jwt_token, mock_langchain_agent):
        """Test stream chat with missing prompt."""
        with patch("main.app_state") as mock_state:
            mock_state.langchain_agent = mock_langchain_agent

            response = client.post(
                "/stream-chat",
                json={"model": "gemini"},
                headers={"Authorization": valid_jwt_token}
            )

            assert response.status_code == 422

    def test_stream_chat_default_model(self, client, valid_jwt_token, mock_langchain_agent):
        """Test stream chat uses default model when not specified."""
        async def mock_astream(*args, **kwargs):
            class MockMessage:
                content = "Response"
            yield MockMessage(), {"langgraph_node": "model"}

        mock_langchain_agent.astream = mock_astream

        with patch("main.app_state") as mock_state:
            mock_state.langchain_agent = mock_langchain_agent
            mock_state.langfuse_handler = MagicMock()

            response = client.post(
                "/stream-chat",
                json={"prompt": "Hello"},
                headers={"Authorization": valid_jwt_token}
            )

            assert response.status_code == 200


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    def test_get_current_user_with_valid_token(self, valid_jwt_token):
        """Test extracting user from valid JWT."""
        from utils.auth import get_current_user
        import asyncio

        # Mock the JWT verification to return decoded token data
        with patch("utils.auth.verify_jwt_from_header") as mock_verify:
            mock_verify.return_value = {
                "name": "Test User",
                "email": "test@example.com"
            }

            user = asyncio.run(get_current_user(valid_jwt_token))

            assert user.name == "Test User"
            assert user.email == "test@example.com"

    def test_get_current_user_without_token(self):
        """Test user extraction without token raises 401."""
        from utils.auth import get_current_user
        from fastapi import HTTPException
        import asyncio

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(get_current_user(None))

        assert exc_info.value.status_code == 401
