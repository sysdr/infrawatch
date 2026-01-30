from minio import Minio
from config.settings import settings
import gzip
import hashlib
import json
from datetime import datetime
import io
try:
    import lz4.frame as lz4_frame
except ImportError:
    lz4_frame = None

class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        self._ensure_buckets()
    
    def _ensure_buckets(self):
        for bucket in [settings.MINIO_BUCKET_HOT, settings.MINIO_BUCKET_WARM, settings.MINIO_BUCKET_COLD]:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
    
    def compress_data(self, data: str, algorithm: str = "gzip") -> bytes:
        data_bytes = data.encode('utf-8')
        if algorithm == "gzip":
            return gzip.compress(data_bytes, compresslevel=9)
        elif algorithm == "lz4" and lz4_frame:
            return lz4_frame.compress(data_bytes)
        return data_bytes
    
    def decompress_data(self, data: bytes, algorithm: str = "gzip") -> str:
        if algorithm == "gzip":
            return gzip.decompress(data).decode('utf-8')
        elif algorithm == "lz4" and lz4_frame:
            return lz4_frame.decompress(data).decode('utf-8')
        return data.decode('utf-8')
    
    def calculate_checksum(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    
    def upload_log(self, bucket: str, object_name: str, data: bytes) -> str:
        data_stream = io.BytesIO(data)
        self.client.put_object(
            bucket,
            object_name,
            data_stream,
            length=len(data)
        )
        return f"{bucket}/{object_name}"
    
    def download_log(self, bucket: str, object_name: str) -> bytes:
        response = self.client.get_object(bucket, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        return data
    
    def delete_log(self, bucket: str, object_name: str):
        self.client.remove_object(bucket, object_name)
    
    def get_bucket_for_tier(self, tier: str) -> str:
        tier_map = {
            "hot": settings.MINIO_BUCKET_HOT,
            "warm": settings.MINIO_BUCKET_WARM,
            "cold": settings.MINIO_BUCKET_COLD
        }
        return tier_map.get(tier, settings.MINIO_BUCKET_HOT)

storage_service = StorageService()
