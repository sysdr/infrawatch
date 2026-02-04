import boto3
import os

_s3_client = None

async def get_s3_client():
    """Get S3 client singleton (mock for local development)"""
    global _s3_client

    if _s3_client is None:
        _s3_client = MockS3Client()

    return _s3_client

class MockS3Client:
    """Mock S3 client for local development"""

    async def upload_file(self, filename, bucket, key):
        print(f"[MOCK] Uploaded {filename} to s3://{bucket}/{key}")

    async def download_file(self, bucket, key, filename):
        print(f"[MOCK] Downloaded s3://{bucket}/{key} to {filename}")
