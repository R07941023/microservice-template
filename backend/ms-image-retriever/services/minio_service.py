"""MinIO service for image storage operations."""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from minio import Minio
from minio.error import S3Error

from config import (
    MINIO_ENDPOINT,
    MINIO_ROOT_USER,
    MINIO_ROOT_PASSWORD,
    THREAD_POOL_SIZE,
)

logger = logging.getLogger(__name__)

# MinIO client instance
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False
)

# Thread pool for sync MinIO operations
executor = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)


def _fetch_object(bucket: str, object_name: str) -> bytes:
    """
    Fetch object from MinIO storage (sync operation).

    Args:
        bucket: MinIO bucket name.
        object_name: Object path in bucket.

    Returns:
        Object data as bytes.

    Raises:
        S3Error: If object not found or MinIO error.
    """
    response = None
    try:
        response = minio_client.get_object(bucket, object_name)
        return response.read()
    finally:
        if response:
            response.close()
            response.release_conn()


def _check_bucket_exists(bucket: str) -> bool:
    """
    Check if MinIO bucket exists (sync operation).

    Args:
        bucket: MinIO bucket name.

    Returns:
        True if bucket exists.

    Raises:
        S3Error: If MinIO connection error.
    """
    return minio_client.bucket_exists(bucket)


def _check_object_exists(bucket: str, object_name: str) -> bool:
    """
    Check if object exists in MinIO (sync operation).

    Args:
        bucket: MinIO bucket name.
        object_name: Object path in bucket.

    Returns:
        True if object exists.
    """
    try:
        minio_client.stat_object(bucket, object_name)
        return True
    except S3Error:
        return False


async def fetch_image(bucket: str, object_name: str) -> bytes:
    """
    Fetch image from MinIO asynchronously.

    Args:
        bucket: MinIO bucket name.
        object_name: Object path in bucket.

    Returns:
        Image data as bytes.

    Raises:
        S3Error: If object not found or MinIO error.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        partial(_fetch_object, bucket, object_name)
    )


async def check_bucket_exists(bucket: str) -> bool:
    """
    Check if MinIO bucket exists asynchronously.

    Args:
        bucket: MinIO bucket name.

    Returns:
        True if bucket exists.

    Raises:
        S3Error: If MinIO connection error.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        partial(_check_bucket_exists, bucket)
    )


async def check_object_exists(bucket: str, object_name: str) -> bool:
    """
    Check if object exists in MinIO asynchronously.

    Args:
        bucket: MinIO bucket name.
        object_name: Object path in bucket.

    Returns:
        True if object exists.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        partial(_check_object_exists, bucket, object_name)
    )


def shutdown() -> None:
    """Shutdown the thread pool executor."""
    executor.shutdown(wait=True)
    logger.info("MinIO thread pool shut down")
