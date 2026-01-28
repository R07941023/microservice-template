"""Shared configuration settings for microservices."""

import os

# --- Redis Cache Config ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_EXPIRATION_SECONDS", "3600"))
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
