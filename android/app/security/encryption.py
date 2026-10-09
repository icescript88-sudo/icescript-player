"""
Mobile Video Decryption and Streaming Manager.
Uses AES-256-CTR with PBKDF2 key derivation.
Supports direct ephemeral decryption and chunked memory processing for mobile devices.
"""
import atexit
import hashlib
import os
import secrets
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from app.config import DATA_DIR
from app.security.device_binding import AndroidDeviceBinding

MAGIC_HEADER = b"PCVID01"
HEADER_SALT_LEN = 16
HEADER_IV_LEN = 16
CHUNK_SIZE = 64 * 1024  # 64 KB streaming buffer


class AndroidEncryptionManager:
    """Handles mobile file decryption to cache and memory-efficient cleanup."""

    def __init__(self, db=None, cache_dir: Optional[Path] = None, device_binding: Optional[AndroidDeviceBinding] = None):
        self.db = db
        self.device_binding = device_binding or AndroidDeviceBinding(db)
        self.cache_dir = cache_dir or (DATA_DIR / ".cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._active_temp_files = set()

        self.cleanup_all_temp_files()
        atexit.register(self.cleanup_all_temp_files)

    def get_or_create_master_key(self) -> bytes:
        """Retrieve master encryption secret from vault."""
        from app.security.vault import get_vault_key
        master_key = get_vault_key()

        if self.db:
            key_hex = self.db.get_setting("master_encryption_key")
            if not key_hex or key_hex != master_key.hex():
                self.db.set_setting("master_encryption_key", master_key.hex())

        return master_key

    def _derive_key(self, master_key: bytes, salt: bytes) -> bytes:
        """Derive standard 256-bit AES key using PBKDF2-HMAC-SHA256 from per-file salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=50_000,
        )
        return kdf.derive(master_key)

    @staticmethod
    def _is_valid_header(data: bytes, ext: str) -> bool:
        """Check if decrypted bytes match expected file container headers."""
        ext_lower = ext.lower()
        if ext_lower in (".mp4", ".mov", ".m4v"):
            return len(data) >= 8 and (
                data[4:8] in (b"ftyp", b"moov", b"wide", b"free", b"mdat")
                or data[0] == 0x47
            )
        elif ext_lower in (".pdf",):
            return data.startswith(b"%PDF-")
        elif ext_lower in (".mkv", ".webm"):
            return data.startswith(b"\x1a\x45\xdf\xa3")
        elif ext_lower in (".avi",):
            return data.startswith(b"RIFF")
        return len(data) >= 4

    @staticmethod
    def is_encrypted_file(file_path: Path) -> bool:
        """Check if file starts with the Player Cripto magic bytes."""
        if not file_path.exists() or file_path.stat().st_size < len(MAGIC_HEADER):
            return False
        try:
            with open(file_path, "rb") as f:
                header = f.read(len(MAGIC_HEADER))
                return header == MAGIC_HEADER
        except Exception:
            return False

    def decrypt_to_cache(self, encrypted_path: Path) -> Path:
        """Decrypt protected video to an ephemeral cache file for local playback."""
        encrypted_path = Path(encrypted_path)
        if not encrypted_path.exists():
            raise FileNotFoundError(f"File not found: {encrypted_path}")

        master_key = self.get_or_create_master_key()

        with open(encrypted_path, "rb") as src:
            magic = src.read(len(MAGIC_HEADER))
            if magic != MAGIC_HEADER:
                raise ValueError("Not a valid Player Cripto protected video.")

            salt = src.read(HEADER_SALT_LEN)
            iv = src.read(HEADER_IV_LEN)
            ext_len = int.from_bytes(src.read(1), "big")
            ext_bytes = src.read(ext_len)
            orig_ext = ext_bytes.decode("utf-8", errors="ignore") or ".mp4"
            payload_start_offset = src.tell()

            derived_key = self._derive_key(master_key, salt)
            src.seek(payload_start_offset)
            cipher = Cipher(algorithms.AES(derived_key), modes.CTR(iv))
            decryptor = cipher.decryptor()

            random_token = secrets.token_hex(12)
            temp_file = self.cache_dir / f"sess_{random_token}{orig_ext}"

            with open(temp_file, "wb") as dst:
                while True:
                    chunk = src.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    dst.write(decryptor.update(chunk))
                dst.write(decryptor.finalize())

        self._active_temp_files.add(str(temp_file))
        return temp_file

    def remove_cache_file(self, file_path: Path):
        """Securely wipe and delete a specific temporary playback file."""
        try:
            p = Path(file_path)
            if p.exists() and p.is_file():
                try:
                    with open(p, "r+b") as f:
                        f.write(b"\x00" * min(65536, p.stat().st_size))
                except Exception:
                    pass
                p.unlink(missing_ok=True)
            self._active_temp_files.discard(str(p))
        except Exception:
            pass

    def cleanup_all_temp_files(self):
        """Purge all ephemeral files in the cache folder."""
        try:
            if self.cache_dir.exists():
                for item in self.cache_dir.iterdir():
                    if item.is_file():
                        try:
                            item.unlink(missing_ok=True)
                        except Exception:
                            pass
            self._active_temp_files.clear()
        except Exception:
            pass
