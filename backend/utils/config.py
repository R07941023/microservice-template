"""Shared configuration settings for microservices."""

import os

# --- Redis Cache Config ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_EXPIRATION_SECONDS", "3600"))
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

# --- Keycloak JWT Config ---
KEYCLOAK_REALM_URL = os.getenv(
    "KEYCLOAK_REALM_URL",
    "https://keycloak.mydormroom.dpdns.org/realms/master"
)
KEYCLOAK_JWKS_URL = os.getenv("KEYCLOAK_JWKS_URL")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE")


def get_jwks_url() -> str:
    """Get JWKS URL, defaulting to Keycloak's standard endpoint."""
    if KEYCLOAK_JWKS_URL:
        return KEYCLOAK_JWKS_URL
    return f"{KEYCLOAK_REALM_URL}/protocol/openid-connect/certs"
