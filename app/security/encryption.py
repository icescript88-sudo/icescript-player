"""
Video encryption and decryption manager.
Uses AES-256-CTR with PBKDF2 key derivation.
Streamed in memory chunks (64 KB) to handle multi-gigabyte video files
without high memory usage.
"""
import atexit
import hashlib
import os
import secrets
import shutil
from pathlib import Path
from typing import Optional, Tuple

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from app.config import DATA_DIR
from app.security.device_binding import DeviceBinding

# Magic bytes identifying Player Cripto encrypted videos
MAGIC_HEADER = b"PCVID01"
HEADER_SALT_LEN = 16
HEADER_IV_LEN = 16
CHUNK_SIZE = 64 * 1024  # 64 KB streaming buffer


class EncryptionManager:
    """Handles file encryption, decryption to ephemeral cache, and secure cleanup."""

    def __init__(self, db=None, cache_dir: Optional[Path] = None, device_binding: Optional[DeviceBinding] = None):
        self.db = db
        self.device_binding = device_binding or DeviceBinding(db)
        self.cache_dir = cache_dir or (DATA_DIR / ".cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._active_temp_files = set()

        # Secure startup cleanup in case of previous unclean shutdown
        self.cleanup_all_temp_files()
        atexit.register(self.cleanup_all_temp_files)

    # ────────────────────────────────────────────
    #  Key Management
    # ────────────────────────────────────────────

    def get_or_create_master_key(self) -> bytes:
        """Retrieve master encryption secret from vault and sync to DB."""
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

    def _derive_key_legacy(self, master_key: bytes, salt: bytes) -> bytes:
        """Derive 256-bit AES key bound to local machine hardware hash (legacy format fallback)."""
        if self.device_binding:
            dev_hash = self.device_binding.get_device_hash()
            effective_salt = hashlib.sha256(salt + dev_hash).digest()
        else:
            effective_salt = salt

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=effective_salt,
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
                or data[0] == 0x47  # MPEG-TS sync byte
            )
        elif ext_lower in (".pdf",):
            return data.startswith(b"%PDF-")
        elif ext_lower in (".mkv", ".webm"):
            return data.startswith(b"\x1a\x45\xdf\xa3")
        elif ext_lower in (".avi",):
            return data.startswith(b"RIFF")
        return len(data) >= 4

    # ────────────────────────────────────────────
    #  Detection
    # ────────────────────────────────────────────

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

    # ────────────────────────────────────────────
    #  Encryption (Raw Video -> .cvid)
    # ────────────────────────────────────────────

    def encrypt_file(
        self,
        source_path: Path,
        dest_path: Optional[Path] = None,
        delete_original: bool = False,
    ) -> Path:
        """Encrypt a video file in streaming chunks into a protected .cvid container.

        Format:
        [MAGIC_HEADER (7B)] [SALT (16B)] [IV (16B)] [EXT_LEN (1B)] [EXT_BYTES] [CIPHERTEXT...]
        """
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        if dest_path is None:
            if source_path.suffix.lower() == ".pdf":
                dest_path = source_path.with_suffix(".cpdf")
            else:
                dest_path = source_path.with_suffix(".cvid")
        else:
            dest_path = Path(dest_path)

        master_key = self.get_or_create_master_key()
        salt = secrets.token_bytes(HEADER_SALT_LEN)
        iv = secrets.token_bytes(HEADER_IV_LEN)
        derived_key = self._derive_key(master_key, salt)

        cipher = Cipher(algorithms.AES(derived_key), modes.CTR(iv))
        encryptor = cipher.encryptor()

        # Preserve original extension so player knows codec on decryption
        ext_bytes = source_path.suffix.lower().encode("utf-8")
        if len(ext_bytes) > 255:
            ext_bytes = b".mp4"

        # Encrypt to a temporary file first, then atomic rename
        temp_dest = dest_path.with_suffix(".cvid.tmp")
        try:
            with open(source_path, "rb") as src, open(temp_dest, "wb") as dst:
                # Write header
                dst.write(MAGIC_HEADER)
                dst.write(salt)
                dst.write(iv)
                dst.write(len(ext_bytes).to_bytes(1, "big"))
                dst.write(ext_bytes)

                # Stream and encrypt payload
                while True:
                    chunk = src.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    dst.write(encryptor.update(chunk))

                dst.write(encryptor.finalize())

            # Atomic replace
            if dest_path.exists():
                dest_path.unlink()
            temp_dest.rename(dest_path)

            if delete_original and source_path.exists() and source_path != dest_path:
                source_path.unlink()

            return dest_path

        finally:
            if temp_dest.exists():
                try:
                    temp_dest.unlink()
                except Exception:
                    pass

    # ────────────────────────────────────────────
    #  Decryption to Ephemeral Cache
    # ────────────────────────────────────────────

    def decrypt_to_cache(self, encrypted_path: Path) -> Path:
        """Decrypt protected video to an ephemeral cache file for local playback.
        Supports both standard universal format and legacy hardware-bound format.
        """
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

            # 1. First attempt: Standard universal derivation
            derived_key = self._derive_key(master_key, salt)
            test_cipher = Cipher(algorithms.AES(derived_key), modes.CTR(iv))
            test_chunk = src.read(min(CHUNK_SIZE, 4096))
            dec_test = test_cipher.decryptor().update(test_chunk)

            # Check if standard key produced valid file header
            if not self._is_valid_header(dec_test, orig_ext):
                # 2. Fallback attempt: Legacy hardware-bound derivation
                src.seek(payload_start_offset)
                derived_key_legacy = self._derive_key_legacy(master_key, salt)
                test_cipher_legacy = Cipher(algorithms.AES(derived_key_legacy), modes.CTR(iv))
                test_chunk_legacy = src.read(min(CHUNK_SIZE, 4096))
                dec_test_legacy = test_cipher_legacy.decryptor().update(test_chunk_legacy)
                if self._is_valid_header(dec_test_legacy, orig_ext):
                    derived_key = derived_key_legacy

            # Rewind to payload start and prepare active decryptor
            src.seek(payload_start_offset)
            cipher = Cipher(algorithms.AES(derived_key), modes.CTR(iv))
            decryptor = cipher.decryptor()

            # Random ephemeral name in .cache/
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

    # ────────────────────────────────────────────
    #  Ephemeral Cleanup
    # ────────────────────────────────────────────

    def remove_cache_file(self, file_path: Path):
        """Securely wipe and delete a specific temporary playback file."""
        try:
            p = Path(file_path)
            if p.exists() and p.is_file():
                # Overwrite first 64KB with zero bytes before unlinking to hinder recovery
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
