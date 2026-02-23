from pydantic import BaseModel, Field
from typing import Any, Optional
class CacheSetRequest(BaseModel): key: str; value: Any; ttl: int = 300; tags: list[str] = []; strategy: str = "ttl"
class InvalidateTagRequest(BaseModel): tag: str
class InvalidateKeyRequest(BaseModel): key: str
