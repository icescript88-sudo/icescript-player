"""
Dialog for encrypting raw video files into protected .cvid containers.
Allows single-file or batch-folder encryption with optional removal of raw originals.
Supports PT/EN internationalization.
"""
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QProgressBar, QTextEdit, QFileDialog, QMessageBox,
    QInputDialog, QLineEdit,
)
from PySide6.QtCore import Qt, QThread, Signal

from app.config import VIDEOS_DIR, RAW_VIDEO_EXTENSIONS, RAW_MATERIAL_EXTENSIONS
from app.security.encryption import EncryptionManager
from app.security.authentication import Authentication
from app.ui.i18n import t


class EncryptWorker(QThread):
    """Worker thread to encrypt videos and PDF materials without freezing the GUI."""
    progress = Signal(int, int, str)     # current, total, filename
    finished = Signal(int, list)         # count_success, errors

    def __init__(self, files: List[Path], delete_originals: bool, encryption_mgr: EncryptionManager):
        super().__init__()
        self.files = files
        self.delete_originals = delete_originals
        self.encryption_mgr = encryption_mgr

    def run(self):
        total = len(self.files)
        success_count = 0
        errors = []

        for idx, file_path in enumerate(self.files, start=1):
            if self.isInterruptionRequested():
                break
            self.progress.emit(idx, total, file_path.name)
            try:
                self.encryption_mgr.encrypt_file(
                    source_path=file_path,
                    delete_original=self.delete_originals,
                )
                success_count += 1
            except Exception as e:
                errors.append(f"{file_path.name}: {str(e)}")

        self.finished.emit(success_count, errors)


class EncryptDialog(QDialog):
    """Dialog allowing the user to protect their raw video courses and PDF handouts."""

    def __init__(self, encryption_mgr: EncryptionManager, auth: Optional[Authentication] = None, parent=None):
        super().__init__(parent)
        self.encryption_mgr = encryption_mgr
        self.auth = auth
        self.setWindowTitle(t("protect_title"))
        self.setFixedSize(540, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        self._files_to_encrypt: List[Path] = []
        self.worker: Optional[EncryptWorker] = None
        self._build_ui()

    def closeEvent(self, event):
        """Safely interrupt background worker thread before dialog destruction to avoid crashes."""
        if self.worker and self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.wait(3000)
        super().closeEvent(event)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Title
        title = QLabel(t("protect_header"))
        title.setObjectName("title_label")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(t("protect_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #a0a0c0; font-size: 13px; line-height: 1.4;")
        layout.addWidget(desc)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.select_file_btn = QPushButton(t("protect_select_file"))
        self.select_file_btn.clicked.connect(self._select_file)
        btn_layout.addWidget(self.select_file_btn)

        self.scan_all_btn = QPushButton(t("protect_find_all"))
        self.scan_all_btn.clicked.connect(self._find_all_unencrypted)
        btn_layout.addWidget(self.scan_all_btn)

        layout.addLayout(btn_layout)

        # Selected files info
        self.info_label = QLabel(t("protect_no_files"))
        self.info_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        layout.addWidget(self.info_label)

        # Option: delete original
        self.delete_check = QCheckBox(t("protect_delete_check"))
        self.delete_check.setChecked(False)
        self.delete_check.setStyleSheet("color: #e0e0e0; font-size: 13px;")
        layout.addWidget(self.delete_check)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            "background-color: #12122a; color: #a0a0c0; font-family: monospace; font-size: 12px; border: 1px solid #2a2a4a; border-radius: 6px;"
        )
        layout.addWidget(self.log_text)

        # Bottom buttons
        bottom_layout = QHBoxLayout()

        if self.auth:
            self.change_pw_btn = QPushButton(t("admin_change_pw_btn"))
            self.change_pw_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.change_pw_btn.clicked.connect(self._change_master_password)
            bottom_layout.addWidget(self.change_pw_btn)

        bottom_layout.addStretch()

        self.start_btn = QPushButton(t("protect_start_btn"))
        self.start_btn.setObjectName("hero_play_btn")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self._start_encryption)
        bottom_layout.addWidget(self.start_btn)

        self.close_btn = QPushButton(t("protect_close_btn"))
        self.close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(self.close_btn)

        layout.addLayout(bottom_layout)

    def _change_master_password(self):
        if not self.auth:
            return
        new_pw, ok = QInputDialog.getText(
            self,
            t("admin_new_pw_title"),
            t("admin_new_pw_prompt"),
            QLineEdit.EchoMode.Password,
        )
        if ok and new_pw.strip():
            if len(new_pw.strip()) < 4:
                QMessageBox.warning(self, "Aviso", "A senha deve conter no mínimo 4 caracteres.")
                return
            self.auth.set_admin_password(new_pw.strip())
            QMessageBox.information(self, "Sucesso", t("admin_pw_changed"))

    def _select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t("protect_select_file"),
            str(VIDEOS_DIR),
            "Course Media & Handouts (*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.flv *.wmv *.pdf);;All Files (*.*)",
        )
        if file_path:
            p = Path(file_path)
            self._files_to_encrypt = [p]
            self.info_label.setText(f"Selected: {p.name}")
            self.log_text.append(f"Selected: {p}")
            self.start_btn.setEnabled(True)

    def _find_all_unencrypted(self):
        found = []
        targets = RAW_VIDEO_EXTENSIONS | RAW_MATERIAL_EXTENSIONS
        if VIDEOS_DIR.exists():
            found = [
                f for f in VIDEOS_DIR.rglob("*")
                if f.is_file() and f.suffix.lower() in targets
            ]

        if not found:
            self.info_label.setText(t("protect_none_found"))
            self.start_btn.setEnabled(False)
            QMessageBox.information(
                self, t("protect_title"), t("protect_none_found")
            )
            return

        self._files_to_encrypt = found
        self.info_label.setText(f"{len(found)} file(s) queued.")
        self.log_text.clear()
        for f in found:
            self.log_text.append(f"Queued: {f.relative_to(VIDEOS_DIR)}")
        self.start_btn.setEnabled(True)

    def _start_encryption(self):
        if not self._files_to_encrypt:
            return

        self.start_btn.setEnabled(False)
        self.select_file_btn.setEnabled(False)
        self.scan_all_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        self.worker = EncryptWorker(
            files=self._files_to_encrypt,
            delete_originals=self.delete_check.isChecked(),
            encryption_mgr=self.encryption_mgr,
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, current: int, total: int, filename: str):
        pct = int((current / total) * 100)
        self.progress_bar.setValue(pct)
        target_ext = ".cpdf" if filename.lower().endswith(".pdf") else ".cvid"
        self.log_text.append(f"[{current}/{total}] {filename} \u2192 {target_ext}")

    def _on_finished(self, success_count: int, errors: list):
        self.close_btn.setEnabled(True)
        self.select_file_btn.setEnabled(True)
        self.scan_all_btn.setEnabled(True)

        if errors:
            self.log_text.append("\nErrors encountered:")
            for err in errors:
                self.log_text.append(f"  - {err}")
            QMessageBox.warning(
                self,
                t("protect_title"),
                f"{success_count} file(s) encrypted.\n{len(errors)} error(s).",
            )
        else:
            self.log_text.append(f"\n{success_count} file(s) encrypted!")
            QMessageBox.information(
                self,
                t("protect_done_title"),
                t("protect_done_msg", count=success_count),
            )
        self._files_to_encrypt = []
        self.start_btn.setEnabled(False)
