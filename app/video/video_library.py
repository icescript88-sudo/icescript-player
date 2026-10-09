"""
Filesystem scanner for video courses and PDF materials.
Synchronises the on-disk folder structure with the SQLite database.
"""
import re
from pathlib import Path
from typing import List

from app.config import (
    VIDEOS_DIR, SUPPORTED_VIDEO_EXTENSIONS, ENCRYPTED_VIDEO_EXTENSIONS,
    SUPPORTED_MATERIAL_EXTENSIONS, ENCRYPTED_MATERIAL_EXTENSIONS,
)
from app.database.database import Database
from app.database.models import Course, Lesson, Material
from app.security.encryption import EncryptionManager


class VideoLibrary:
    """Scans the local videos directory and synchronises it with the DB."""

    def __init__(self, db: Database, videos_dir: Path = VIDEOS_DIR):
        self.db = db
        self.videos_dir = videos_dir

    # ── Public API ──

    def scan(self) -> List[Course]:
        """Full scan: discover courses, lessons, and PDF materials."""
        self.videos_dir.mkdir(parents=True, exist_ok=True)

        found_folders: List[str] = []

        # Each immediate subdirectory is a course
        for item in sorted(self.videos_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                found_folders.append(item.name)
                self._process_course_folder(item)

        # Loose videos/PDFs in root → "Uncategorized" course
        root_videos = self._find_videos(self.videos_dir)
        root_materials = self._find_materials(self.videos_dir)
        if root_videos or root_materials:
            found_folders.append("_uncategorized")
            self._process_loose_videos(root_videos, root_materials)

        # Remove DB entries for courses whose folders were deleted
        self.db.remove_deleted_courses(found_folders)

        return self.db.get_all_courses()

    # ── Internals ──

    def _process_course_folder(self, folder: Path):
        """Register / update a course, its lessons, and its PDF materials from a folder."""
        course = Course(
            name=self._folder_to_title(folder.name),
            folder_name=folder.name,
        )
        self.db.upsert_course(course)

        db_course = self.db.get_course_by_folder(folder.name)
        if not db_course or db_course.id is None:
            return
        course_id = db_course.id

        # 1. Lessons
        videos = self._find_videos(folder)
        existing_filenames: List[str] = []
        lessons_batch: List[Lesson] = []

        for idx, video_path in enumerate(videos):
            existing_filenames.append(video_path.name)
            is_enc = (
                video_path.suffix.lower() in ENCRYPTED_VIDEO_EXTENSIONS
                or EncryptionManager.is_encrypted_file(video_path)
            )
            lesson = Lesson(
                course_id=course_id,
                title=self._filename_to_title(video_path.name),
                filename=video_path.name,
                file_path=str(video_path.resolve()),
                sort_order=idx,
                is_encrypted=is_enc,
            )
            lessons_batch.append(lesson)

        self.db.upsert_lessons_batch(lessons_batch)
        self.db.remove_deleted_lessons(course_id, existing_filenames)

        # 2. PDF Materials
        materials = self._find_materials(folder)
        existing_mat_filenames: List[str] = []
        materials_batch: List[Material] = []

        for idx, mat_path in enumerate(materials):
            existing_mat_filenames.append(mat_path.name)
            is_enc = (
                mat_path.suffix.lower() in ENCRYPTED_MATERIAL_EXTENSIONS
                or EncryptionManager.is_encrypted_file(mat_path)
            )
            mat = Material(
                course_id=course_id,
                title=self._filename_to_title(mat_path.name),
                filename=mat_path.name,
                file_path=str(mat_path.resolve()),
                sort_order=idx,
                is_encrypted=is_enc,
            )
            materials_batch.append(mat)

        self.db.upsert_materials_batch(materials_batch)
        self.db.remove_deleted_materials(course_id, existing_mat_filenames)

    def _process_loose_videos(self, videos: List[Path], materials: List[Path]):
        """Create / update the special 'Uncategorized' course for root-level media."""
        course = Course(name="Uncategorized", folder_name="_uncategorized")
        self.db.upsert_course(course)

        db_course = self.db.get_course_by_folder("_uncategorized")
        if not db_course or db_course.id is None:
            return
        course_id = db_course.id

        # Lessons
        existing_filenames: List[str] = []
        lessons_batch: List[Lesson] = []
        for idx, video_path in enumerate(videos):
            existing_filenames.append(video_path.name)
            is_enc = (
                video_path.suffix.lower() in ENCRYPTED_VIDEO_EXTENSIONS
                or EncryptionManager.is_encrypted_file(video_path)
            )
            lesson = Lesson(
                course_id=course_id,
                title=self._filename_to_title(video_path.name),
                filename=video_path.name,
                file_path=str(video_path.resolve()),
                sort_order=idx,
                is_encrypted=is_enc,
            )
            lessons_batch.append(lesson)

        self.db.upsert_lessons_batch(lessons_batch)
        self.db.remove_deleted_lessons(course_id, existing_filenames)

        # Materials
        existing_mat_filenames: List[str] = []
        materials_batch: List[Material] = []
        for idx, mat_path in enumerate(materials):
            existing_mat_filenames.append(mat_path.name)
            is_enc = (
                mat_path.suffix.lower() in ENCRYPTED_MATERIAL_EXTENSIONS
                or EncryptionManager.is_encrypted_file(mat_path)
            )
            mat = Material(
                course_id=course_id,
                title=self._filename_to_title(mat_path.name),
                filename=mat_path.name,
                file_path=str(mat_path.resolve()),
                sort_order=idx,
                is_encrypted=is_enc,
            )
            materials_batch.append(mat)

        self.db.upsert_materials_batch(materials_batch)
        self.db.remove_deleted_materials(course_id, existing_mat_filenames)

    # ── Helpers ──

    @staticmethod
    def _find_videos(directory: Path) -> List[Path]:
        """Return sorted list of video files in *directory* (non-recursive)."""
        return sorted(
            f for f in directory.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS
        )

    @staticmethod
    def _find_materials(directory: Path) -> List[Path]:
        """Return sorted list of PDF material files in *directory* (non-recursive)."""
        return sorted(
            f for f in directory.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_MATERIAL_EXTENSIONS
        )

    @staticmethod
    def _folder_to_title(folder_name: str) -> str:
        """Convert a folder name like 'my_course-01' → 'My Course 01'."""
        name = folder_name.replace("_", " ").replace("-", " ")
        if name.islower() or name.isupper():
            return name.title()
        return name

    @staticmethod
    def _filename_to_title(filename: str) -> str:
        """Convert '01_lesson_name.mp4' → '01 lesson name'."""
        name = Path(filename).stem
        name = name.replace("_", " ")
        name = re.sub(r"\s+", " ", name).strip()
        return name
