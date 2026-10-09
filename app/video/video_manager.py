"""
Video playback state manager.
Handles lesson loading, decryption to ephemeral cache, progress tracking,
and secure temporary file cleanup.
"""
from pathlib import Path
from typing import List, Optional

from app.database.database import Database
from app.database.models import Lesson
from app.security.encryption import EncryptionManager


class VideoManager:
    """Manages the currently-playing lesson, ephemeral decryption, and progress persistence."""

    # A lesson is "complete" when within this many ms of the end
    COMPLETION_THRESHOLD_MS = 5_000

    def __init__(self, db: Database, encryption_mgr: Optional[EncryptionManager] = None):
        self.db = db
        self.encryption_mgr = encryption_mgr or EncryptionManager(db)
        self.current_lesson: Optional[Lesson] = None
        self._current_temp_path: Optional[Path] = None

    def load_lesson(self, lesson_id: int) -> Optional[Lesson]:
        """Load a lesson by ID and set it as the active lesson."""
        lesson = self.db.get_lesson(lesson_id)
        if lesson:
            self.current_lesson = lesson
        return lesson

    def prepare_playback_path(self, lesson: Lesson) -> Path:
        """Resolve the playable path for a lesson.
        If encrypted, decrypts to an ephemeral file in the secure cache.
        Wipes any previously opened session cache file.
        """
        self.cleanup_active_temp_file()

        file_path = Path(lesson.file_path)
        if not file_path.exists():
            from app.config import VIDEOS_DIR
            course = self.db.get_course(lesson.course_id)
            if course:
                candidate = VIDEOS_DIR / course.folder_name / lesson.filename
                if candidate.exists():
                    file_path = candidate
            if not file_path.exists():
                candidate = VIDEOS_DIR / lesson.filename
                if candidate.exists():
                    file_path = candidate

        if not file_path.exists():
            raise FileNotFoundError(f"Video file not found: {lesson.file_path}")

        if lesson.is_encrypted or self.encryption_mgr.is_encrypted_file(file_path):
            temp_path = self.encryption_mgr.decrypt_to_cache(file_path)
            self._current_temp_path = temp_path
            return temp_path

        return file_path

    def cleanup_active_temp_file(self):
        """Immediately wipe and unlink any active decrypted temporary file."""
        if self._current_temp_path:
            self.encryption_mgr.remove_cache_file(self._current_temp_path)
            self._current_temp_path = None

    def save_progress(self, position_ms: int, duration_ms: int = 0):
        """Persist the current playback position for the active lesson."""
        if not self.current_lesson or not self.current_lesson.id:
            return

        completed = False
        if duration_ms > 0 and position_ms >= (duration_ms - self.COMPLETION_THRESHOLD_MS):
            completed = True

        self.db.update_lesson_progress(
            lesson_id=self.current_lesson.id,
            position_ms=position_ms,
            duration_ms=duration_ms,
            completed=completed,
        )
        # Keep the local model in sync
        self.current_lesson.last_position_ms = position_ms
        self.current_lesson.duration_ms = duration_ms
        self.current_lesson.completed = completed

    def mark_completed(self):
        """Mark the active lesson as fully completed and reset position."""
        if not self.current_lesson or not self.current_lesson.id:
            return
        self.db.update_lesson_progress(
            lesson_id=self.current_lesson.id,
            position_ms=0,
            completed=True,
        )
        self.current_lesson.completed = True

    def get_continue_watching(self) -> List[dict]:
        """Return recently-watched, unfinished lessons across all courses."""
        return self.db.get_continue_watching()
