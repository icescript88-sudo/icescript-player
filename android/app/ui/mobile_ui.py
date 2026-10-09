"""
Mobile User Interface for Icescript Player Android.
Optimized for smartphones, touch interaction, and portrait/landscape orientation.
"""
from pathlib import Path
from typing import List, Optional

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.videoplayer import VideoPlayer
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle

from app.config import VIDEOS_DIR, APP_NAME, APP_VERSION
from app.database.database import Database
from app.security.authentication import Authentication
from app.security.device_binding import AndroidDeviceBinding
from app.security.encryption import AndroidEncryptionManager
from app.ui.i18n import t


class MobileTheme:
    BG_DARK = (0.04, 0.05, 0.08, 1)
    CARD_BG = (0.09, 0.12, 0.18, 1)
    ACCENT_CYAN = (0.0, 0.82, 0.99, 1)
    TEXT_LIGHT = (0.95, 0.96, 0.98, 1)
    TEXT_MUTED = (0.6, 0.65, 0.72, 1)
    BTN_PRIMARY = (0.0, 0.48, 0.8, 1)
    BTN_SUCCESS = (0.1, 0.65, 0.35, 1)


class StyledCard(BoxLayout):
    """Reusable touch card container with rounded edges."""
    def __init__(self, bg_color=MobileTheme.CARD_BG, radius=12, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ActivationScreen(Screen):
    """Screen for offline hardware device activation."""
    def __init__(self, device_binding: AndroidDeviceBinding, on_activated_callback, **kwargs):
        super().__init__(**kwargs)
        self.device_binding = device_binding
        self.on_activated = on_activated_callback

        layout = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(16))
        
        # Header
        layout.add_widget(Label(
            text=f"[b]{APP_NAME}[/b]\n[size=14sp]Ativação do Dispositivo[/size]",
            markup=True,
            font_size='22sp',
            color=MobileTheme.ACCENT_CYAN,
            size_hint_y=0.25,
            halign='center'
        ))

        # Device ID card
        dev_card = StyledCard(orientation='vertical', padding=dp(16), spacing=dp(8), size_hint_y=0.25)
        dev_card.add_widget(Label(
            text="ID DESTE DISPOSITIVO:",
            color=MobileTheme.TEXT_MUTED,
            font_size='13sp',
            size_hint_y=0.3
        ))
        self.device_id_lbl = Label(
            text=self.device_binding.get_device_id(),
            color=MobileTheme.TEXT_LIGHT,
            font_size='16sp',
            bold=True,
            size_hint_y=0.7
        )
        dev_card.add_widget(self.device_id_lbl)
        layout.add_widget(dev_card)

        # Key Input
        self.key_input = TextInput(
            hint_text="Insira a chave (ACT-XXXX-XXXX-XXXX-XXXX)",
            multiline=False,
            size_hint_y=0.15,
            font_size='15sp',
            background_color=(0.12, 0.15, 0.22, 1),
            foreground_color=MobileTheme.TEXT_LIGHT
        )
        layout.add_widget(self.key_input)

        # Status feedback
        self.status_lbl = Label(
            text="",
            color=(0.95, 0.3, 0.3, 1),
            size_hint_y=0.1,
            font_size='13sp'
        )
        layout.add_widget(self.status_lbl)

        # Activate Button
        btn = Button(
            text="Ativar Agora",
            background_color=MobileTheme.BTN_PRIMARY,
            size_hint_y=0.15,
            bold=True
        )
        btn.bind(on_press=self._do_activation)
        layout.add_widget(btn)

        self.add_widget(layout)

    def _do_activation(self, *args):
        key = self.key_input.text.strip()
        if self.device_binding.activate(key):
            self.status_lbl.text = "[OK] Dispositivo ativado com sucesso!"
            self.status_lbl.color = MobileTheme.BTN_SUCCESS
            self.on_activated()
        else:
            self.status_lbl.text = "Chave inválida para este aparelho."
            self.status_lbl.color = (0.95, 0.3, 0.3, 1)


class CourseListScreen(Screen):
    """Mobile Course & Lesson Browser Screen."""
    def __init__(self, db: Database, enc_mgr: AndroidEncryptionManager, on_play_callback, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.enc_mgr = enc_mgr
        self.on_play = on_play_callback

        root = BoxLayout(orientation='vertical')

        # Top Bar
        top_bar = BoxLayout(size_hint_y=0.1, padding=[dp(16), dp(8)], spacing=dp(10))
        with top_bar.canvas.before:
            Color(*MobileTheme.CARD_BG)
            self.top_rect = Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(pos=lambda *a: setattr(self.top_rect, 'pos', top_bar.pos),
                     size=lambda *a: setattr(self.top_rect, 'size', top_bar.size))

        top_bar.add_widget(Label(
            text=f"[b]{APP_NAME}[/b]",
            markup=True,
            font_size='18sp',
            color=MobileTheme.ACCENT_CYAN,
            halign='left',
            valign='middle'
        ))
        root.add_widget(top_bar)

        # Scrollable list
        self.scroll = ScrollView(size_hint_y=0.9)
        self.items_layout = GridLayout(cols=1, spacing=dp(12), padding=dp(16), size_hint_y=None)
        self.items_layout.bind(minimum_height=self.items_layout.setter('height'))
        self.scroll.add_widget(self.items_layout)
        root.add_widget(self.scroll)

        self.add_widget(root)

    def on_enter(self, *args):
        self.refresh_courses()

    def refresh_courses(self):
        self.items_layout.clear_widgets()
        courses = self.db.get_courses() if self.db else []

        if not courses:
            empty_lbl = Label(
                text="Nenhum curso encontrado.\nColoque seus arquivos na pasta de vídeos.",
                color=MobileTheme.TEXT_MUTED,
                size_hint_y=None,
                height=dp(100),
                halign='center'
            )
            self.items_layout.add_widget(empty_lbl)
            return

        for course in courses:
            card = StyledCard(orientation='vertical', padding=dp(16), spacing=dp(8), size_hint_y=None, height=dp(100))
            card.add_widget(Label(
                text=f"[b]{course.title}[/b]",
                markup=True,
                font_size='16sp',
                color=MobileTheme.TEXT_LIGHT,
                halign='left'
            ))
            play_btn = Button(
                text="Acessar Conteúdo",
                background_color=MobileTheme.BTN_PRIMARY,
                size_hint_y=0.5
            )
            play_btn.bind(on_press=lambda inst, c=course: self.on_play(c))
            card.add_widget(play_btn)
            self.items_layout.add_widget(card)


class PlayerScreen(Screen):
    """Mobile Video Playback Screen with clean touch controls."""
    def __init__(self, enc_mgr: AndroidEncryptionManager, on_back_callback, **kwargs):
        super().__init__(**kwargs)
        self.enc_mgr = enc_mgr
        self.on_back = on_back_callback
        self.active_temp_file: Optional[Path] = None

        self.layout = BoxLayout(orientation='vertical')

        # Video Player Widget
        self.player = VideoPlayer(state='stop', options={'allow_stretch': True})
        self.layout.add_widget(self.player)

        # Back Control bar
        bottom_bar = BoxLayout(size_hint_y=0.1, padding=dp(8))
        back_btn = Button(text="Voltar ao Catálogo", background_color=MobileTheme.CARD_BG)
        back_btn.bind(on_press=self._close_and_back)
        bottom_bar.add_widget(back_btn)
        self.layout.add_widget(bottom_bar)

        self.add_widget(self.layout)

    def play_lesson(self, video_path: Path):
        self.stop_and_cleanup()
        if self.enc_mgr.is_encrypted_file(video_path):
            self.active_temp_file = self.enc_mgr.decrypt_to_cache(video_path)
            self.player.source = str(self.active_temp_file)
        else:
            self.player.source = str(video_path)
        self.player.state = 'play'

    def _close_and_back(self, *args):
        self.stop_and_cleanup()
        self.on_back()

    def stop_and_cleanup(self):
        self.player.state = 'stop'
        self.player.source = ''
        if self.active_temp_file:
            self.enc_mgr.remove_cache_file(self.active_temp_file)
            self.active_temp_file = None
