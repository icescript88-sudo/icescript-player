"""
Hardware Device Activation Dialog for Icescript Player.
Displays unique Computer ID (e.g. ICES-A9B5-361F-731A-A44F), provides a 1-click copy button,
and verifies the offline cryptographic license key.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpacerItem, QSizePolicy, QApplication,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap

from app.config import APP_NAME, ASSETS_DIR
from app.security.device_binding import DeviceBinding
from app.ui.i18n import I18n, t


class ActivationDialog(QDialog):
    """Dialog requiring student machine activation before application unlocks."""

    def __init__(self, device_binding: DeviceBinding, parent=None):
        super().__init__(parent)
        self.device_binding = device_binding
        self.device_id = device_binding.get_device_id()

        self.setWindowTitle(t("act_window_title"))
        self.setFixedSize(460, 580)
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
                110, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.logo_lbl.setPixmap(pix)
            self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addWidget(self.logo_lbl)

        # Header Title
        self.header_lbl = QLabel(t("act_header"))
        self.header_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.header_lbl.setStyleSheet("color: #ffffff; background: transparent;")
        self.main_layout.addWidget(self.header_lbl)

        # Subtitle
        self.sub_lbl = QLabel(t("act_sub"))
        self.sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub_lbl.setWordWrap(True)
        self.sub_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent; line-height: 1.4;")
        self.main_layout.addWidget(self.sub_lbl)

        self.main_layout.addSpacing(10)

        # Device ID Section
        self.dev_id_lbl = QLabel(t("act_dev_id_label"))
        self.dev_id_lbl.setStyleSheet("color: #00d2fc; font-size: 11px; font-weight: 800; letter-spacing: 1px; background: transparent;")
        self.main_layout.addWidget(self.dev_id_lbl)

        dev_row = QHBoxLayout()
        dev_row.setSpacing(8)

        self.dev_id_input = QLineEdit(self.device_id)
        self.dev_id_input.setReadOnly(True)
        self.dev_id_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dev_id_input.setStyleSheet(
            "background-color: #121826; color: #00d2fc; font-weight: bold; font-family: monospace; font-size: 13px; border: 1px solid #1e293b; border-radius: 6px;"
        )
        dev_row.addWidget(self.dev_id_input)

        self.copy_btn = QPushButton(t("act_copy_btn"))
        self.copy_btn.setObjectName("nav_action_btn")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_device_id)
        dev_row.addWidget(self.copy_btn)

        self.main_layout.addLayout(dev_row)

        self.main_layout.addSpacing(10)

        # Key Input Section
        self.key_lbl = QLabel(t("act_key_label"))
        self.key_lbl.setStyleSheet("color: #e2e8f0; font-size: 11px; font-weight: 800; letter-spacing: 1px; background: transparent;")
        self.main_layout.addWidget(self.key_lbl)

        self.key_input = QLineEdit()
        self.key_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_input.setMaxLength(30)
        self.key_input.setStyleSheet("font-family: monospace; font-size: 13px; font-weight: bold;")
        self.key_input.returnPressed.connect(self._on_submit)
        self.main_layout.addWidget(self.key_input)

        # Error / Status Label
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("color: #ff5555; font-size: 12px; font-weight: bold; background: transparent;")
        self.error_label.setWordWrap(True)
        self.main_layout.addWidget(self.error_label)

        self.main_layout.addSpacing(6)

        # Submit Button
        self.submit_btn = QPushButton(t("act_submit_btn"))
        self.submit_btn.setObjectName("hero_play_btn")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self._on_submit)
        self.main_layout.addWidget(self.submit_btn)

        self.key_input.setFocus()

    def _retranslate_ui(self):
        self.setWindowTitle(t("act_window_title"))
        self.lang_btn.setText(t("lang_btn"))
        self.header_lbl.setText(t("act_header"))
        self.sub_lbl.setText(t("act_sub"))
        self.dev_id_lbl.setText(t("act_dev_id_label"))
        self.copy_btn.setText(t("act_copy_btn"))
        self.key_lbl.setText(t("act_key_label"))
        self.key_input.setPlaceholderText(t("act_key_placeholder"))
        self.submit_btn.setText(t("act_submit_btn"))

    def _toggle_language(self):
        new_lang = "en" if I18n.get_lang() == "pt" else "pt"
        I18n.set_lang(new_lang)
        if self.device_binding.db:
            self.device_binding.db.set_setting("ui_language", new_lang)
        self._retranslate_ui()

    def _copy_device_id(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.device_id)
        self.copy_btn.setText(t("act_copied"))
        QTimer.singleShot(2000, lambda: self.copy_btn.setText(t("act_copy_btn")))

    def _on_submit(self):
        key = self.key_input.text().strip()
        if not key:
            self._show_error(t("act_err_empty"))
            return

        if self.device_binding.activate(key):
            self.accept()
        else:
            self._show_error(t("act_err_invalid"))
            self.key_input.selectAll()
            self.key_input.setFocus()

    def _show_error(self, message: str):
        self.error_label.setText(message)
