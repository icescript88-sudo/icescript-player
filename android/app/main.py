"""
Mobile Entry Point for Icescript Player Android.
Handles initialization, offline licensing, and mobile screen navigation.
"""
import os
import sys
from pathlib import Path

# Add app directory to sys.path
_app_dir = Path(__file__).resolve().parent
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window

from app.config import APP_NAME
from app.database.database import Database
from app.security.authentication import Authentication
from app.security.device_binding import AndroidDeviceBinding
from app.security.encryption import AndroidEncryptionManager
from app.ui.mobile_ui import ActivationScreen, CourseListScreen, PlayerScreen, AboutScreen


class IcescriptMobileApp(App):
    """Main Kivy Application for Android."""
    title = APP_NAME

    def build(self):
        # Mobile dark background
        Window.clearcolor = (0.04, 0.05, 0.08, 1)

        # Core services
        self.db = Database()
        self.device_binding = AndroidDeviceBinding(self.db)
        self.enc_mgr = AndroidEncryptionManager(self.db, device_binding=self.device_binding)
        self.auth = Authentication(self.db)

        # Screen Manager
        self.sm = ScreenManager(transition=SlideTransition())

        # Setup screens
        self.act_screen = ActivationScreen(
            device_binding=self.device_binding,
            on_activated_callback=self._on_activated,
            name="activation"
        )
        self.catalog_screen = CourseListScreen(
            db=self.db,
            enc_mgr=self.enc_mgr,
            on_play_callback=self._on_play_course,
            on_about_callback=self._on_open_about,
            name="catalog"
        )
        self.player_screen = PlayerScreen(
            enc_mgr=self.enc_mgr,
            on_back_callback=self._on_back_to_catalog,
            name="player"
        )
        self.about_screen = AboutScreen(
            on_back_callback=self._on_back_to_catalog,
            name="about"
        )

        self.sm.add_widget(self.act_screen)
        self.sm.add_widget(self.catalog_screen)
        self.sm.add_widget(self.player_screen)
        self.sm.add_widget(self.about_screen)

        # Route to initial screen based on activation state
        if self.device_binding.is_activated():
            self.sm.current = "catalog"
        else:
            self.sm.current = "activation"

        return self.sm

    def _on_activated(self):
        self.sm.current = "catalog"

    def _on_open_about(self):
        self.sm.current = "about"

    def _on_play_course(self, course):
        # If the course has lessons, load first playable
        lessons = self.db.get_lessons_by_course(course.id)
        if lessons:
            self.player_screen.play_lesson(Path(lessons[0].file_path))
            self.sm.current = "player"

    def _on_back_to_catalog(self):
        self.sm.current = "catalog"

    def on_stop(self):
        # Cleanup temporary files on exit
        if hasattr(self, 'enc_mgr'):
            self.enc_mgr.cleanup_all_temp_files()


if __name__ == "__main__":
    IcescriptMobileApp().run()
