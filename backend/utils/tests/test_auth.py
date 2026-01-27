import pytest
import jwt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import decode_jwt_from_header


class TestDecodeJwtFromHeader:
    """Tests for decode_jwt_from_header function."""

    def test_valid_jwt_token(self):
        """Test decoding valid JWT token."""
        payload = {"name": "Test User", "email": "test@example.com"}
        token = jwt.encode(payload, "secret", algorithm="HS256")
        authorization = f"Bearer {token}"

        name, email = decode_jwt_from_header(authorization)

        assert name == "Test User"
        assert email == "test@example.com"

    def test_no_authorization_header(self):
        """Test with no authorization header."""
        name, email = decode_jwt_from_header(None)

        assert name is None
        assert email is None

    def test_empty_authorization_header(self):
        """Test with empty authorization header."""
        name, email = decode_jwt_from_header("")

        assert name is None
        assert email is None

    def test_invalid_bearer_format(self):
        """Test with invalid bearer format."""
        name, email = decode_jwt_from_header("InvalidFormat token123")

        assert name is None
        assert email is None

    def test_missing_bearer_prefix(self):
        """Test with missing Bearer prefix."""
        payload = {"name": "Test User", "email": "test@example.com"}
        token = jwt.encode(payload, "secret", algorithm="HS256")

        name, email = decode_jwt_from_header(token)

        assert name is None
        assert email is None

    def test_invalid_jwt_token(self):
        """Test with invalid JWT token."""
        name, email = decode_jwt_from_header("Bearer invalid.token.here")

        assert name is None
        assert email is None

    def test_jwt_missing_claims(self):
        """Test JWT missing name and email claims."""
        payload = {"sub": "user123"}
        token = jwt.encode(payload, "secret", algorithm="HS256")
        authorization = f"Bearer {token}"

        name, email = decode_jwt_from_header(authorization)

        assert name is None
        assert email is None

    def test_jwt_partial_claims(self):
        """Test JWT with only name claim."""
        payload = {"name": "Test User"}
        token = jwt.encode(payload, "secret", algorithm="HS256")
        authorization = f"Bearer {token}"

        name, email = decode_jwt_from_header(authorization)

        assert name == "Test User"
        assert email is None

    def test_jwt_only_email(self):
        """Test JWT with only email claim."""
        payload = {"email": "test@example.com"}
        token = jwt.encode(payload, "secret", algorithm="HS256")
        authorization = f"Bearer {token}"

        name, email = decode_jwt_from_header(authorization)

        assert name is None
        assert email == "test@example.com"
