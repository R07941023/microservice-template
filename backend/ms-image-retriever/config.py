"""Configuration settings for image retriever service."""

import os


# --- MinIO Connection ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minio")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minio")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "minio")

# --- Redis Cache Config ---
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_EXPIRATION_SECONDS", "3600"))
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

# --- Thread Pool Config ---
THREAD_POOL_SIZE = int(os.getenv("MINIO_THREAD_POOL_SIZE", "20"))
