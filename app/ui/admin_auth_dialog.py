"""
Instructor Master Password Authentication Dialog.
Restricts video encryption and protection operations to the course creator/administrator.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.security.authentication import Authentication
from app.ui.i18n import t


class AdminAuthDialog(QDialog):
    """
    Prompts for the instructor's master secret before unlocking
    course encryption and file protection features.
    """

    def __init__(self, auth: Authentication, parent=None):
        super().__init__(parent)
        self.auth = auth
        self.setWindowTitle(t("admin_auth_title"))
        self.setFixedSize(460, 310)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self._show_pwd = False

        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0e131d;
                color: #e2e8f0;
            }
            QLabel {
                background: transparent;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.07);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                font-family: monospace;
            }
            QLineEdit:focus {
                border-color: #00d2fc;
                background-color: rgba(0, 210, 252, 0.05);
            }
            QPushButton#primary_btn {
                background-color: #00d2fc;
                color: #080c14;
                font-size: 13px;
                font-weight: 800;
                border: none;
                border-radius: 6px;
                padding: 10px 22px;
            }
            QPushButton#primary_btn:hover {
                background-color: #38bdf8;
            }
            QPushButton#secondary_btn {
                background-color: rgba(255, 255, 255, 0.08);
                color: #cbd5e1;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 6px;
                padding: 10px 18px;
            }
            QPushButton#secondary_btn:hover {
                background-color: rgba(255, 255, 255, 0.15);
                color: #ffffff;
            }
            QPushButton#icon_toggle_btn {
                background: transparent;
                border: none;
                color: #94a3b8;
                font-size: 16px;
                padding: 4px;
            }
            QPushButton#icon_toggle_btn:hover {
                color: #00d2fc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        # Header Title
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        icon_lbl = QLabel("🛡️")
        icon_lbl.setStyleSheet("font-size: 26px;")
        header_row.addWidget(icon_lbl)

        title_lbl = QLabel(t("admin_auth_header"))
        title_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #ffffff;")
        header_row.addWidget(title_lbl)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Description
        desc_lbl = QLabel(t("admin_auth_desc"))
        desc_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; line-height: 1.4;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        layout.addSpacing(4)

        # Password Input Box + Eye toggle
        input_container = QFrame()
        input_container.setStyleSheet("background: transparent;")
        ic_layout = QHBoxLayout(input_container)
        ic_layout.setContentsMargins(0, 0, 0, 0)
        ic_layout.setSpacing(6)

        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_input.setPlaceholderText(t("admin_pw_placeholder"))
        self.pw_input.returnPressed.connect(self._verify_and_submit)
        ic_layout.addWidget(self.pw_input)

        self.eye_btn = QPushButton("👁")
        self.eye_btn.setObjectName("icon_toggle_btn")
        self.eye_btn.setToolTip("Mostrar/Ocultar Senha")
        self.eye_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_btn.clicked.connect(self._toggle_password_visibility)
        ic_layout.addWidget(self.eye_btn)

        layout.addWidget(input_container)

        # Error message label
        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet("color: #ef4444; font-size: 12px; font-weight: bold;")
        self.err_lbl.hide()
        layout.addWidget(self.err_lbl)

        layout.addStretch()

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.cancel_btn = QPushButton(t("admin_cancel_btn"))
        self.cancel_btn.setObjectName("secondary_btn")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)

        self.submit_btn = QPushButton(t("admin_unlock_btn"))
        self.submit_btn.setObjectName("primary_btn")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self._verify_and_submit)
        btn_row.addWidget(self.submit_btn)

        layout.addLayout(btn_row)

        self.pw_input.setFocus()

    def _toggle_password_visibility(self):
        self._show_pwd = not self._show_pwd
        if self._show_pwd:
            self.pw_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.eye_btn.setText("🔒")
        else:
            self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye_btn.setText("👁")

    def _verify_and_submit(self):
        pwd = self.pw_input.text().strip()
        if not pwd:
            self.err_lbl.setText(t("admin_err_empty"))
            self.err_lbl.show()
            self.pw_input.setFocus()
            return

        if self.auth.verify_admin_password(pwd):
            self.accept()
        else:
            self.err_lbl.setText(t("admin_err_wrong"))
            self.err_lbl.show()
            self.pw_input.selectAll()
            self.pw_input.setFocus()
