"""
Android Configuration & Path Management.
Resolves paths for internal storage and external storage on Android devices.
"""
import os
import sys
from pathlib import Path


def get_android_internal_dir() -> Path:
    """Retrieve app's private internal storage directory."""
    # When running under Python-for-Android / Kivy / PySide Android
    files_dir = os.environ.get("ANDROID_PRIVATE") or os.environ.get("FILES_DIR")
    if files_dir:
        return Path(files_dir)
    # Fallback to local data folder for development/testing
    return Path(__file__).resolve().parent.parent / "data"


def get_android_external_courses_dir() -> Path:
    """Retrieve standard user-accessible storage for course videos."""
    # Typically /storage/emulated/0/Download/Icescript or app external files
    ext_storage = os.environ.get("EXTERNAL_STORAGE", "/storage/emulated/0")
    candidate = Path(ext_storage) / "Download" / "Icescript"
    if candidate.exists():
        return candidate
    return Path(__file__).resolve().parent.parent / "videos"


APP_NAME = "Icescript Player"
APP_VERSION = "1.0.0"

# Directories
DATA_DIR = get_android_internal_dir()
CACHE_DIR = DATA_DIR / ".cache"
VIDEOS_DIR = get_android_external_courses_dir()
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
DATABASE_PATH = DATA_DIR / "app.db"

# Ensure data and cache directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Formats
RAW_VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.webm', '.m4v'}
ENCRYPTED_VIDEO_EXTENSIONS = {'.cvid', '.enc'}
SUPPORTED_VIDEO_EXTENSIONS = RAW_VIDEO_EXTENSIONS | ENCRYPTED_VIDEO_EXTENSIONS

RAW_MATERIAL_EXTENSIONS = {'.pdf'}
ENCRYPTED_MATERIAL_EXTENSIONS = {'.cpdf'}
SUPPORTED_MATERIAL_EXTENSIONS = RAW_MATERIAL_EXTENSIONS | ENCRYPTED_MATERIAL_EXTENSIONS
