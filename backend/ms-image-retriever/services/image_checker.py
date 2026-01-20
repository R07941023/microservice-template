import asyncio
import logging
from minio import Minio
from minio.error import S3Error
from models import ImageInfo, ImageExistence # Assuming models.py is in the parent directory

logger = logging.getLogger(__name__)

async def check_single_image(
    minio_client: Minio,
    bucket_name: str,
    image_info: ImageInfo
) -> ImageExistence:
    object_name = f"{image_info.type}/{image_info.id}.png"
    try:
        await asyncio.to_thread(minio_client.stat_object, bucket_name, object_name)
        return ImageExistence(type=image_info.type, id=image_info.id, image_exist=True)
    except S3Error as exc:
        if exc.code == "NoSuchKey":
            return ImageExistence(type=image_info.type, id=image_info.id, image_exist=False)
        else:
            logger.error(f"S3Error checking for object {object_name}: {exc}")
            return ImageExistence(type=image_info.type, id=image_info.id, image_exist=False)
    except Exception as e:
        logger.error(f"An unexpected error occurred while checking for object {object_name}: {e}")
        return ImageExistence(type=image_info.type, id=image_info.id, image_exist=False)
