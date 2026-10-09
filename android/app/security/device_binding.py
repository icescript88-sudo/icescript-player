"""
Mobile & Cross-Platform Hardware Device Binding Engine.
Supports Android (Settings.Secure.ANDROID_ID / Build hardware specs),
with automatic fallback to Linux, Mac, and Windows.
"""
import hashlib
import hmac
import os
import sys
from typing import Optional


class AndroidDeviceBinding:
    """Manages mobile device fingerprinting and offline license activation."""

    def __init__(self, db=None):
        self.db = db
        self._cached_device_id: Optional[str] = None
        self._cached_device_hash: Optional[bytes] = None

    def get_hardware_raw_signature(self) -> str:
        """Collect hardware signatures on Android or host environment."""
        components = []

        # 1. Android Native Environment Detection
        try:
            # Pyjnius / Android API check
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            content_resolver = activity.getContentResolver()
            SettingsSecure = autoclass("android.provider.Settings$Secure")
            android_id = SettingsSecure.getString(content_resolver, SettingsSecure.ANDROID_ID)
            if android_id:
                components.append(f"AID:{android_id}")

            Build = autoclass("android.os.Build")
            components.append(f"MFG:{Build.MANUFACTURER}::{Build.MODEL}")
        except Exception:
            pass

        # 2. Linux / Android system files fallback (/etc/machine-id, /proc/sys/kernel/random/boot_id)
        if not components:
            for sys_id_path in ("/etc/machine-id", "/var/lib/dbus/machine-id", "/proc/sys/kernel/random/boot_id"):
                p = sys_id_path
                if os.path.exists(p):
                    try:
                        with open(p, "r", encoding="utf-8") as f:
                            content = f.read().strip()
                            if content:
                                components.append(f"SYS:{content}")
                                break
                    except Exception:
                        pass

        # 3. Fallback to user/host environment
        if not components:
            fallback = os.environ.get("ANDROID_ID") or os.environ.get("COMPUTERNAME") or os.environ.get("USER", "ANDROID_USER")
            components.append(f"DEV:{fallback}")

        return "::".join(components)

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

    @staticmethod
    def generate_activation_key(device_id: str, custom_secret: bytes = None) -> str:
        """Generate a cryptographic offline activation key for a specific Device ID."""
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
        return hmac.compare_digest(expected_key, clean_input)

    def is_activated(self) -> bool:
        """Check if application has been activated on this physical mobile device."""
        if not self.db:
            return False

        stored_key = self.db.get_setting("device_activation_key")
        stored_dev_id = self.db.get_setting("device_activated_id")

        if not stored_key or not stored_dev_id:
            return False

        current_dev_id = self.get_device_id()
        if stored_dev_id != current_dev_id:
            return False

        return self.verify_activation_key(stored_dev_id, stored_key)

    def activate(self, activation_key: str) -> bool:
        """Activate the player with a license key."""
        current_dev_id = self.get_device_id()
        if not self.verify_activation_key(current_dev_id, activation_key):
            return False

        if self.db:
            self.db.set_setting("device_activated_id", current_dev_id)
            self.db.set_setting("device_activation_key", activation_key.strip().upper())

        return True
