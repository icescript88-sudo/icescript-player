"""
PIN-based authentication.
Uses salted SHA-256 hashing with constant-time comparison.
"""
import hashlib
import secrets
from typing import Optional, Tuple

from app.database.database import Database


class Authentication:
    """Manages PIN creation, storage, and verification."""

    def __init__(self, db: Database):
        self.db = db

    # ── Private helpers ──

    @staticmethod
    def _hash_pin(pin: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash a PIN with a random salt (or a provided one).
        Returns (hex_hash, hex_salt).
        """
        if salt is None:
            salt = secrets.token_hex(16)
        pin_hash = hashlib.sha256(f"{salt}:{pin}".encode("utf-8")).hexdigest()
        return pin_hash, salt

    # ── Public API ──

    def is_pin_set(self) -> bool:
        """True if the user has already configured a PIN."""
        return self.db.get_setting("pin_hash") is not None

    def set_pin(self, pin: str) -> bool:
        """Create or replace the application PIN.
        Returns True on success, False if the PIN is too short.
        """
        if len(pin) < 4:
            return False
        pin_hash, salt = self._hash_pin(pin)
        self.db.set_setting("pin_hash", pin_hash)
        self.db.set_setting("pin_salt", salt)
        return True

    def verify_pin(self, pin: str) -> bool:
        """Verify a PIN against the stored hash (constant-time)."""
        stored_hash = self.db.get_setting("pin_hash")
        stored_salt = self.db.get_setting("pin_salt")
        if not stored_hash or not stored_salt:
            return False
        computed_hash, _ = self._hash_pin(pin, stored_salt)
        return secrets.compare_digest(computed_hash, stored_hash)

    # ── Instructor Master Password ──

    def verify_admin_password(self, password: str) -> bool:
        """Verify the instructor/admin master password (constant-time)."""
        from app.config import get_default_admin_password
        stored_hash = self.db.get_setting("admin_password_hash")
        stored_salt = self.db.get_setting("admin_password_salt")

        if not stored_hash or not stored_salt:
            # First time: check against vault-derived default password
            default_pwd = get_default_admin_password()
            if secrets.compare_digest(password.strip(), default_pwd):
                # Initialize salt and hash in database
                self.set_admin_password(password.strip())
                return True
            return False

        computed_hash, _ = self._hash_pin(password.strip(), stored_salt)
        return secrets.compare_digest(computed_hash, stored_hash)

    def set_admin_password(self, new_password: str) -> bool:
        """Set or update the instructor master password."""
        if len(new_password.strip()) < 4:
            return False
        pwd_hash, salt = self._hash_pin(new_password.strip())
        self.db.set_setting("admin_password_hash", pwd_hash)
        self.db.set_setting("admin_password_salt", salt)
        return True

    def is_admin_password_customized(self) -> bool:
        """Returns True if the instructor has explicitly configured a master password in DB."""
        return self.db.get_setting("admin_password_hash") is not None
