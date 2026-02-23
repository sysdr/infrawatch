"""Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional, Any

class CacheSetRequest(BaseModel):
    key: str
    value: Any
    ttl: int = 300
    tags: list[str] = []
    strategy: str = "ttl"

class InvalidateTagRequest(BaseModel):
    tag: str

class InvalidateKeyRequest(BaseModel):
    key: str
