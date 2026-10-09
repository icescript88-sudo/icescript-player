"""
Application configuration and path management.
All paths are resolved relative to the application root directory.
Handles both development mode and PyInstaller frozen executables.
"""
import os
import sys
from pathlib import Path


def get_app_root() -> Path:
    """Get the application root directory.
    Works in both development and PyInstaller frozen environments.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return Path(sys.executable).parent
    else:
        # Running in development — app/ is one level below root
        return Path(__file__).parent.parent


# ── Application Metadata ──
APP_NAME = "Icescript Player"
APP_VERSION = "1.0.0"

# ── Master Instructor Security ──
# Admin password is derived from vault key at runtime — no plaintext in source.
# Can be overridden via ICESCRIPT_ADMIN_PASSWORD environment variable.
_cached_admin_password = None

def get_default_admin_password() -> str:
    """Retrieve the default admin password (derived from vault, not hardcoded)."""
    global _cached_admin_password
    if _cached_admin_password is None:
        from app.security.vault import get_default_admin_credential
        _cached_admin_password = get_default_admin_credential()
    return _cached_admin_password

# ── Directory Paths ──
APP_ROOT = get_app_root()
APP_DIR = APP_ROOT / "app"
DATA_DIR = APP_ROOT / "data"
CACHE_DIR = DATA_DIR / ".cache"
VIDEOS_DIR = APP_ROOT / "videos"
ASSETS_DIR = APP_ROOT / "assets"

# ── Database ──
DATABASE_PATH = DATA_DIR / "app.db"

# Ensure required directories exist at import time
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# ── Supported Formats ──
RAW_VIDEO_EXTENSIONS = {
    '.mp4', '.mkv', '.avi', '.mov',
    '.wmv', '.flv', '.webm', '.m4v',
}

ENCRYPTED_VIDEO_EXTENSIONS = {
    '.cvid', '.enc',
}

SUPPORTED_VIDEO_EXTENSIONS = RAW_VIDEO_EXTENSIONS | ENCRYPTED_VIDEO_EXTENSIONS

RAW_MATERIAL_EXTENSIONS = {
    '.pdf',
}

ENCRYPTED_MATERIAL_EXTENSIONS = {
    '.cpdf',
}

SUPPORTED_MATERIAL_EXTENSIONS = RAW_MATERIAL_EXTENSIONS | ENCRYPTED_MATERIAL_EXTENSIONS

# ── Playback Settings ──
SEEK_STEP_MS = 10_000          # 10 seconds forward / backward
SAVE_PROGRESS_INTERVAL_MS = 5_000   # Auto-save progress every 5 s

# ── Window Settings ──
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 700
SIDEBAR_WIDTH = 260
