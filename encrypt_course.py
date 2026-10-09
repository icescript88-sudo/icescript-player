"""
CLI tool to encrypt video files or entire course folders into protected .cvid format.

Usage:
    python encrypt_course.py "videos/Sample Course"
    python encrypt_course.py "videos/Sample Course" --delete-original
    python encrypt_course.py "path/to/video.mp4"
"""
import argparse
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import RAW_VIDEO_EXTENSIONS, RAW_MATERIAL_EXTENSIONS
from app.database.database import Database
from app.security.encryption import EncryptionManager


def main():
    parser = argparse.ArgumentParser(description="Icescript Player — Media & Handouts Encryption Tool")
    parser.add_argument(
        "target",
        type=str,
        help="Path to a video file, PDF document, or a course directory to encrypt",
    )
    parser.add_argument(
        "--delete-original",
        action="store_true",
        help="Permanently delete the raw original media/handout(s) after successful encryption",
    )
    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    if not target_path.exists():
        print(f"[ERROR] Target does not exist: {target_path}")
        sys.exit(1)

    db = Database()
    mgr = EncryptionManager(db)

    # Collect files
    targets = RAW_VIDEO_EXTENSIONS | RAW_MATERIAL_EXTENSIONS
    if target_path.is_file():
        files = [target_path]
    else:
        files = [
            f for f in target_path.rglob("*")
            if f.is_file() and f.suffix.lower() in targets
        ]

    if not files:
        print("[INFO] No unencrypted media or PDF handouts found matching supported formats.")
        sys.exit(0)

    print("=" * 60)
    print(f" Icescript Player — Encrypting {len(files)} file(s)")
    print(f" Delete originals: {args.delete_original}")
    print("=" * 60)

    success = 0
    for idx, f in enumerate(files, start=1):
        print(f"[{idx}/{len(files)}] Encrypting: {f.name} ... ", end="", flush=True)
        try:
            out_file = mgr.encrypt_file(f, delete_original=args.delete_original)
            print(f"DONE -> {out_file.name}")
            success += 1
        except Exception as e:
            print(f"FAILED ({e})")

    print("=" * 60)
    print(f"Finished: {success}/{len(files)} files successfully encrypted (.cvid / .cpdf).")
    print("=" * 60)


if __name__ == "__main__":
    main()
