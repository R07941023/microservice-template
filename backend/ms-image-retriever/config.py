"""Configuration settings for image retriever service."""

import os

# --- MinIO Connection ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minio")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minio")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "minio")

# --- Thread Pool Config ---
THREAD_POOL_SIZE = int(os.getenv("MINIO_THREAD_POOL_SIZE", "20"))
