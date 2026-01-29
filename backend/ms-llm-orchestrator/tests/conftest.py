import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def mock_get_current_user():
    """Mock user for testing."""
    from utils.auth import User
    return User(name="testuser", email="test@example.com")


@pytest.fixture
def mock_langchain_agent():
    """Create a mock LangChain agent."""
    agent = MagicMock()
    return agent


@pytest.fixture
def mock_langfuse_handler():
    """Create a mock Langfuse handler."""
    return MagicMock()


@pytest.fixture
def client(mock_langchain_agent, mock_langfuse_handler):
    """Create a FastAPI test client with mocked dependencies."""
    with patch.dict(os.environ, {
        "MCP_TOKEN": "test_token",
        "MCP_HOST": "http://mock-mcp:8000",
        "LITELLM_HOST": "http://mock-litellm:8000"
    }):
        # Mock MCP client to prevent actual network connections
        with patch("main.MultiServerMCPClient") as mock_mcp:
            mock_mcp_instance = AsyncMock()
            mock_mcp_instance.get_tools = AsyncMock(return_value=[])
            mock_mcp.return_value = mock_mcp_instance

            # Mock Langfuse handler
            with patch("main.CallbackHandler", return_value=mock_langfuse_handler):
                # Mock ChatOpenAI and create_agent
                with patch("main.ChatOpenAI"):
                    with patch("main.create_agent", return_value=mock_langchain_agent):
                        from main import app
                        from utils.auth import get_current_user

                        app.dependency_overrides[get_current_user] = mock_get_current_user

                        with TestClient(app, raise_server_exceptions=False) as test_client:
                            yield test_client

                        app.dependency_overrides.clear()


@pytest.fixture
def valid_jwt_token():
    """Create a valid JWT token for testing."""
    import jwt
    payload = {"name": "Test User", "email": "test@example.com"}
    return "Bearer " + jwt.encode(payload, "secret", algorithm="HS256")


@pytest.fixture
def sample_chat_request():
    """Sample chat request data."""
    return {
        "prompt": "Hello, how are you?",
        "model": "gemini"
    }
