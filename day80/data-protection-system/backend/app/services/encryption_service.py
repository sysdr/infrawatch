from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
import base64
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EncryptionService:
    def __init__(self):
        self.master_key = None
        self.dek_cache = {}
        self.key_version = "v1"
    
    async def initialize(self):
        """Initialize encryption service with master key"""
        # In production, fetch from KMS (AWS KMS, HashiCorp Vault, etc.)
        master_key_str = os.getenv("MASTER_KEY", "default-key-change-in-production-32-bytes-minimum-required")
        # Ensure master key is exactly 32 bytes
        master_key_bytes = master_key_str.encode()[:32]
        if len(master_key_bytes) < 32:
            master_key_bytes = master_key_bytes.ljust(32, b'0')
        self.master_key = master_key_bytes
        logger.info("Encryption service initialized with master key")
    
    def derive_dek(self, context: str) -> bytes:
        """Derive data encryption key from master key using HKDF"""
        cache_key = f"{self.key_version}:{context}"
        
        if cache_key in self.dek_cache:
            return self.dek_cache[cache_key]
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=context.encode(),
            backend=default_backend()
        )
        dek = hkdf.derive(self.master_key)
        
        # Cache DEK for performance
        self.dek_cache[cache_key] = dek
        return dek
    
    def encrypt(self, plaintext: str, context: str = "default") -> dict:
        """Encrypt data using AES-256-GCM with context-specific DEK"""
        if not plaintext:
            return {"ciphertext": None, "nonce": None, "tag": None}
        
        try:
            # Derive DEK for this context
            dek = self.derive_dek(context)
            
            # Generate random nonce
            nonce = os.urandom(12)
            
            # Encrypt with AES-256-GCM
            aesgcm = AESGCM(dek)
            ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
            
            return {
                "ciphertext": base64.b64encode(ciphertext).decode(),
                "nonce": base64.b64encode(nonce).decode(),
                "version": self.key_version,
                "context": context
            }
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_data: dict) -> str:
        """Decrypt data using stored nonce and context"""
        if not encrypted_data or not encrypted_data.get("ciphertext"):
            return None
        
        try:
            # Derive same DEK using stored context
            context = encrypted_data.get("context", "default")
            dek = self.derive_dek(context)
            
            # Decode from base64
            ciphertext = base64.b64decode(encrypted_data["ciphertext"])
            nonce = base64.b64decode(encrypted_data["nonce"])
            
            # Decrypt
            aesgcm = AESGCM(dek)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    def rotate_keys(self):
        """Rotate to new key version"""
        # In production, this would:
        # 1. Generate new master key
        # 2. Re-encrypt all DEKs with new master
        # 3. Update key_version
        # 4. Gradually re-encrypt data
        old_version = self.key_version
        self.key_version = f"v{int(old_version[1:]) + 1}"
        self.dek_cache.clear()
        logger.info(f"Keys rotated from {old_version} to {self.key_version}")
        return {"old_version": old_version, "new_version": self.key_version}

# Global instance
encryption_service = EncryptionService()
