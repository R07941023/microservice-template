"""Tests for auth module."""

import sys
import os
from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock config before importing auth
with patch.dict('sys.modules', {
    'utils.config': MagicMock(
        KEYCLOAK_REALM_URL="https://keycloak.example.com/realms/test",
        JWT_AUDIENCE=None,
        get_jwks_url=lambda: "https://keycloak.example.com/realms/test/protocol/openid-connect/certs"
    )
}):
    # Also need to mock the relative import
    import importlib
    import utils.auth
    importlib.reload(utils.auth)
    from utils.auth import (
        User,
        get_current_user,
        get_jwks_client,
        verify_keycloak_token,
        verify_jwt_from_header,
        _jwks_clients,
    )


class TestUserModel:
    """Tests for User model."""

    def test_user_with_all_fields(self):
        """Test creating User with all fields."""
        user = User(name="John Doe", email="john@example.com")
        assert user.name == "John Doe"
        assert user.email == "john@example.com"

    def test_user_with_optional_fields(self):
        """Test creating User with optional fields as None."""
        user = User()
        assert user.name is None
        assert user.email is None

    def test_user_with_partial_fields(self):
        """Test creating User with only name."""
        user = User(name="Jane")
        assert user.name == "Jane"
        assert user.email is None


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self):
        """Test that valid token returns User object."""
        token_data = {
            "name": "Test User",
            "email": "test@example.com",
            "preferred_username": "testuser",
        }

        with patch("utils.auth.verify_jwt_from_header") as mock_verify:
            mock_verify.return_value = token_data

            user = await get_current_user("Bearer valid.token")

            assert isinstance(user, User)
            assert user.name == "Test User"
            assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_valid_token_uses_preferred_username_fallback(self):
        """Test that preferred_username is used when name is missing."""
        token_data = {
            "preferred_username": "testuser",
            "email": "test@example.com",
        }

        with patch("utils.auth.verify_jwt_from_header") as mock_verify:
            mock_verify.return_value = token_data

            user = await get_current_user("Bearer valid.token")

            assert user.name == "testuser"
            assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        """Test that invalid token raises HTTPException 401."""
        with patch("utils.auth.verify_jwt_from_header") as mock_verify:
            mock_verify.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("Bearer invalid.token")

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid or missing token"

    @pytest.mark.asyncio
    async def test_missing_token_raises_401(self):
        """Test that missing token raises HTTPException 401."""
        with patch("utils.auth.verify_jwt_from_header") as mock_verify:
            mock_verify.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(None)

            assert exc_info.value.status_code == 401


class TestGetJwksClient:
    """Tests for get_jwks_client function."""

    def setup_method(self):
        """Clear cached clients before each test."""
        _jwks_clients.clear()

    def test_creates_new_client(self):
        """Test creating a new JWKS client."""
        jwks_url = "https://keycloak.example.com/realms/test/protocol/openid-connect/certs"

        with patch("utils.auth.PyJWKClient") as mock_client_class:
            mock_instance = MagicMock()
            mock_client_class.return_value = mock_instance

            client = get_jwks_client(jwks_url)

            mock_client_class.assert_called_once_with(
                jwks_url,
                headers={"User-Agent": "microservice/1.0"},
            )
            assert client == mock_instance

    def test_returns_cached_client(self):
        """Test that the same client is returned for the same URL."""
        jwks_url = "https://keycloak.example.com/realms/test/protocol/openid-connect/certs"

        with patch("utils.auth.PyJWKClient") as mock_client_class:
            mock_instance = MagicMock()
            mock_client_class.return_value = mock_instance

            client1 = get_jwks_client(jwks_url)
            client2 = get_jwks_client(jwks_url)

            assert mock_client_class.call_count == 1
            assert client1 is client2

    def test_different_urls_get_different_clients(self):
        """Test that different URLs get different clients."""
        url1 = "https://keycloak1.example.com/certs"
        url2 = "https://keycloak2.example.com/certs"

        with patch("utils.auth.PyJWKClient") as mock_client_class:
            mock_instance1 = MagicMock()
            mock_instance2 = MagicMock()
            mock_client_class.side_effect = [mock_instance1, mock_instance2]

            client1 = get_jwks_client(url1)
            client2 = get_jwks_client(url2)

            assert mock_client_class.call_count == 2
            assert client1 is not client2


class TestVerifyKeycloakToken:
    """Tests for verify_keycloak_token function."""

    def setup_method(self):
        """Clear cached clients before each test."""
        _jwks_clients.clear()

    def test_valid_token(self):
        """Test verifying a valid token."""
        token = "valid.jwt.token"
        jwks_url = "https://keycloak.example.com/certs"
        issuer = "https://keycloak.example.com/realms/test"
        expected_payload = {"sub": "user123", "preferred_username": "testuser"}

        with patch("utils.auth.get_jwks_client") as mock_get_client, \
             patch("utils.auth.jwt.decode") as mock_decode:
            mock_jwks_client = MagicMock()
            mock_signing_key = MagicMock()
            mock_signing_key.key = "test-key"
            mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key
            mock_get_client.return_value = mock_jwks_client
            mock_decode.return_value = expected_payload

            result = verify_keycloak_token(token, jwks_url, issuer)

            assert result == expected_payload
            mock_get_client.assert_called_once_with(jwks_url)
            mock_jwks_client.get_signing_key_from_jwt.assert_called_once_with(token)

    def test_valid_token_with_audience(self):
        """Test verifying a token with audience check."""
        token = "valid.jwt.token"
        jwks_url = "https://keycloak.example.com/certs"
        issuer = "https://keycloak.example.com/realms/test"
        audience = "my-client"
        expected_payload = {"sub": "user123", "aud": "my-client"}

        with patch("utils.auth.get_jwks_client") as mock_get_client, \
             patch("utils.auth.jwt.decode") as mock_decode:
            mock_jwks_client = MagicMock()
            mock_signing_key = MagicMock()
            mock_signing_key.key = "test-key"
            mock_jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key
            mock_get_client.return_value = mock_jwks_client
            mock_decode.return_value = expected_payload

            result = verify_keycloak_token(token, jwks_url, issuer, audience=audience)

            assert result == expected_payload
            mock_decode.assert_called_once()
            call_kwargs = mock_decode.call_args[1]
            assert call_kwargs["audience"] == audience
            assert call_kwargs["options"]["verify_aud"] is True


class TestVerifyJwtFromHeader:
    """Tests for verify_jwt_from_header function."""

    def setup_method(self):
        """Clear cached clients before each test."""
        _jwks_clients.clear()

    def test_valid_authorization_header(self):
        """Test with valid Authorization header."""
        authorization = "Bearer valid.jwt.token"
        jwks_url = "https://keycloak.example.com/certs"
        issuer = "https://keycloak.example.com/realms/test"
        expected_payload = {"sub": "user123"}

        with patch("utils.auth.verify_keycloak_token") as mock_verify:
            mock_verify.return_value = expected_payload

            result = verify_jwt_from_header(authorization, jwks_url, issuer)

            assert result == expected_payload
            mock_verify.assert_called_once_with("valid.jwt.token", jwks_url, issuer, None)

    def test_no_authorization_header(self):
        """Test with no authorization header."""
        result = verify_jwt_from_header(None, "https://example.com/certs", "https://example.com")

        assert result is None

    def test_empty_authorization_header(self):
        """Test with empty authorization header."""
        result = verify_jwt_from_header("", "https://example.com/certs", "https://example.com")

        assert result is None

    def test_invalid_bearer_format(self):
        """Test with invalid bearer format."""
        result = verify_jwt_from_header(
            "InvalidFormat token123",
            "https://example.com/certs",
            "https://example.com",
        )

        assert result is None

    def test_expired_token(self):
        """Test with expired token."""
        authorization = "Bearer expired.jwt.token"
        jwks_url = "https://keycloak.example.com/certs"
        issuer = "https://keycloak.example.com/realms/test"

        with patch("utils.auth.verify_keycloak_token") as mock_verify:
            mock_verify.side_effect = jwt.ExpiredSignatureError("Token expired")

            result = verify_jwt_from_header(authorization, jwks_url, issuer)

            assert result is None

    def test_invalid_issuer(self):
        """Test with invalid issuer."""
        authorization = "Bearer token.with.bad.issuer"
        jwks_url = "https://keycloak.example.com/certs"
        issuer = "https://keycloak.example.com/realms/test"

        with patch("utils.auth.verify_keycloak_token") as mock_verify:
            mock_verify.side_effect = jwt.InvalidIssuerError("Invalid issuer")

            result = verify_jwt_from_header(authorization, jwks_url, issuer)

            assert result is None

    def test_invalid_audience(self):
        """Test with invalid audience."""
        authorization = "Bearer token.with.bad.audience"
        jwks_url = "https://keycloak.example.com/certs"
        issuer = "https://keycloak.example.com/realms/test"
        audience = "expected-client"

        with patch("utils.auth.verify_keycloak_token") as mock_verify:
            mock_verify.side_effect = jwt.InvalidAudienceError("Invalid audience")

            result = verify_jwt_from_header(authorization, jwks_url, issuer, audience)

            assert result is None

    def test_generic_jwt_error(self):
        """Test with generic JWT error."""
        authorization = "Bearer invalid.token"
        jwks_url = "https://keycloak.example.com/certs"
        issuer = "https://keycloak.example.com/realms/test"

        with patch("utils.auth.verify_keycloak_token") as mock_verify:
            mock_verify.side_effect = jwt.PyJWTError("Some JWT error")

            result = verify_jwt_from_header(authorization, jwks_url, issuer)

            assert result is None
