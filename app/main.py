"""
Icescript Player — Private Offline Video Player
===============================================
Entry point. Run with:

    python app/main.py          (development)
    python -m app.main          (alternative)
    IcescriptPlayer.exe         (packaged)

No internet, no server, no telemetry. 100% offline.
"""
import ctypes
import os
import sys
from pathlib import Path

# Ensure the project root is importable regardless of CWD
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from app.config import APP_NAME, ASSETS_DIR
from app.database.database import Database
from app.security.authentication import Authentication
from app.security.device_binding import DeviceBinding
from app.ui.styles import DARK_THEME
from app.ui.activation_dialog import ActivationDialog
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow
from app.video.video_library import VideoLibrary


def _handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Global handler for unhandled exceptions to prevent silent crashes."""
    import traceback
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    try:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(
            None,
            "Erro Inesperado / Unexpected Error",
            f"Ocorreu um erro no aplicativo:\n\n{exc_value}\n\nConsulte os logs para mais detalhes."
        )
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main():
    sys.excepthook = _handle_unhandled_exception
    # Set Windows AppUserModelID for crisp taskbar icon grouping
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "icescript.player.desktop.v1"
            )
        except Exception:
            pass

    # ── Qt Application ──
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyleSheet(DARK_THEME)

    # ── Application Icon ──
    icon_path = ASSETS_DIR / "icon.ico"
    if not icon_path.exists():
        icon_path = ASSETS_DIR / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # ── Core services ──
    db = Database()
    auth = Authentication(db)
    device_binding = DeviceBinding(db)

    # ── 1. Hardware Activation Check ──
    if not device_binding.is_activated():
        activation = ActivationDialog(device_binding)
        if icon_path.exists():
            activation.setWindowIcon(QIcon(str(icon_path)))
        if activation.exec() != ActivationDialog.DialogCode.Accepted:
            sys.exit(0)

    # ── 2. PIN authentication ──
    login = LoginWindow(auth, db)
    if icon_path.exists():
        login.setWindowIcon(QIcon(str(icon_path)))
    if login.exec() != LoginWindow.DialogCode.Accepted:
        sys.exit(0)

    # ── 3. Video library ──
    library = VideoLibrary(db)

    # ── 4. Main window ──
    window = MainWindow(db, library)
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
