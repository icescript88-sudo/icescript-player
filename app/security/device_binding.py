"""
Hardware Device Binding & Offline Licensing Engine.
Binds application execution and cryptographic key derivation to physical machine hardware.
Uses Motherboard UUID, Machine GUID, and HMAC-SHA256 offline signature validation.
"""
import hashlib
import hmac
import os
import subprocess
import sys
from typing import Optional, Tuple

from app.database.database import Database


class DeviceBinding:
    """Manages physical hardware fingerprinting, device locking, and offline activation."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db
        self._cached_device_id: Optional[str] = None
        self._cached_device_hash: Optional[bytes] = None

    # ────────────────────────────────────────────
    #  Hardware Fingerprinting
    # ────────────────────────────────────────────

    def get_hardware_raw_signature(self) -> str:
        """Collect non-spoofable hardware signatures from Windows."""
        components = []

        # 1. Windows Cryptography Machine GUID (Always available via native winreg)
        try:
            import winreg
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Cryptography")
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            if guid:
                components.append(f"GUID:{guid.strip()}")
        except Exception:
            pass

        # 2. Motherboard UUID via CIM / WMIC (with CREATE_NO_WINDOW and DEVNULL for GUI mode)
        try:
            cmd = "powershell -NoProfile -Command (Get-CimInstance Win32_ComputerSystemProduct).UUID"
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            mb_uuid = subprocess.check_output(
                cmd, shell=True, text=True, timeout=3,
                stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=flags
            ).strip()
            if mb_uuid and "Error" not in mb_uuid:
                components.append(f"MBO:{mb_uuid}")
        except Exception:
            pass

        # 3. CPU Processor ID (Fallback)
        try:
            cmd = "powershell -NoProfile -Command (Get-CimInstance Win32_Processor).ProcessorId"
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
            cpu_id = subprocess.check_output(
                cmd, shell=True, text=True, timeout=3,
                stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=flags
            ).strip()
            if cpu_id and "Error" not in cpu_id:
                components.append(f"CPU:{cpu_id}")
        except Exception:
            pass

        if not components:
            components.append(f"HOST:{os.environ.get('COMPUTERNAME', 'DEFAULT_HOST')}")

        return "::".join(components)

    def get_guid_only_device_id(self) -> Optional[str]:
        """Return Device ID computed solely from Windows Machine GUID for fallback tolerance."""
        try:
            import winreg
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Cryptography")
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            if guid:
                sig = f"GUID:{guid.strip()}"
                digest = hashlib.sha256(sig.encode("utf-8")).hexdigest().upper()
                return f"ICES-{digest[0:4]}-{digest[4:8]}-{digest[8:12]}-{digest[12:16]}"
        except Exception:
            pass
        return None

    def get_device_id(self) -> str:
        """Return human-readable 20-character Device ID: e.g. ICES-A9B5-361F-731A-A44F."""
        if self._cached_device_id:
            return self._cached_device_id

        raw_sig = self.get_hardware_raw_signature()
        digest = hashlib.sha256(raw_sig.encode("utf-8")).hexdigest().upper()
        self._cached_device_id = f"ICES-{digest[0:4]}-{digest[4:8]}-{digest[8:12]}-{digest[12:16]}"
        return self._cached_device_id

    def get_device_hash(self) -> bytes:
        """Return 256-bit binary device hash for cryptographic key derivation."""
        if self._cached_device_hash:
            return self._cached_device_hash

        raw_sig = self.get_hardware_raw_signature()
        self._cached_device_hash = hashlib.sha256(raw_sig.encode("utf-8")).digest()
        return self._cached_device_hash

    # ────────────────────────────────────────────
    #  Offline License Key Generation & Verification
    # ────────────────────────────────────────────

    @staticmethod
    def generate_activation_key(device_id: str, custom_secret: bytes = None) -> str:
        """Generate a cryptographic offline activation key for a specific Device ID.
        Format: ACT-XXXX-XXXX-XXXX-XXXX
        """
        if custom_secret is None:
            from app.security.vault import get_signing_secret
            custom_secret = get_signing_secret()

        clean_dev = device_id.strip().upper()
        sig = hmac.new(custom_secret, clean_dev.encode("utf-8"), hashlib.sha256).hexdigest().upper()
        return f"ACT-{sig[0:4]}-{sig[4:8]}-{sig[8:12]}-{sig[12:16]}"

    def verify_activation_key(self, device_id: str, activation_key: str) -> bool:
        """Verify if activation key mathematically matches this device (constant-time)."""
        expected_key = self.generate_activation_key(device_id)
        clean_input = activation_key.strip().upper()
        if hmac.compare_digest(expected_key, clean_input):
            return True

        alt_id = self.get_guid_only_device_id()
        if alt_id and hmac.compare_digest(self.generate_activation_key(alt_id), clean_input):
            return True

        return False

    # ────────────────────────────────────────────
    #  Activation State Persistence
    # ────────────────────────────────────────────

    def is_activated(self) -> bool:
        """Check if application has been activated on this physical machine."""
        if not self.db:
            return False

        stored_key = self.db.get_setting("device_activation_key")
        stored_dev_id = self.db.get_setting("device_activated_id")

        if not stored_key or not stored_dev_id:
            return False

        current_dev_id = self.get_device_id()
        alt_id = self.get_guid_only_device_id()

        # Valid if it matches either the full device ID or GUID-only fallback
        if stored_dev_id not in (current_dev_id, alt_id):
            return False

        return self.verify_activation_key(stored_dev_id, stored_key)

    def activate(self, activation_key: str) -> bool:
        """Activate the player with a license key. Returns True on success."""
        current_dev_id = self.get_device_id()
        if not self.verify_activation_key(current_dev_id, activation_key):
            alt_id = self.get_guid_only_device_id()
            if alt_id and self.verify_activation_key(alt_id, activation_key):
                current_dev_id = alt_id
            else:
                return False

        if self.db:
            self.db.set_setting("device_activated_id", current_dev_id)
            self.db.set_setting("device_activation_key", activation_key.strip().upper())

        return True
