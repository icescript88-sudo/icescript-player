"""
VLC-Inspired Video Player Widget for Icescript Player.
Provides authentic VLC media controls with complete functionality:
- Seek bar with -10s / +10s jump buttons
- Play / Pause (Space)
- Previous Track (P): restarts if >3s, or plays previous lesson
- Stop (S): stops playback, resets to 00:00, displays VLC cone
- Next Track (N): advances to next lesson (respects shuffle)
- Toggle Fullscreen (F / F11)
- In-Player Playlist Drawer (Ctrl+L): live search & instant lesson selection
- Extended Settings / Audio & Video Effects Dialog (Ctrl+E)
- Repeat Mode (R): Off -> Loop All -> Loop One
- Shuffle Mode (Z): Random playback
- VLC-style Mute & Volume Slider with Booster up to 125%
- Playback Speed Box: 1.00x (click cycles speeds, right-click resets)
- Time Box: Elapsed / Total time (click toggles Remaining time)
"""
import random
from pathlib import Path
from typing import List, Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QSizePolicy, QFrame, QDialog,
    QTabWidget, QRadioButton, QButtonGroup, QCheckBox,
    QLineEdit, QListWidget, QListWidgetItem, QStackedLayout,
)
from PySide6.QtCore import Qt, Signal, QUrl, QTimer, QPoint
from PySide6.QtGui import QPixmap, QKeySequence, QShortcut, QMouseEvent, QWheelEvent
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from app.config import SEEK_STEP_MS, ASSETS_DIR
from app.ui.i18n import t


class VlcEffectsDialog(QDialog):
    """
    VLC-style 'Adjustments and Effects' modal dialog.
    Allows adjusting Audio Booster, Equalizer Presets, Video Aspect Ratio, and Speed.
    """
    aspect_ratio_changed = Signal(int)  # 0: Keep, 1: Ignore, 2: Expanding
    speed_changed = Signal(float)
    volume_changed = Signal(int)

    def __init__(self, current_speed: float, current_vol: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("vlc_effects_title"))
        self.setFixedWidth(460)
        self.setFixedHeight(380)
        self.setStyleSheet("""
            QDialog {
                background-color: #121620;
                color: #e2e8f0;
            }
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.12);
                background-color: #161c28;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #10141d;
                color: #94a3b8;
                padding: 8px 18px;
                font-weight: bold;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #161c28;
                color: #00d2fc;
                border-color: rgba(255, 255, 255, 0.16);
            }
            QLabel {
                color: #e2e8f0;
                font-size: 13px;
                background: transparent;
            }
            QRadioButton {
                color: #cbd5e1;
                font-size: 13px;
                spacing: 8px;
                background: transparent;
            }
            QRadioButton::indicator:checked {
                background-color: #00d2fc;
                border: 2px solid #ffffff;
                border-radius: 6px;
                width: 12px;
                height: 12px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00d2fc;
                color: #0b0f19;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        tabs = QTabWidget()

        # ── Tab 1: Audio ──
        tab_audio = QWidget()
        a_layout = QVBoxLayout(tab_audio)
        a_layout.setContentsMargins(16, 16, 16, 16)
        a_layout.setSpacing(12)

        a_layout.addWidget(QLabel(f"<b>{t('vlc_volume_booster')}</b>"))
        vol_row = QHBoxLayout()
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setObjectName("vlc_volume_slider")
        self.vol_slider.setRange(0, 150)
        self.vol_slider.setValue(current_vol)
        self.vol_label = QLabel(f"{current_vol}%")
        self.vol_label.setFixedWidth(45)
        self.vol_slider.valueChanged.connect(self._on_vol_slider_changed)
        vol_row.addWidget(self.vol_slider)
        vol_row.addWidget(self.vol_label)
        a_layout.addLayout(vol_row)

        a_layout.addSpacing(8)
        a_layout.addWidget(QLabel("<b>Equalizador / Equalizer Presets</b>"))
        self.eq_combo_labels = ["Padrão / Flat", "Diálogo & Voz Clara", "Graves Fortes (Bass)", "Cinema & Espacial"]
        for lbl in self.eq_combo_labels:
            rb = QRadioButton(lbl)
            if lbl.startswith("Padrão"):
                rb.setChecked(True)
            a_layout.addWidget(rb)

        a_layout.addStretch()
        tabs.addTab(tab_audio, f"🔊 {t('vlc_tab_audio')}")

        # ── Tab 2: Video (Aspect Ratio) ──
        tab_video = QWidget()
        v_layout = QVBoxLayout(tab_video)
        v_layout.setContentsMargins(16, 16, 16, 16)
        v_layout.setSpacing(12)

        v_layout.addWidget(QLabel(f"<b>{t('vlc_aspect_ratio')}</b>"))
        self.ar_group = QButtonGroup(self)

        self.rb_keep = QRadioButton(t("vlc_aspect_auto"))
        self.rb_keep.setChecked(True)
        self.ar_group.addButton(self.rb_keep, 0)
        v_layout.addWidget(self.rb_keep)

        self.rb_fill = QRadioButton(t("vlc_aspect_fill"))
        self.ar_group.addButton(self.rb_fill, 1)
        v_layout.addWidget(self.rb_fill)

        self.rb_expand = QRadioButton(t("vlc_aspect_16_9") + " (Expand)")
        self.ar_group.addButton(self.rb_expand, 2)
        v_layout.addWidget(self.rb_expand)

        self.ar_group.idClicked.connect(self.aspect_ratio_changed.emit)

        v_layout.addStretch()
        tabs.addTab(tab_video, f"🖥️ {t('vlc_tab_video')}")

        # ── Tab 3: Playback (Speed) ──
        tab_playback = QWidget()
        p_layout = QVBoxLayout(tab_playback)
        p_layout.setContentsMargins(16, 16, 16, 16)
        p_layout.setSpacing(12)

        p_layout.addWidget(QLabel(f"<b>{t('vlc_speed')}</b>"))
        spd_row = QHBoxLayout()
        self.spd_slider = QSlider(Qt.Orientation.Horizontal)
        self.spd_slider.setRange(25, 300)
        self.spd_slider.setValue(int(current_speed * 100))
        self.spd_label = QLabel(f"{current_speed:.2f}x")
        self.spd_label.setFixedWidth(50)
        self.spd_slider.valueChanged.connect(self._on_spd_slider_changed)
        spd_row.addWidget(self.spd_slider)
        spd_row.addWidget(self.spd_label)
        p_layout.addLayout(spd_row)

        presets_row = QHBoxLayout()
        for spd in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
            btn = QPushButton(f"{spd}x")
            btn.clicked.connect(lambda _c, s=spd: self._set_speed(s))
            presets_row.addWidget(btn)
        p_layout.addLayout(presets_row)

        reset_btn = QPushButton("↺ Redefinir para 1.00x")
        reset_btn.clicked.connect(lambda: self._set_speed(1.0))
        p_layout.addWidget(reset_btn)

        p_layout.addStretch()
        tabs.addTab(tab_playback, f"⚡ {t('vlc_tab_playback')}")

        layout.addWidget(tabs)

        # Close button
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

    def _on_vol_slider_changed(self, val: int):
        self.vol_label.setText(f"{val}%")
        self.volume_changed.emit(val)

    def _on_spd_slider_changed(self, val: int):
        speed = val / 100.0
        self.spd_label.setText(f"{speed:.2f}x")
        self.speed_changed.emit(speed)

    def _set_speed(self, speed: float):
        self.spd_slider.setValue(int(speed * 100))
        self.spd_label.setText(f"{speed:.2f}x")
        self.speed_changed.emit(speed)


class VideoPlayer(QWidget):
    """
    Self-contained video player with authentic VLC media player controls.
    """

    # ── Signals ──
    position_changed = Signal(int)       # current position (ms)
    playback_finished = Signal()         # video reached end
    fullscreen_toggled = Signal(bool)    # True → entering fullscreen
    back_requested = Signal()            # user clicked back to showcase
    notes_requested = Signal(int)        # user clicked notes (passes current position ms)
    prev_requested = Signal()            # VLC Previous Track
    next_requested = Signal()            # VLC Next Track
    stop_requested = Signal()            # VLC Stop
    lesson_selected = Signal(int)        # lesson clicked from in-player playlist drawer
    repeat_mode_changed = Signal(str)    # 'off', 'all', 'one'
    shuffle_mode_changed = Signal(bool)  # True/False

    PLAYBACK_SPEEDS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]

    def __init__(self, device_id: str = "", parent=None):
        super().__init__(parent)
        self._device_id = device_id
        self._is_fullscreen = False
        self._duration_ms = 0
        self._start_position = 0
        self._speed_idx = 2              # default 1.0x (index 2 in PLAYBACK_SPEEDS)
        self._volume = 85
        self._is_muted = False
        self._unmuted_volume = 85
        self._repeat_mode = "off"        # 'off', 'all', 'one'
        self._shuffle_mode = False
        self._show_remaining_time = False
        self._playlist_lessons: List[Any] = []
        self._current_lesson_id: Optional[int] = None
        self._current_file_path: str = ""

        self._init_player()
        self._build_ui()
        self._connect_signals()

    # ────────────────────────────────────────────
    #  Initialisation
    # ────────────────────────────────────────────

    def _init_player(self):
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(self._volume / 100.0)
        self.media_player.setAudioOutput(self.audio_output)

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Top Bar (Back button + Title + Badges) ──
        self.top_bar = QFrame()
        self.top_bar.setStyleSheet(
            "background-color: rgba(11, 15, 25, 0.95); padding: 8px 16px; border-bottom: 1px solid rgba(255,255,255,0.08);"
        )
        tb_layout = QHBoxLayout(self.top_bar)
        tb_layout.setContentsMargins(0, 0, 0, 0)

        self.back_btn = QPushButton("←  " + t("player_browser_btn").replace("←", "").strip())
        self.back_btn.setObjectName("nav_tab")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        tb_layout.addWidget(self.back_btn)

        tb_layout.addSpacing(10)

        self.notes_btn = QPushButton("📝  " + t("notes_btn").replace("📝", "").strip())
        self.notes_btn.setObjectName("nav_tab")
        self.notes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.notes_btn.clicked.connect(lambda: self.notes_requested.emit(self.media_player.position()))
        tb_layout.addWidget(self.notes_btn)

        tb_layout.addSpacing(16)

        self.title_label = QLabel(t("ready_to_play"))
        self.title_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; background: transparent;")
        tb_layout.addWidget(self.title_label)

        tb_layout.addStretch()

        self.watermark_lbl = QLabel(f"🛡️ {self._device_id}" if self._device_id else "")
        self.watermark_lbl.setStyleSheet(
            "color: rgba(255,255,255,0.45); font-family: monospace; font-size: 11px; font-weight: bold; "
            "background: rgba(0,210,252,0.08); padding: 3px 8px; border-radius: 4px;"
        )
        tb_layout.addWidget(self.watermark_lbl)

        self.badge_enc = QLabel("🔒 PROTECTED")
        self.badge_enc.setStyleSheet(
            "color: #00d2fc; font-size: 11px; font-weight: bold; letter-spacing: 1px; background: transparent;"
        )
        tb_layout.addWidget(self.badge_enc)

        root_layout.addWidget(self.top_bar)

        # ── Center Stage (Video + In-Player Playlist Drawer) ──
        center_stage = QWidget()
        center_layout = QHBoxLayout(center_stage)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # Video container
        self.video_container = QWidget()
        self.video_container_layout = QStackedLayout(self.video_container)
        self.video_container_layout.setContentsMargins(0, 0, 0, 0)

        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_widget.setMinimumHeight(300)
        self.video_widget.setStyleSheet("background-color: #000000;")
        self.media_player.setVideoOutput(self.video_widget)

        # Double click toggles fullscreen; single click toggles play/pause
        self.video_widget.mouseDoubleClickEvent = lambda _e: self.toggle_fullscreen()
        self.video_widget.mousePressEvent = self._on_video_widget_clicked
        self.video_widget.wheelEvent = self._on_video_wheel_event

        # VLC Cone Placeholder when idle/stopped
        self.cone_widget = QWidget()
        self.cone_widget.setStyleSheet("background-color: #090c13;")
        cone_layout = QVBoxLayout(self.cone_widget)
        cone_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cone_layout.setSpacing(12)

        self.cone_lbl = QLabel()
        self.cone_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cone_img_path = ASSETS_DIR / "vlc_cone.png"
        if not cone_img_path.exists():
            cone_img_path = ASSETS_DIR / "logo.png"
        if cone_img_path.exists():
            pix = QPixmap(str(cone_img_path)).scaled(
                130, 130, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.cone_lbl.setPixmap(pix)
        cone_layout.addWidget(self.cone_lbl)

        self.cone_text_lbl = QLabel(t("ready_to_play"))
        self.cone_text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cone_text_lbl.setStyleSheet("color: #64748b; font-size: 14px; font-weight: bold; background: transparent;")
        cone_layout.addWidget(self.cone_text_lbl)

        self.video_container_layout.addWidget(self.cone_widget)
        self.video_container_layout.addWidget(self.video_widget)
        self.video_container_layout.setCurrentWidget(self.cone_widget)

        center_layout.addWidget(self.video_container, stretch=1)

        # ── In-Player Playlist Drawer (Collapsible) ──
        self.playlist_drawer = QFrame()
        self.playlist_drawer.setObjectName("vlc_playlist_drawer")
        self.playlist_drawer.setFixedWidth(290)
        self.playlist_drawer.hide()

        pl_layout = QVBoxLayout(self.playlist_drawer)
        pl_layout.setContentsMargins(12, 12, 12, 12)
        pl_layout.setSpacing(8)

        pl_header = QHBoxLayout()
        pl_title = QLabel(f"📋 {t('vlc_playlist_title')}")
        pl_title.setStyleSheet("color: #00d2fc; font-weight: 800; font-size: 12px; letter-spacing: 1px;")
        pl_header.addWidget(pl_title)
        pl_header.addStretch()

        self.pl_close_btn = QPushButton("✕")
        self.pl_close_btn.setObjectName("vlc_jump_btn")
        self.pl_close_btn.setProperty("class", "vlc_jump_btn")
        self.pl_close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pl_close_btn.clicked.connect(self.toggle_playlist_drawer)
        pl_header.addWidget(self.pl_close_btn)
        pl_layout.addLayout(pl_header)

        self.pl_course_lbl = QLabel("")
        self.pl_course_lbl.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold;")
        pl_layout.addWidget(self.pl_course_lbl)

        # Filter / search input
        self.pl_search = QLineEdit()
        self.pl_search.setObjectName("vlc_search_input")
        self.pl_search.setPlaceholderText(t("vlc_filter_placeholder"))
        self.pl_search.textChanged.connect(self._filter_playlist)
        pl_layout.addWidget(self.pl_search)

        # Lessons list
        self.pl_list = QListWidget()
        self.pl_list.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.25); border: 1px solid rgba(255,255,255,0.08); "
            "border-radius: 4px; font-size: 12px; padding: 4px;"
        )
        self.pl_list.itemDoubleClicked.connect(self._on_playlist_item_activated)
        pl_layout.addWidget(self.pl_list)

        pl_btn_row = QHBoxLayout()
        self.pl_play_btn = QPushButton("▶ " + t("watch_lesson").replace("▶", "").strip())
        self.pl_play_btn.setObjectName("vlc_btn")
        self.pl_play_btn.setProperty("class", "vlc_btn")
        self.pl_play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pl_play_btn.clicked.connect(self._on_playlist_play_clicked)
        pl_btn_row.addWidget(self.pl_play_btn)
        pl_layout.addLayout(pl_btn_row)

        center_layout.addWidget(self.playlist_drawer)
        root_layout.addWidget(center_stage)

        # ── VLC Controls Frame (Seek bar + VLC Toolbar) ──
        self.controls_frame = QFrame()
        self.controls_frame.setObjectName("vlc_controls_bar")
        cf_layout = QVBoxLayout(self.controls_frame)
        cf_layout.setContentsMargins(12, 6, 12, 8)
        cf_layout.setSpacing(6)

        # ── 1. VLC Seek Bar Row ( « | Seek Slider | » ) ──
        seek_row = QHBoxLayout()
        seek_row.setContentsMargins(0, 0, 0, 0)
        seek_row.setSpacing(6)

        self.jump_back_btn = QPushButton("«")
        self.jump_back_btn.setObjectName("vlc_jump_back_btn")
        self.jump_back_btn.setProperty("class", "vlc_jump_btn")
        self.jump_back_btn.setToolTip(t("vlc_seek_back_tooltip"))
        self.jump_back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.jump_back_btn.clicked.connect(self.seek_backward)
        seek_row.addWidget(self.jump_back_btn)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setObjectName("vlc_seek_slider")
        self.progress_slider.setRange(0, 0)
        self.progress_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        seek_row.addWidget(self.progress_slider)

        self.jump_fwd_btn = QPushButton("»")
        self.jump_fwd_btn.setObjectName("vlc_jump_fwd_btn")
        self.jump_fwd_btn.setProperty("class", "vlc_jump_btn")
        self.jump_fwd_btn.setToolTip(t("vlc_seek_fwd_tooltip"))
        self.jump_fwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.jump_fwd_btn.clicked.connect(self.seek_forward)
        seek_row.addWidget(self.jump_fwd_btn)

        cf_layout.addLayout(seek_row)

        # ── 2. VLC Main Toolbar Row ──
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(5)

        # 1. Play / Pause
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setObjectName("vlc_play_btn")
        self.play_pause_btn.setToolTip(t("vlc_play"))
        self.play_pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        btn_row.addWidget(self.play_pause_btn)

        # 2. Previous Track
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setObjectName("vlc_prev_btn")
        self.prev_btn.setProperty("class", "vlc_btn")
        self.prev_btn.setToolTip(t("vlc_prev"))
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self._on_prev_clicked)
        btn_row.addWidget(self.prev_btn)

        # 3. Stop
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setObjectName("vlc_stop_btn")
        self.stop_btn.setProperty("class", "vlc_btn")
        self.stop_btn.setToolTip(t("vlc_stop"))
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.clicked.connect(self.stop)
        btn_row.addWidget(self.stop_btn)

        # 4. Next Track
        self.next_btn = QPushButton("⏭")
        self.next_btn.setObjectName("vlc_next_btn")
        self.next_btn.setProperty("class", "vlc_btn")
        self.next_btn.setToolTip(t("vlc_next"))
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self.next_requested.emit)
        btn_row.addWidget(self.next_btn)

        # 5. Fullscreen
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setObjectName("vlc_fullscreen_btn")
        self.fullscreen_btn.setProperty("class", "vlc_btn")
        self.fullscreen_btn.setToolTip(t("vlc_fullscreen"))
        self.fullscreen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        btn_row.addWidget(self.fullscreen_btn)

        # 6. Toggle Playlist
        self.playlist_btn = QPushButton("☰")
        self.playlist_btn.setObjectName("vlc_playlist_btn")
        self.playlist_btn.setProperty("class", "vlc_btn")
        self.playlist_btn.setToolTip(t("vlc_playlist"))
        self.playlist_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.playlist_btn.clicked.connect(self.toggle_playlist_drawer)
        btn_row.addWidget(self.playlist_btn)

        # 7. Extended Settings / Effects
        self.effects_btn = QPushButton("🎛")
        self.effects_btn.setObjectName("vlc_effects_btn")
        self.effects_btn.setProperty("class", "vlc_btn")
        self.effects_btn.setToolTip(t("vlc_effects"))
        self.effects_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.effects_btn.clicked.connect(self.open_effects_dialog)
        btn_row.addWidget(self.effects_btn)

        # 8. Repeat / Loop mode
        self.repeat_btn = QPushButton("🔁")
        self.repeat_btn.setObjectName("vlc_repeat_btn")
        self.repeat_btn.setProperty("class", "vlc_btn")
        self.repeat_btn.setToolTip(t("vlc_repeat_off"))
        self.repeat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.repeat_btn.clicked.connect(self.cycle_repeat_mode)
        btn_row.addWidget(self.repeat_btn)

        # 9. Shuffle / Random mode
        self.shuffle_btn = QPushButton("🔀")
        self.shuffle_btn.setObjectName("vlc_shuffle_btn")
        self.shuffle_btn.setProperty("class", "vlc_btn")
        self.shuffle_btn.setToolTip(t("vlc_shuffle_off"))
        self.shuffle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        btn_row.addWidget(self.shuffle_btn)

        btn_row.addStretch()

        # 10. Mute / Speaker
        self.mute_btn = QPushButton("🔊")
        self.mute_btn.setObjectName("vlc_mute_btn")
        self.mute_btn.setProperty("class", "vlc_btn")
        self.mute_btn.setToolTip(t("vlc_mute"))
        self.mute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mute_btn.clicked.connect(self.toggle_mute)
        btn_row.addWidget(self.mute_btn)

        # 11. Volume Percentage Label
        self.vol_pct_lbl = QLabel(f"{self._volume}%")
        self.vol_pct_lbl.setFixedWidth(40)
        self.vol_pct_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.vol_pct_lbl.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #84cc16; font-family: monospace; background: transparent;"
        )
        btn_row.addWidget(self.vol_pct_lbl)

        # 12. Volume Slider (supports VLC-style boost up to 125%)
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setObjectName("vlc_volume_slider")
        self.volume_slider.setRange(0, 125)
        self.volume_slider.setValue(self._volume)
        self.volume_slider.setFixedWidth(95)
        self.volume_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self.volume_slider)

        btn_row.addSpacing(10)

        # 13. Speed Box (1.00x)
        self.speed_box = QPushButton(f"{self.PLAYBACK_SPEEDS[self._speed_idx]:.2f}x")
        self.speed_box.setObjectName("vlc_speed_box")
        self.speed_box.setToolTip(t("vlc_speed"))
        self.speed_box.setCursor(Qt.CursorShape.PointingHandCursor)
        self.speed_box.clicked.connect(self.cycle_speed)
        self.speed_box.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.speed_box.customContextMenuRequested.connect(lambda _pos: self.set_speed(1.0))
        btn_row.addWidget(self.speed_box)

        # 14. Time Box (00:00 / 00:00, click toggles remaining time!)
        self.time_box = QLabel("00:00 / 00:00")
        self.time_box.setObjectName("vlc_status_box")
        self.time_box.setToolTip(t("vlc_time_tooltip"))
        self.time_box.setCursor(Qt.CursorShape.PointingHandCursor)
        self.time_box.mousePressEvent = self._toggle_time_display
        btn_row.addWidget(self.time_box)

        cf_layout.addLayout(btn_row)
        root_layout.addWidget(self.controls_frame)

    def _connect_signals(self):
        self.media_player.positionChanged.connect(self._on_position_changed)
        self.media_player.durationChanged.connect(self._on_duration_changed)
        self.media_player.playbackStateChanged.connect(self._on_state_changed)
        self.media_player.mediaStatusChanged.connect(self._on_media_status)
        self.media_player.errorOccurred.connect(self._on_player_error)

        self.progress_slider.sliderMoved.connect(self._on_seek)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)

    # ────────────────────────────────────────────
    #  Public API for MainWindow
    # ────────────────────────────────────────────

    def set_device_id(self, device_id: str):
        self._device_id = device_id
        if hasattr(self, 'watermark_lbl') and self.watermark_lbl:
            self.watermark_lbl.setText(f"🛡️ {device_id}" if device_id else "")

    def load_video(self, file_path: str, title: str = "", start_position_ms: int = 0, is_encrypted: bool = True):
        self._current_file_path = file_path
        self._start_position = start_position_ms
        self.title_label.setText(title or Path(file_path).name)
        self.cone_text_lbl.setText(title or Path(file_path).name)
        self.badge_enc.setVisible(is_encrypted)
        self.media_player.stop()

        norm_path = str(Path(file_path).resolve())
        self.media_player.setSource(QUrl.fromLocalFile(norm_path))

        # Show video widget on load
        self.video_container_layout.setCurrentWidget(self.video_widget)
        self.video_widget.show()
        self.video_widget.update()

        QTimer.singleShot(60, self.media_player.play)

    def set_playlist(self, lessons: List[Any], current_lesson_id: Optional[int] = None, course_name: str = ""):
        """Updates the in-player playlist drawer with lessons from the current course."""
        self._playlist_lessons = lessons
        self._current_lesson_id = current_lesson_id
        if course_name:
            self.pl_course_lbl.setText(course_name.upper())
        self._populate_playlist_widget()

    def play(self):
        self.video_container_layout.setCurrentWidget(self.video_widget)
        self.media_player.play()

    def pause(self):
        self.media_player.pause()

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause()
        else:
            self.play()

    def stop(self):
        """Stops playback, resets position to 00:00, and displays the VLC cone."""
        self.media_player.stop()
        self.media_player.setPosition(0)
        self.progress_slider.setValue(0)
        self._update_time_label(0)
        self.play_pause_btn.setText("▶")
        self.play_pause_btn.setToolTip(t("vlc_play"))
        self.video_container_layout.setCurrentWidget(self.cone_widget)
        self.stop_requested.emit()

    def seek_forward(self):
        pos = min(self.media_player.position() + SEEK_STEP_MS, self._duration_ms)
        self.media_player.setPosition(pos)

    def seek_backward(self):
        pos = max(self.media_player.position() - SEEK_STEP_MS, 0)
        self.media_player.setPosition(pos)

    def seek_to(self, position_ms: int):
        self.media_player.setPosition(max(0, min(position_ms, self._duration_ms)))

    def toggle_fullscreen(self):
        self._is_fullscreen = not self._is_fullscreen
        self.fullscreen_toggled.emit(self._is_fullscreen)

    def set_fullscreen(self, fullscreen: bool):
        self._is_fullscreen = fullscreen

    def get_position(self) -> int:
        return self.media_player.position()

    def get_duration(self) -> int:
        return self._duration_ms

    def get_repeat_mode(self) -> str:
        return self._repeat_mode

    def is_shuffle(self) -> bool:
        return self._shuffle_mode

    def cleanup(self):
        self.media_player.stop()
        self.media_player.setSource(QUrl())
        self.video_container_layout.setCurrentWidget(self.cone_widget)

    # ────────────────────────────────────────────
    #  VLC Specific Actions & Handlers
    # ────────────────────────────────────────────

    def _on_prev_clicked(self):
        """Authentic VLC previous behavior: if >3s into video, restarts it; else goes to previous track."""
        if self.media_player.position() > 3000:
            self.media_player.setPosition(0)
            self.media_player.play()
        else:
            self.prev_requested.emit()

    def toggle_playlist_drawer(self):
        """Opens or closes the in-player playlist drawer."""
        is_visible = self.playlist_drawer.isVisible()
        self.playlist_drawer.setVisible(not is_visible)
        if not is_visible:
            self.playlist_btn.setStyleSheet("background-color: rgba(0, 210, 252, 0.25); border-color: #00d2fc; color: #00d2fc;")
        else:
            self.playlist_btn.setStyleSheet("")

    def open_effects_dialog(self):
        """Opens the VLC-style Adjustments and Effects dialog."""
        current_speed = self.media_player.playbackRate()
        dlg = VlcEffectsDialog(current_speed=current_speed, current_vol=self._volume, parent=self)
        dlg.speed_changed.connect(self.set_speed)
        dlg.volume_changed.connect(self.set_volume)
        dlg.aspect_ratio_changed.connect(self._set_aspect_ratio)
        dlg.exec()

    def _set_aspect_ratio(self, mode: int):
        if mode == 0:
            self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        elif mode == 1:
            self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.IgnoreAspectRatio)
        elif mode == 2:
            self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatioByExpanding)

    def cycle_repeat_mode(self):
        """Cycles VLC Repeat modes: Off -> Loop All -> Loop One -> Off."""
        if self._repeat_mode == "off":
            self._repeat_mode = "all"
            self.repeat_btn.setText("🔁")
            self.repeat_btn.setStyleSheet("background-color: rgba(0, 210, 252, 0.25); border-color: #00d2fc; color: #00d2fc;")
            self.repeat_btn.setToolTip(t("vlc_repeat_all"))
        elif self._repeat_mode == "all":
            self._repeat_mode = "one"
            self.repeat_btn.setText("🔂")
            self.repeat_btn.setStyleSheet("background-color: rgba(0, 210, 252, 0.35); border-color: #00d2fc; color: #ffffff;")
            self.repeat_btn.setToolTip(t("vlc_repeat_one"))
        else:
            self._repeat_mode = "off"
            self.repeat_btn.setText("🔁")
            self.repeat_btn.setStyleSheet("")
            self.repeat_btn.setToolTip(t("vlc_repeat_off"))

        self.repeat_mode_changed.emit(self._repeat_mode)

    def toggle_shuffle(self):
        """Toggles VLC Shuffle mode on / off."""
        self._shuffle_mode = not self._shuffle_mode
        if self._shuffle_mode:
            self.shuffle_btn.setStyleSheet("background-color: rgba(0, 210, 252, 0.25); border-color: #00d2fc; color: #00d2fc;")
            self.shuffle_btn.setToolTip(t("vlc_shuffle_on"))
        else:
            self.shuffle_btn.setStyleSheet("")
            self.shuffle_btn.setToolTip(t("vlc_shuffle_off"))

        self.shuffle_mode_changed.emit(self._shuffle_mode)

    def toggle_mute(self):
        """Toggles audio mute, restoring the previous volume level."""
        if self._is_muted or self._volume == 0:
            self._is_muted = False
            restored = max(self._unmuted_volume, 15)
            self.set_volume(restored)
        else:
            self._unmuted_volume = self._volume
            self._is_muted = True
            self.set_volume(0)

    def set_volume(self, value: int):
        self._volume = max(0, min(value, 150))
        self.volume_slider.blockSignals(True)
        self.volume_slider.setValue(self._volume)
        self.volume_slider.blockSignals(False)
        self._on_volume_changed(self._volume)

    def set_speed(self, speed: float):
        self.media_player.setPlaybackRate(speed)
        self.speed_box.setText(f"{speed:.2f}x")
        # Update speed index if it matches a preset
        for idx, sp in enumerate(self.PLAYBACK_SPEEDS):
            if abs(sp - speed) < 0.01:
                self._speed_idx = idx
                break

    def cycle_speed(self):
        """Left click cycles through preset playback speeds."""
        self._speed_idx = (self._speed_idx + 1) % len(self.PLAYBACK_SPEEDS)
        speed = self.PLAYBACK_SPEEDS[self._speed_idx]
        self.set_speed(speed)

    # ────────────────────────────────────────────
    #  Private Handlers & Event Filters
    # ────────────────────────────────────────────

    def _on_position_changed(self, position: int):
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)
        self._update_time_label(position)
        self.position_changed.emit(position)

    def _on_duration_changed(self, duration: int):
        self._duration_ms = duration
        self.progress_slider.setRange(0, duration)
        self._update_time_label(self.media_player.position())

    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_pause_btn.setText("⏸")
            self.play_pause_btn.setToolTip(t("vlc_pause"))
            self.video_container_layout.setCurrentWidget(self.video_widget)
        else:
            self.play_pause_btn.setText("▶")
            self.play_pause_btn.setToolTip(t("vlc_play"))

    def _on_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            if self._start_position > 0:
                pos = self._start_position
                self._start_position = 0
                QTimer.singleShot(150, lambda: self.media_player.setPosition(pos))
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.playback_finished.emit()

    def _on_player_error(self, error, error_string: str = ""):
        msg = error_string or self.media_player.errorString()
        print(f"[VideoPlayer] Error: {error} - {msg}")
        if msg:
            self.title_label.setText(f"Erro: {msg}")

    def _on_seek(self, position: int):
        self.media_player.setPosition(position)
        self._update_time_label(position)

    def _on_slider_released(self):
        self.media_player.setPosition(self.progress_slider.value())

    def _on_volume_changed(self, value: int):
        self._volume = value
        self.vol_pct_lbl.setText(f"{value}%")
        self.audio_output.setVolume(value / 100.0)

        if value == 0:
            self.mute_btn.setText("🔇")
            self.vol_pct_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #ef4444; font-family: monospace; background: transparent;")
        elif value <= 50:
            self.mute_btn.setText("🔉")
            self.vol_pct_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #84cc16; font-family: monospace; background: transparent;")
        elif value <= 100:
            self.mute_btn.setText("🔊")
            self.vol_pct_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #84cc16; font-family: monospace; background: transparent;")
        else:
            self.mute_btn.setText("🔊")
            # Orange/red boost color for > 100%
            self.vol_pct_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #f97316; font-family: monospace; background: transparent;")

    def _toggle_time_display(self, _event):
        """Clicking on time box toggles between Total time and Remaining time."""
        self._show_remaining_time = not self._show_remaining_time
        self._update_time_label(self.media_player.position())

    def _update_time_label(self, position_ms: int):
        elapsed = self._fmt(position_ms)
        if self._show_remaining_time and self._duration_ms > 0:
            remaining = max(0, self._duration_ms - position_ms)
            self.time_box.setText(f"{elapsed} / -{self._fmt(remaining)}")
        else:
            total = self._fmt(self._duration_ms)
            self.time_box.setText(f"{elapsed} / {total}")

    def _on_video_widget_clicked(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_play_pause()

    def _on_video_wheel_event(self, event: QWheelEvent):
        """Mouse wheel over video adjusts volume up or down by 5%."""
        delta = event.angleDelta().y()
        step = 5 if delta > 0 else -5
        self.set_volume(self._volume + step)

    # ────────────────────────────────────────────
    #  In-Player Playlist Management
    # ────────────────────────────────────────────

    def _populate_playlist_widget(self):
        self.pl_list.clear()
        query = self.pl_search.text().strip().lower()

        for idx, ls in enumerate(self._playlist_lessons):
            title = getattr(ls, "title", str(ls))
            lid = getattr(ls, "id", None)
            is_enc = getattr(ls, "is_encrypted", False)
            completed = getattr(ls, "completed", False)

            if query and query not in title.lower():
                continue

            prefix = f"{idx + 1:02d}. "
            icons = []
            if lid == self._current_lesson_id:
                icons.append("▶")
            if completed:
                icons.append("✔")
            if is_enc:
                icons.append("🔒")

            icon_suffix = f"  {' '.join(icons)}" if icons else ""
            item = QListWidgetItem(f"{prefix}{title}{icon_suffix}")
            item.setData(Qt.ItemDataRole.UserRole, lid)

            if lid == self._current_lesson_id:
                item.setForeground(Qt.GlobalColor.cyan)
                self.pl_list.addItem(item)
                self.pl_list.setCurrentItem(item)
            else:
                self.pl_list.addItem(item)

    def _filter_playlist(self, _text: str):
        self._populate_playlist_widget()

    def _on_playlist_item_activated(self, item: QListWidgetItem):
        lid = item.data(Qt.ItemDataRole.UserRole)
        if lid is not None:
            self.lesson_selected.emit(lid)

    def _on_playlist_play_clicked(self):
        curr = self.pl_list.currentItem()
        if curr:
            self._on_playlist_item_activated(curr)

    @staticmethod
    def _fmt(ms: int) -> str:
        s = ms // 1000
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
