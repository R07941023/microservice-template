"""Authentication utilities for JWT handling with Keycloak."""

import logging
from typing import Any, Dict, Optional

import jwt
from jwt import PyJWKClient

logger = logging.getLogger(__name__)

# Cache for JWKS client per URL
_jwks_clients: Dict[str, PyJWKClient] = {}


def get_jwks_client(jwks_url: str) -> PyJWKClient:
    """
    Get or create a cached JWKS client with proper headers.

    Args:
        jwks_url: URL to the JWKS endpoint.

    Returns:
        PyJWKClient instance for fetching public keys.
    """
    if jwks_url not in _jwks_clients:
        _jwks_clients[jwks_url] = PyJWKClient(
            jwks_url,
            headers={"User-Agent": "microservice/1.0"},
        )
    return _jwks_clients[jwks_url]


def verify_keycloak_token(
    token: str,
    jwks_url: str,
    issuer: str,
    audience: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Verify and decode a Keycloak JWT token.

    Args:
        token: The JWT token string (without Bearer prefix).
        jwks_url: URL to Keycloak's JWKS endpoint.
        issuer: Expected issuer (Keycloak realm URL).
        audience: Expected audience claim (optional).

    Returns:
        Decoded token payload as dictionary.

    Raises:
        jwt.InvalidTokenError: If token validation fails.
    """
    jwks_client = get_jwks_client(jwks_url)
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    options = {
        "verify_signature": True,
        "verify_exp": True,
        "verify_iss": True,
        "verify_aud": audience is not None,
    }

    decoded = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer=issuer,
        audience=audience,
        options=options,
    )

    logger.info("JWT verified successfully for user: %s", decoded.get("preferred_username"))
    return decoded


def verify_jwt_from_header(
    authorization: Optional[str],
    jwks_url: str,
    issuer: str,
    audience: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Verify JWT from Authorization header.

    Args:
        authorization: The Authorization header value (e.g., "Bearer <token>").
        jwks_url: URL to Keycloak's JWKS endpoint.
        issuer: Expected issuer (Keycloak realm URL).
        audience: Expected audience claim (optional).

    Returns:
        Decoded token payload or None if validation fails.
    """
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header")
        return None

    token = authorization.split(" ", 1)[1]

    try:
        return verify_keycloak_token(token, jwks_url, issuer, audience)
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidIssuerError:
        logger.warning("JWT token has invalid issuer")
        return None
    except jwt.InvalidAudienceError:
        logger.warning("JWT token has invalid audience")
        return None
    except jwt.PyJWTError as e:
        logger.error("JWT verification failed: %s", e)
        return None
