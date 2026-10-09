"""
SQLite database manager.
Single-file, zero-config persistence for courses, lessons, and settings.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.config import DATABASE_PATH
from app.database.models import Course, Lesson, Material, Note


class Database:
    """Thread-safe SQLite database operations."""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a new connection with row-factory enabled."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    # ────────────────────────────────────────────
    #  Schema
    # ────────────────────────────────────────────

    def _init_database(self):
        """Create tables if they don't exist."""
        conn = self._get_connection()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS settings (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS courses (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT    NOT NULL,
                    folder_name TEXT    NOT NULL UNIQUE,
                    description TEXT    DEFAULT '',
                    created_at  TEXT    NOT NULL
                );

                CREATE TABLE IF NOT EXISTS lessons (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id       INTEGER NOT NULL,
                    title           TEXT    NOT NULL,
                    filename        TEXT    NOT NULL,
                    file_path       TEXT    NOT NULL,
                    sort_order      INTEGER DEFAULT 0,
                    duration_ms     INTEGER DEFAULT 0,
                    last_position_ms INTEGER DEFAULT 0,
                    last_played     TEXT,
                    completed       INTEGER DEFAULT 0,
                    is_encrypted    INTEGER DEFAULT 0,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                    UNIQUE(course_id, filename)
                );

                CREATE TABLE IF NOT EXISTS materials (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id    INTEGER NOT NULL,
                    lesson_id    INTEGER,
                    title        TEXT    NOT NULL,
                    filename     TEXT    NOT NULL,
                    file_path    TEXT    NOT NULL,
                    sort_order   INTEGER DEFAULT 0,
                    is_encrypted INTEGER DEFAULT 0,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL,
                    UNIQUE(course_id, filename)
                );

                CREATE TABLE IF NOT EXISTS notes (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    lesson_id    INTEGER NOT NULL,
                    timestamp_ms INTEGER NOT NULL,
                    text         TEXT    NOT NULL,
                    created_at   TEXT    NOT NULL,
                    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
                );
            """)

            # Migration: ensure is_encrypted exists in existing DBs
            columns = [r["name"] for r in conn.execute("PRAGMA table_info(lessons)").fetchall()]
            if "is_encrypted" not in columns:
                conn.execute("ALTER TABLE lessons ADD COLUMN is_encrypted INTEGER DEFAULT 0")

            conn.commit()
        finally:
            conn.close()

    # ────────────────────────────────────────────
    #  Settings (key → value)
    # ────────────────────────────────────────────

    def get_setting(self, key: str) -> Optional[str]:
        """Read a setting value by key, or None if unset."""
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
            return row["value"] if row else None
        finally:
            conn.close()

    def set_setting(self, key: str, value: str):
        """Insert or update a setting."""
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
            conn.commit()
        finally:
            conn.close()

    # ────────────────────────────────────────────
    #  Courses
    # ────────────────────────────────────────────

    def get_all_courses(self) -> List[Course]:
        """Return every course, alphabetically."""
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM courses ORDER BY name").fetchall()
            return [Course(**dict(r)) for r in rows]
        finally:
            conn.close()

    def get_course(self, course_id: int) -> Optional[Course]:
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM courses WHERE id = ?", (course_id,)
            ).fetchone()
            return Course(**dict(row)) if row else None
        finally:
            conn.close()

    def upsert_course(self, course: Course) -> int:
        """Insert a new course or update an existing one (matched by folder_name)."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """INSERT INTO courses (name, folder_name, description, created_at)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(folder_name) DO UPDATE SET
                       name        = excluded.name,
                       description = excluded.description
                """,
                (course.name, course.folder_name, course.description, course.created_at),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_course_by_folder(self, folder_name: str) -> Optional[Course]:
        """Look up a course by its folder name."""
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM courses WHERE folder_name = ?", (folder_name,)
            ).fetchone()
            return Course(**dict(row)) if row else None
        finally:
            conn.close()

    def remove_deleted_courses(self, existing_folder_names: List[str]):
        """Delete courses whose folders no longer exist on disk."""
        conn = self._get_connection()
        try:
            if not existing_folder_names:
                conn.execute("DELETE FROM courses")
            else:
                existing_set = set(existing_folder_names)
                rows = conn.execute("SELECT id, folder_name FROM courses").fetchall()
                to_delete = [(r["id"],) for r in rows if r["folder_name"] not in existing_set]
                if to_delete:
                    conn.executemany("DELETE FROM courses WHERE id = ?", to_delete)
            conn.commit()
        finally:
            conn.close()

    # ────────────────────────────────────────────
    #  Lessons
    # ────────────────────────────────────────────

    def get_lessons_for_course(self, course_id: int) -> List[Lesson]:
        """All lessons in a course, ordered by sort_order then title."""
        conn = self._get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM lessons WHERE course_id = ? ORDER BY sort_order, title",
                (course_id,),
            ).fetchall()
            return [Lesson(**dict(r)) for r in rows]
        finally:
            conn.close()

    def get_lesson(self, lesson_id: int) -> Optional[Lesson]:
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM lessons WHERE id = ?", (lesson_id,)
            ).fetchone()
            return Lesson(**dict(row)) if row else None
        finally:
            conn.close()

    def upsert_lesson(self, lesson: Lesson) -> int:
        """Insert a new lesson or update an existing one (matched by course + filename)."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """INSERT INTO lessons
                       (course_id, title, filename, file_path, sort_order,
                        duration_ms, last_position_ms, last_played, completed, is_encrypted)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(course_id, filename) DO UPDATE SET
                       title        = excluded.title,
                       file_path    = excluded.file_path,
                       sort_order   = excluded.sort_order,
                       is_encrypted = excluded.is_encrypted
                """,
                (
                    lesson.course_id, lesson.title, lesson.filename,
                    lesson.file_path, lesson.sort_order, lesson.duration_ms,
                    lesson.last_position_ms, lesson.last_played,
                    int(lesson.completed), int(lesson.is_encrypted),
                ),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def upsert_lessons_batch(self, lessons: List[Lesson]):
        """Bulk insert/update lessons in a single fast database transaction."""
        if not lessons:
            return
        conn = self._get_connection()
        try:
            params = [
                (
                    ls.course_id, ls.title, ls.filename, ls.file_path,
                    ls.sort_order, ls.duration_ms, ls.last_position_ms,
                    ls.last_played, int(ls.completed), int(ls.is_encrypted),
                )
                for ls in lessons
            ]
            conn.executemany(
                """INSERT INTO lessons
                       (course_id, title, filename, file_path, sort_order,
                        duration_ms, last_position_ms, last_played, completed, is_encrypted)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(course_id, filename) DO UPDATE SET
                       title        = excluded.title,
                       file_path    = excluded.file_path,
                       sort_order   = excluded.sort_order,
                       is_encrypted = excluded.is_encrypted
                """,
                params,
            )
            conn.commit()
        finally:
            conn.close()

    def update_lesson_progress(
        self,
        lesson_id: int,
        position_ms: int,
        duration_ms: int = 0,
        completed: bool = False,
    ):
        """Save playback progress for a lesson."""
        conn = self._get_connection()
        try:
            conn.execute(
                """UPDATE lessons SET
                       last_position_ms = ?,
                       duration_ms      = CASE WHEN ? > 0 THEN ? ELSE duration_ms END,
                       last_played      = ?,
                       completed        = ?
                   WHERE id = ?
                """,
                (
                    position_ms,
                    duration_ms, duration_ms,
                    datetime.now().isoformat(),
                    int(completed),
                    lesson_id,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def get_continue_watching(self, limit: int = 10) -> List[dict]:
        """Recent, unfinished lessons with their course name (for "Continue Watching")."""
        conn = self._get_connection()
        try:
            rows = conn.execute(
                """SELECT l.*, c.name AS course_name
                   FROM lessons l
                   JOIN courses c ON l.course_id = c.id
                   WHERE l.last_played IS NOT NULL
                     AND l.completed = 0
                     AND l.last_position_ms > 0
                   ORDER BY l.last_played DESC
                   LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def remove_deleted_lessons(self, course_id: int, existing_filenames: List[str]):
        """Delete lessons whose video files no longer exist on disk."""
        conn = self._get_connection()
        try:
            if not existing_filenames:
                conn.execute(
                    "DELETE FROM lessons WHERE course_id = ?", (course_id,)
                )
            else:
                existing_set = set(existing_filenames)
                rows = conn.execute(
                    "SELECT id, filename FROM lessons WHERE course_id = ?", (course_id,)
                ).fetchall()
                to_delete = [(r["id"],) for r in rows if r["filename"] not in existing_set]
                if to_delete:
                    conn.executemany("DELETE FROM lessons WHERE id = ?", to_delete)
            conn.commit()
        finally:
            conn.close()

    # ────────────────────────────────────────────
    #  Materials (PDFs & Handouts)
    # ────────────────────────────────────────────

    def get_materials_for_course(self, course_id: int) -> List[Material]:
        """All supplementary materials in a course, ordered by sort_order then title."""
        conn = self._get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM materials WHERE course_id = ? ORDER BY sort_order, title",
                (course_id,),
            ).fetchall()
            return [Material(**dict(r)) for r in rows]
        finally:
            conn.close()

    def get_material(self, material_id: int) -> Optional[Material]:
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM materials WHERE id = ?", (material_id,)
            ).fetchone()
            return Material(**dict(row)) if row else None
        finally:
            conn.close()

    def upsert_material(self, mat: Material) -> int:
        """Insert or update a course material/handout."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """INSERT INTO materials
                       (course_id, lesson_id, title, filename, file_path, sort_order, is_encrypted)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(course_id, filename) DO UPDATE SET
                       lesson_id    = excluded.lesson_id,
                       title        = excluded.title,
                       file_path    = excluded.file_path,
                       sort_order   = excluded.sort_order,
                       is_encrypted = excluded.is_encrypted
                """,
                (
                    mat.course_id, mat.lesson_id, mat.title,
                    mat.filename, mat.file_path, mat.sort_order,
                    int(mat.is_encrypted),
                ),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def upsert_materials_batch(self, materials: List[Material]):
        """Bulk insert/update materials in a single fast database transaction."""
        if not materials:
            return
        conn = self._get_connection()
        try:
            params = [
                (
                    mat.course_id, mat.lesson_id, mat.title,
                    mat.filename, mat.file_path, mat.sort_order,
                    int(mat.is_encrypted),
                )
                for mat in materials
            ]
            conn.executemany(
                """INSERT INTO materials
                       (course_id, lesson_id, title, filename, file_path, sort_order, is_encrypted)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(course_id, filename) DO UPDATE SET
                        lesson_id    = excluded.lesson_id,
                        title        = excluded.title,
                        file_path    = excluded.file_path,
                        sort_order   = excluded.sort_order,
                        is_encrypted = excluded.is_encrypted
                """,
                params,
            )
            conn.commit()
        finally:
            conn.close()

    def remove_deleted_materials(self, course_id: int, existing_filenames: List[str]):
        """Delete materials whose PDF files no longer exist on disk."""
        conn = self._get_connection()
        try:
            if not existing_filenames:
                conn.execute(
                    "DELETE FROM materials WHERE course_id = ?", (course_id,)
                )
            else:
                existing_set = set(existing_filenames)
                rows = conn.execute(
                    "SELECT id, filename FROM materials WHERE course_id = ?", (course_id,)
                ).fetchall()
                to_delete = [(r["id"],) for r in rows if r["filename"] not in existing_set]
                if to_delete:
                    conn.executemany("DELETE FROM materials WHERE id = ?", to_delete)
            conn.commit()
        finally:
            conn.close()

    # ────────────────────────────────────────────
    #  Notes & Bookmarks
    # ────────────────────────────────────────────

    def add_note(self, lesson_id: int, timestamp_ms: int, text: str) -> int:
        """Create a new bookmark/note for a specific moment in a lesson."""
        conn = self._get_connection()
        try:
            now = datetime.now().isoformat()
            cursor = conn.execute(
                """INSERT INTO notes (lesson_id, timestamp_ms, text, created_at)
                   VALUES (?, ?, ?, ?)""",
                (lesson_id, timestamp_ms, text.strip(), now),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_notes_for_lesson(self, lesson_id: int) -> List[Note]:
        """Return all notes and bookmarks for a lesson, sorted by video timestamp."""
        conn = self._get_connection()
        try:
            rows = conn.execute(
                """SELECT * FROM notes WHERE lesson_id = ? ORDER BY timestamp_ms ASC""",
                (lesson_id,),
            ).fetchall()
            return [Note(**dict(r)) for r in rows]
        finally:
            conn.close()

    def delete_note(self, note_id: int):
        """Remove a note by ID."""
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
        finally:
            conn.close()

