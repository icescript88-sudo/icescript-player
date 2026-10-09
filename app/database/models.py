"""
Data models for the application.
Plain dataclasses — no ORM, no external dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Course:
    """A video course (maps to a folder inside videos/)."""
    id: Optional[int] = None
    name: str = ""
    folder_name: str = ""
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Lesson:
    """A single video lesson within a course."""
    id: Optional[int] = None
    course_id: int = 0
    title: str = ""
    filename: str = ""
    file_path: str = ""
    sort_order: int = 0
    duration_ms: int = 0
    last_position_ms: int = 0
    last_played: Optional[str] = None
    completed: bool = False
    is_encrypted: bool = False

    def __post_init__(self):
        # SQLite stores booleans as 0/1 — normalise on load
        self.completed = bool(self.completed)
        self.is_encrypted = bool(self.is_encrypted)


@dataclass
class Material:
    """A PDF handout, slides, or supplementary document inside a course."""
    id: Optional[int] = None
    course_id: int = 0
    lesson_id: Optional[int] = None
    title: str = ""
    filename: str = ""
    file_path: str = ""
    sort_order: int = 0
    is_encrypted: bool = False

    def __post_init__(self):
        self.is_encrypted = bool(self.is_encrypted)


@dataclass
class Note:
    """A bookmark and personal note associated with a specific timestamp in a lesson."""
    id: Optional[int] = None
    lesson_id: int = 0
    timestamp_ms: int = 0
    text: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AppSettings:
    """Application-level settings (key-value store in DB)."""
    pin_hash: str = ""
    last_course_id: Optional[int] = None
    last_lesson_id: Optional[int] = None
    volume: int = 80

