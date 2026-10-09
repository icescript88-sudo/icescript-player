"""
Notes and Bookmarks dialog for Icescript Player.
Allows students to take timestamped study notes and click to jump to exact moments in the video.
"""
from typing import List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QFrame, QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from app.database.database import Database
from app.database.models import Note
from app.ui.i18n import t


class NotesDialog(QDialog):
    """Interactive sidebar / dialog for taking timestamped notes during playback."""

    seek_requested = Signal(int)  # Emits timestamp_ms when user clicks a bookmark

    def __init__(self, db: Database, lesson_id: int, lesson_title: str, current_time_ms: int, parent=None):
        super().__init__(parent)
        self.db = db
        self.lesson_id = lesson_id
        self.lesson_title = lesson_title
        self.current_time_ms = current_time_ms

        self.setWindowTitle(t("notes_title"))
        self.setFixedSize(540, 520)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        self._build_ui()
        self._load_notes()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Title
        title_lbl = QLabel(f"📝 {t('notes_title')}")
        title_lbl.setObjectName("title_label")
        layout.addWidget(title_lbl)

        lesson_lbl = QLabel(f"Aula: {self.lesson_title}")
        lesson_lbl.setStyleSheet("color: #00d2fc; font-size: 13px; font-weight: bold;")
        lesson_lbl.setWordWrap(True)
        layout.addWidget(lesson_lbl)

        # ── Add Note Section ──
        add_frame = QFrame()
        add_frame.setStyleSheet("background-color: #121829; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px;")
        af_layout = QVBoxLayout(add_frame)
        af_layout.setContentsMargins(10, 8, 10, 8)
        af_layout.setSpacing(8)

        time_str = self._fmt(self.current_time_ms)
        self.time_badge = QLabel(f"⏱️ Momento Atual: {time_str}")
        self.time_badge.setStyleSheet("color: #f1f5f9; font-weight: bold; font-size: 12px;")
        af_layout.addWidget(self.time_badge)

        self.input_note = QLineEdit()
        self.input_note.setPlaceholderText(t("notes_add_placeholder"))
        self.input_note.returnPressed.connect(self._add_note)
        af_layout.addWidget(self.input_note)

        save_btn = QPushButton(f"💾 {t('notes_save_btn')}")
        save_btn.setObjectName("hero_play_btn")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._add_note)
        af_layout.addWidget(save_btn)

        layout.addWidget(add_frame)

        # ── Notes List ──
        layout.addWidget(QLabel("Minhas Anotações Salvas (duplo clique para pular no vídeo):"))
        self.notes_list = QListWidget()
        self.notes_list.itemDoubleClicked.connect(self._on_note_clicked)
        layout.addWidget(self.notes_list)

        # ── Bottom Action Buttons ──
        btn_row = QHBoxLayout()
        self.jump_btn = QPushButton("▶ Pular para o Momento")
        self.jump_btn.setObjectName("hero_secondary_btn")
        self.jump_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.jump_btn.clicked.connect(self._jump_selected)
        btn_row.addWidget(self.jump_btn)

        self.delete_btn = QPushButton("🗑️ Excluir Anotação")
        self.delete_btn.setObjectName("nav_tab")
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(self._delete_selected)
        btn_row.addWidget(self.delete_btn)

        btn_row.addStretch()

        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)

    def _load_notes(self):
        self.notes_list.clear()
        notes = self.db.get_notes_for_lesson(self.lesson_id)
        if not notes:
            item = QListWidgetItem(f"ℹ {t('notes_empty')}")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.notes_list.addItem(item)
            return

        for note in notes:
            time_str = self._fmt(note.timestamp_ms)
            item = QListWidgetItem(f"⏱️ [{time_str}]  {note.text}")
            item.setData(Qt.ItemDataRole.UserRole, note.timestamp_ms)
            item.setData(Qt.ItemDataRole.UserRole + 1, note.id)
            self.notes_list.addItem(item)

    def _add_note(self):
        text = self.input_note.text().strip()
        if not text:
            return
        self.db.add_note(self.lesson_id, self.current_time_ms, text)
        self.input_note.clear()
        self._load_notes()

    def _jump_selected(self):
        item = self.notes_list.currentItem()
        if not item:
            return
        ts = item.data(Qt.ItemDataRole.UserRole)
        if ts is not None:
            self.seek_requested.emit(ts)
            self.accept()

    def _on_note_clicked(self, item):
        ts = item.data(Qt.ItemDataRole.UserRole)
        if ts is not None:
            self.seek_requested.emit(ts)
            self.accept()

    def _delete_selected(self):
        item = self.notes_list.currentItem()
        if not item:
            return
        note_id = item.data(Qt.ItemDataRole.UserRole + 1)
        if note_id:
            self.db.delete_note(note_id)
            self._load_notes()

    @staticmethod
    def _fmt(ms: int) -> str:
        s = ms // 1000
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
