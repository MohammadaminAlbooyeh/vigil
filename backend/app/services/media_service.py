# Sentinel-X Media Service
# Stores media (images, videos) using MinIO

import io
import os
import time
import uuid
from typing import Optional, BinaryIO
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False

class MediaService:
    """Service for storing surveillance media in MinIO."""

    def __init__(self, endpoint: str = "localhost:9000",
                 access_key: str = "sentinel",
                 secret_key: str = "sentinel123",
                 bucket: str = "sentinel-x-media"):
        self.bucket = bucket
        self.endpoint = endpoint

        if MINIO_AVAILABLE:
            self.client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=False
            )
            self._ensure_bucket()
        else:
            self.client = None
            logger.warning("MinIO not available, using local storage")

    def _ensure_bucket(self):
        """Ensure the bucket exists."""
        if not self.client:
            return
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Created bucket: {self.bucket}")
        except S3Error as e:
            logger.error(f"Bucket error: {e}")

    def store_image(self, image_data: bytes, device_id: str,
                    event_type: str = "detection") -> Optional[str]:
        """Store an image in MinIO."""
        filename = f"{device_id}/{event_type}/{uuid.uuid4().hex}.jpg"
        return self._store_object(filename, image_data, "image/jpeg")

    def store_video(self, video_data: bytes, device_id: str,
                    event_type: str = "recording") -> Optional[str]:
        """Store a video in MinIO."""
        filename = f"{device_id}/{event_type}/{uuid.uuid4().hex}.mp4"
        return self._store_object(filename, video_data, "video/mp4")

    def _store_object(self, object_name: str, data: bytes,
                      content_type: str) -> Optional[str]:
        """Store an object in MinIO."""
        if self.client:
            try:
                self.client.put_object(
                    self.bucket,
                    object_name,
                    io.BytesIO(data),
                    length=len(data),
                    content_type=content_type
                )
                return f"{self.bucket}/{object_name}"
            except S3Error as e:
                logger.error(f"MinIO upload error: {e}")
                return None
        else:
            # Fallback to local storage
            local_path = f"/var/sentinel-x/media/{object_name}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(data)
            return local_path

    def get_presigned_url(self, object_name: str, expires_seconds: int = 3600) -> Optional[str]:
        """Get a presigned URL for an object."""
        if self.client:
            try:
                return self.client.presigned_get_object(
                    self.bucket, object_name, expires=expires_seconds
                )
            except S3Error as e:
                logger.error(f"Presigned URL error: {e}")
                return None
        return None