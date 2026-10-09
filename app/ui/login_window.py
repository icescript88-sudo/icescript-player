"""
PIN-based login dialog with bilingual (PT/EN) support and official Icescript logo.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

from app.config import APP_NAME, ASSETS_DIR
from app.security.authentication import Authentication
from app.ui.i18n import I18n, t


class LoginWindow(QDialog):
    """Modal dialog for PIN authentication with language switching."""

    def __init__(self, auth: Authentication, db=None, parent=None):
        super().__init__(parent)
        self.auth = auth
        self.db = db
        self.is_setup = not auth.is_pin_set()

        # Load saved language preference if db available
        if self.db:
            saved_lang = self.db.get_setting("ui_language")
            if saved_lang:
                I18n.set_lang(saved_lang)

        self.setWindowTitle(APP_NAME)
        self.setFixedSize(430, 530)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        self._build_ui()
        self._retranslate_ui()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 24, 40, 32)
        self.main_layout.setSpacing(10)

        # Top Bar: Language toggle
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.lang_btn = QPushButton(t("lang_btn"))
        self.lang_btn.setObjectName("nav_skin_btn")
        self.lang_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lang_btn.setToolTip("Mudar Idioma / Switch Language")
        self.lang_btn.clicked.connect(self._toggle_language)
        top_bar.addWidget(self.lang_btn)
        self.main_layout.addLayout(top_bar)

        # Official Logo
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            self.logo_lbl = QLabel()
            pix = QPixmap(str(logo_path)).scaled(
                125, 125, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.logo_lbl.setPixmap(pix)
            self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addWidget(self.logo_lbl)

        # Slogan
        self.slogan_lbl = QLabel(t("slogan"))
        self.slogan_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slogan_lbl.setStyleSheet("color: #00d2fc; font-style: italic; font-size: 13px; font-weight: bold; background: transparent;")
        self.main_layout.addWidget(self.slogan_lbl)

        self.main_layout.addSpacing(14)

        # Instruction
        self.instruction_lbl = QLabel()
        self.instruction_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_lbl.setStyleSheet("color: #e2e8f0; font-size: 14px; font-weight: 600; background: transparent;")
        self.main_layout.addWidget(self.instruction_lbl)

        # PIN input
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_input.setMaxLength(32)
        self.pin_input.returnPressed.connect(self._on_submit)
        self.main_layout.addWidget(self.pin_input)

        # Confirm input (setup mode only)
        self.confirm_input = None
        if self.is_setup:
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.confirm_input.setMaxLength(32)
            self.confirm_input.returnPressed.connect(self._on_submit)
            self.main_layout.addWidget(self.confirm_input)

        # Error message
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("color: #ff5555; font-size: 12px; font-weight: bold; background: transparent;")
        self.error_label.setWordWrap(True)
        self.main_layout.addWidget(self.error_label)

        self.main_layout.addSpacing(6)

        # Submit button
        self.submit_btn = QPushButton()
        self.submit_btn.setObjectName("hero_play_btn")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self._on_submit)
        self.main_layout.addWidget(self.submit_btn)

        self.pin_input.setFocus()

    def _retranslate_ui(self):
        self.lang_btn.setText(t("lang_btn"))
        self.slogan_lbl.setText(t("slogan"))

        if self.is_setup:
            self.instruction_lbl.setText(t("login_create_title"))
            self.pin_input.setPlaceholderText(t("login_pin_placeholder"))
            if self.confirm_input:
                self.confirm_input.setPlaceholderText(t("login_confirm_placeholder"))
            self.submit_btn.setText(t("login_create_btn"))
        else:
            self.instruction_lbl.setText(t("login_enter_title"))
            self.pin_input.setPlaceholderText(t("login_pin_placeholder"))
            self.submit_btn.setText(t("login_unlock_btn"))

    def _toggle_language(self):
        new_lang = "en" if I18n.get_lang() == "pt" else "pt"
        I18n.set_lang(new_lang)
        if self.db:
            self.db.set_setting("ui_language", new_lang)
        self._retranslate_ui()

    def _on_submit(self):
        pin = self.pin_input.text().strip()

        if self.is_setup:
            confirm = self.confirm_input.text().strip() if self.confirm_input else ""
            if len(pin) < 4:
                self._show_error(t("login_err_short"))
                return
            if pin != confirm:
                self._show_error(t("login_err_mismatch"))
                if self.confirm_input:
                    self.confirm_input.clear()
                    self.confirm_input.setFocus()
                return
            if self.auth.set_pin(pin):
                self.accept()
            else:
                self._show_error(t("login_err_failed"))
        else:
            if not pin:
                self._show_error(t("login_err_empty"))
                return
            if self.auth.verify_pin(pin):
                self.accept()
            else:
                self._show_error(t("login_err_wrong"))
                self.pin_input.clear()
                self.pin_input.setFocus()

    def _show_error(self, message: str):
        self.error_label.setText(message)
