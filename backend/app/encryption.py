"""
Encryption utilities for API keys
"""
from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


def get_encryption_key() -> bytes:
    """Generate encryption key from settings"""
    key = settings.ENCRYPTION_KEY.encode()
    # Use SHA256 to ensure 32 bytes
    key_hash = hashlib.sha256(key).digest()
    return base64.urlsafe_b64encode(key_hash)


_fernet = Fernet(get_encryption_key())


def encrypt_secret(secret: str) -> str:
    """Encrypt API key secret"""
    return _fernet.encrypt(secret.encode()).decode()


def decrypt_secret(encrypted: str) -> str:
    """Decrypt API key secret"""
    return _fernet.decrypt(encrypted.encode()).decode()

