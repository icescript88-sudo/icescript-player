"""
Icescript Player — Multi-Skin Modern Interface with Bilingual & PDF Materials Support.
Supports:
- Skin 1: "Cinematic" (HBO / Streaming style with bottom carousel & hero stage)
- Skin 2: "Editorial" (DC Comics / Poster style with vertical numbered index & bold kicker)
- Live Language Switching (Português / English)
- Integrated Native Hardware-Accelerated PDF Viewer for Handouts & Slides
- Official Icescript Logo Branding
- Integrated Cinema Player with Playback Speed Control
"""
import os
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QListWidget, QListWidgetItem, QMessageBox, QSplitter,
    QApplication, QInputDialog, QDialog,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QPixmap

from app.config import (
    APP_NAME, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    SAVE_PROGRESS_INTERVAL_MS, ASSETS_DIR,
)
from app.database.database import Database
from app.database.models import Course, Lesson, Material
from app.security.authentication import Authentication
from app.security.certificate import CertificateGenerator
from app.security.device_binding import DeviceBinding
from app.security.encryption import EncryptionManager
from app.ui.video_player import VideoPlayer
from app.ui.pdf_viewer import PdfViewer
from app.ui.notes_dialog import NotesDialog
from app.ui.admin_auth_dialog import AdminAuthDialog
from app.ui.encrypt_dialog import EncryptDialog
from app.ui.about_dialog import AboutDialog
from app.ui.i18n import I18n, t
from app.ui.styles import THEMES, CINEMATIC_THEME, EDITORIAL_THEME
from app.video.video_manager import VideoManager
from app.video.video_library import VideoLibrary


class MainWindow(QMainWindow):
    """Multi-skin, bilingual main window for Icescript Player with PDF reader integration."""

    def __init__(self, db: Database, video_library: VideoLibrary, parent=None):
        super().__init__(parent)
        self.db = db
        self.video_library = video_library
        self.device_binding = DeviceBinding(db)
        self.auth = Authentication(db)
        self.encryption_mgr = EncryptionManager(db, device_binding=self.device_binding)
        self.video_manager = VideoManager(db, self.encryption_mgr)

        self._courses: List[Course] = []
        self._current_course_idx: int = 0
        self._current_lessons: List[Lesson] = []
        self._current_materials: List[Material] = []
        self._selected_lesson_idx: int = 0
        self._previous_page_idx: int = 0
        self._active_pdf_temp_path: Optional[Path] = None
        self._shuffle_history: List[int] = []

        # Load saved preferences
        self._current_skin = self.db.get_setting("ui_skin") or "cinematic"
        saved_lang = self.db.get_setting("ui_language") or "pt"
        I18n.set_lang(saved_lang)

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self._build_ui()
        self.video_player.set_device_id(self.device_binding.get_device_id())
        self._apply_skin(self._current_skin)
        self._retranslate_ui()
        self._connect_signals()
        self._setup_shortcuts()
        self._start_auto_save()
        self._load_library()

    # ════════════════════════════════════════════
    #  UI Construction
    # ════════════════════════════════════════════

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── 1. Top Navigation Bar ──
        self.top_nav = QFrame()
        self.top_nav.setObjectName("top_nav")
        nav_layout = QHBoxLayout(self.top_nav)
        nav_layout.setContentsMargins(28, 10, 28, 10)
        nav_layout.setSpacing(14)

        # Official Logo Emblem + Brand
        brand_box = QHBoxLayout()
        brand_box.setSpacing(10)

        logo_path = ASSETS_DIR / "logo_small.png"
        if not logo_path.exists():
            logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            logo_lbl = QLabel()
            pix = QPixmap(str(logo_path)).scaled(
                34, 34, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pix)
            brand_box.addWidget(logo_lbl)

        logo_title = QLabel("ICESCRIPT")
        logo_title.setObjectName("brand_logo")
        brand_box.addWidget(logo_title)

        tag = QLabel(t("app_tag"))
        tag.setObjectName("brand_tag")
        self.brand_tag_lbl = tag
        brand_box.addWidget(tag)
        nav_layout.addLayout(brand_box)

        nav_layout.addSpacing(20)

        # Nav Tabs
        self.tab_featured = QPushButton(t("nav_featured"))
        self.tab_featured.setObjectName("nav_tab")
        self.tab_featured.setCursor(Qt.CursorShape.PointingHandCursor)
        nav_layout.addWidget(self.tab_featured)

        self.tab_courses = QPushButton(t("nav_courses"))
        self.tab_courses.setObjectName("nav_tab")
        self.tab_courses.setCursor(Qt.CursorShape.PointingHandCursor)
        nav_layout.addWidget(self.tab_courses)

        self.tab_continue = QPushButton(t("nav_continue"))
        self.tab_continue.setObjectName("nav_tab")
        self.tab_continue.setCursor(Qt.CursorShape.PointingHandCursor)
        nav_layout.addWidget(self.tab_continue)

        nav_layout.addStretch()

        # Language Switcher
        self.lang_btn = QPushButton(t("lang_btn"))
        self.lang_btn.setObjectName("nav_skin_btn")
        self.lang_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lang_btn.setToolTip("Mudar Idioma / Switch Language")
        self.lang_btn.clicked.connect(self._toggle_language)
        nav_layout.addWidget(self.lang_btn)

        # Theme Switcher Button
        self.skin_btn = QPushButton(t("skin_hbo"))
        self.skin_btn.setObjectName("nav_skin_btn")
        self.skin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.skin_btn.setToolTip("Alternar Tema / Toggle Skin")
        self.skin_btn.clicked.connect(self._toggle_skin)
        nav_layout.addWidget(self.skin_btn)

        # About Us Button
        self.about_btn = QPushButton(t("nav_about"))
        self.about_btn.setObjectName("nav_skin_btn")
        self.about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.about_btn.clicked.connect(self._open_about_dialog)
        nav_layout.addWidget(self.about_btn)

        # Action Buttons
        self.scan_btn = QPushButton("🔄")
        self.scan_btn.setObjectName("nav_icon_btn")
        self.scan_btn.setToolTip(t("nav_scan_tooltip"))
        self.scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        nav_layout.addWidget(self.scan_btn)

        self.protect_btn = QPushButton(t("nav_protect"))
        self.protect_btn.setObjectName("nav_action_btn")
        self.protect_btn.setToolTip("Encrypt videos into .cvid containers")
        self.protect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        nav_layout.addWidget(self.protect_btn)

        layout.addWidget(self.top_nav)

        # ── 2. Stacked Content Area ──
        self.stack = QStackedWidget()

        # Page 0: Skin 1 — Cinematic Showcase (HBO style)
        self.page_cinematic = self._build_cinematic_page()
        self.stack.addWidget(self.page_cinematic)

        # Page 1: Skin 2 — Editorial Poster (DC Comics style)
        self.page_editorial = self._build_editorial_page()
        self.stack.addWidget(self.page_editorial)

        # Page 2: Course & PDF Browser View
        self.page_browser = self._build_browser_page()
        self.stack.addWidget(self.page_browser)

        # Page 3: Cinema Video Player View
        self.video_player = VideoPlayer()
        self.stack.addWidget(self.video_player)

        # Page 4: Integrated Native PDF Viewer
        self.pdf_viewer = PdfViewer()
        self.stack.addWidget(self.pdf_viewer)

        layout.addWidget(self.stack)

    # ════════════════════════════════════════════
    #  Skin 1: Cinematic (HBO Reference)
    # ════════════════════════════════════════════

    def _build_cinematic_page(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Hero Stage
        self.hero_stage = QFrame()
        self.hero_stage.setObjectName("hero_stage")
        hero_layout = QHBoxLayout(self.hero_stage)
        hero_layout.setContentsMargins(50, 40, 50, 20)

        left_col = QVBoxLayout()
        left_col.setSpacing(14)

        self.hero_category = QLabel(t("offline_vault"))
        self.hero_category.setObjectName("hero_badge")
        left_col.addWidget(self.hero_category)

        self.hero_title = QLabel(t("select_course"))
        self.hero_title.setObjectName("hero_title")
        self.hero_title.setWordWrap(True)
        left_col.addWidget(self.hero_title)

        self.hero_desc = QLabel(t("hero_default_desc"))
        self.hero_desc.setObjectName("hero_desc")
        self.hero_desc.setWordWrap(True)
        self.hero_desc.setMaximumWidth(600)
        left_col.addWidget(self.hero_desc)

        # Meta pills
        meta_row = QHBoxLayout()
        meta_row.setSpacing(10)
        self.hero_badge_enc = QLabel(t("badge_protected"))
        self.hero_badge_enc.setStyleSheet("color: #00d2fc; font-size: 12px; font-weight: bold; background: rgba(0,210,252,0.1); padding: 4px 10px; border-radius: 4px;")
        meta_row.addWidget(self.hero_badge_enc)

        self.hero_badge_progress = QLabel(t("badge_ready"))
        self.hero_badge_progress.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold; background: rgba(255,255,255,0.06); padding: 4px 10px; border-radius: 4px;")
        meta_row.addWidget(self.hero_badge_progress)

        self.hero_badge_pdf = QLabel("📄 PDF")
        self.hero_badge_pdf.setStyleSheet("color: #38bdf8; font-size: 12px; font-weight: bold; background: rgba(56,189,248,0.12); padding: 4px 10px; border-radius: 4px;")
        self.hero_badge_pdf.setVisible(False)
        meta_row.addWidget(self.hero_badge_pdf)

        meta_row.addStretch()
        left_col.addLayout(meta_row)

        left_col.addSpacing(10)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(14)
        self.hero_play_btn = QPushButton(t("watch_lesson"))
        self.hero_play_btn.setObjectName("hero_play_btn")
        self.hero_play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hero_play_btn.clicked.connect(self._play_current_lesson)
        btn_box.addWidget(self.hero_play_btn)

        self.hero_materials_btn = QPushButton("📄 " + t("materials_label"))
        self.hero_materials_btn.setObjectName("hero_secondary_btn")
        self.hero_materials_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hero_materials_btn.clicked.connect(self._open_first_course_pdf)
        btn_box.addWidget(self.hero_materials_btn)

        self.hero_browse_btn = QPushButton(t("all_lessons"))
        self.hero_browse_btn.setObjectName("hero_secondary_btn")
        self.hero_browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hero_browse_btn.clicked.connect(lambda: self._set_page(2))
        btn_box.addWidget(self.hero_browse_btn)

        btn_box.addStretch()
        left_col.addLayout(btn_box)

        left_col.addStretch()
        hero_layout.addLayout(left_col, stretch=6)

        # Right Col: Official Logo Emblem
        right_col = QVBoxLayout()
        right_col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_display_lbl = QLabel()
        self.logo_display_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_hero_logo(self.logo_display_lbl, 240)
        right_col.addWidget(self.logo_display_lbl)

        self.slogan_lbl = QLabel(t("slogan"))
        self.slogan_lbl.setStyleSheet("color: #00d2fc; font-style: italic; font-size: 13px; font-weight: bold; background: transparent;")
        self.slogan_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_col.addWidget(self.slogan_lbl)
        hero_layout.addLayout(right_col, stretch=4)

        page_layout.addWidget(self.hero_stage, stretch=7)

        # Bottom Carousel Switcher
        carousel_bar = QFrame()
        carousel_bar.setObjectName("carousel_bar")
        c_layout = QHBoxLayout(carousel_bar)
        c_layout.setContentsMargins(36, 12, 36, 16)
        c_layout.setSpacing(24)

        # Prev card
        self.prev_card = QFrame()
        self.prev_card.setObjectName("card_widget")
        self.prev_card.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_card.mousePressEvent = lambda _e: self._step_lesson(-1)
        prev_layout = QHBoxLayout(self.prev_card)
        prev_layout.setContentsMargins(10, 8, 14, 8)
        prev_layout.setSpacing(12)
        prev_icon_lbl = QLabel("❮")
        prev_icon_lbl.setStyleSheet("font-size: 18px; color: #00d2fc; font-weight: bold; background: transparent;")
        prev_layout.addWidget(prev_icon_lbl)
        prev_info = QVBoxLayout()
        prev_info.setSpacing(2)
        self.prev_card_title = QLabel(t("prev_lesson"))
        self.prev_card_title.setStyleSheet("font-weight: bold; color: #ffffff; font-size: 13px; background: transparent;")
        prev_info.addWidget(self.prev_card_title)
        self.prev_card_sub = QLabel(t("nav_courses"))
        self.prev_card_sub.setStyleSheet("color: #8a99ad; font-size: 11px; background: transparent;")
        prev_info.addWidget(self.prev_card_sub)
        prev_layout.addLayout(prev_info)
        c_layout.addWidget(self.prev_card, stretch=4)

        # Center line
        center_nav = QHBoxLayout()
        center_nav.setSpacing(12)
        self.carousel_prev_btn = QPushButton("❮")
        self.carousel_prev_btn.setObjectName("circle_arrow_btn")
        self.carousel_prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.carousel_prev_btn.clicked.connect(lambda: self._step_lesson(-1))
        center_nav.addWidget(self.carousel_prev_btn)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: rgba(255,255,255,0.18); min-width: 60px;")
        center_nav.addWidget(line)
        self.carousel_counter = QLabel("01 / 01")
        self.carousel_counter.setStyleSheet("color: #8a99ad; font-weight: bold; font-size: 12px; background: transparent;")
        center_nav.addWidget(self.carousel_counter)
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("color: rgba(255,255,255,0.18); min-width: 60px;")
        center_nav.addWidget(line2)
        self.carousel_next_btn = QPushButton("❯")
        self.carousel_next_btn.setObjectName("circle_arrow_btn")
        self.carousel_next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.carousel_next_btn.clicked.connect(lambda: self._step_lesson(1))
        center_nav.addWidget(self.carousel_next_btn)
        c_layout.addLayout(center_nav, stretch=3)

        # Next card
        self.next_card = QFrame()
        self.next_card.setObjectName("card_widget")
        self.next_card.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_card.mousePressEvent = lambda _e: self._step_lesson(1)
        next_layout = QHBoxLayout(self.next_card)
        next_layout.setContentsMargins(14, 8, 10, 8)
        next_layout.setSpacing(12)
        next_info = QVBoxLayout()
        next_info.setSpacing(2)
        self.next_card_title = QLabel(t("next_lesson"))
        self.next_card_title.setStyleSheet("font-weight: bold; color: #ffffff; font-size: 13px; background: transparent;")
        next_info.addWidget(self.next_card_title)
        self.next_card_sub = QLabel(t("nav_courses"))
        self.next_card_sub.setStyleSheet("color: #8a99ad; font-size: 11px; background: transparent;")
        next_info.addWidget(self.next_card_sub)
        next_layout.addLayout(next_info)
        next_icon_lbl = QLabel("❯")
        next_icon_lbl.setStyleSheet("font-size: 18px; color: #ff7a45; font-weight: bold; background: transparent;")
        next_layout.addWidget(next_icon_lbl)
        c_layout.addWidget(self.next_card, stretch=4)

        page_layout.addWidget(carousel_bar, stretch=3)
        return page

    # ════════════════════════════════════════════
    #  Skin 2: Editorial (DC Poster Reference)
    # ════════════════════════════════════════════

    def _build_editorial_page(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left Numbered Index Rail
        self.editorial_rail = QFrame()
        self.editorial_rail.setObjectName("editorial_rail")
        self.editorial_rail.setFixedWidth(240)
        rail_layout = QVBoxLayout(self.editorial_rail)
        rail_layout.setContentsMargins(20, 36, 20, 24)
        rail_layout.setSpacing(12)

        self.rail_header = QLabel(t("index_title"))
        self.rail_header.setStyleSheet("color: #00f0ff; font-size: 11px; font-weight: 800; letter-spacing: 2px; background: transparent;")
        rail_layout.addWidget(self.rail_header)

        self.editorial_index_list = QListWidget()
        self.editorial_index_list.setStyleSheet(
            "background: transparent; border: none; outline: none; font-size: 13px;"
        )
        self.editorial_index_list.currentItemChanged.connect(self._on_editorial_item_changed)
        rail_layout.addWidget(self.editorial_index_list)

        self.editorial_footer_lbl = QLabel(t("footer_vault"))
        self.editorial_footer_lbl.setStyleSheet("color: #64748b; font-size: 11px; background: transparent;")
        rail_layout.addWidget(self.editorial_footer_lbl)

        layout.addWidget(self.editorial_rail)

        # Center/Right Hero Poster Stage
        self.editorial_stage = QFrame()
        self.editorial_stage.setObjectName("editorial_stage")
        es_layout = QHBoxLayout(self.editorial_stage)
        es_layout.setContentsMargins(50, 40, 50, 30)

        center_col = QVBoxLayout()
        center_col.setSpacing(10)

        self.editorial_kicker = QLabel(t("kicker_default"))
        self.editorial_kicker.setObjectName("kicker_label")
        center_col.addWidget(self.editorial_kicker)

        self.editorial_huge_title = QLabel("ICESCRIPT")
        self.editorial_huge_title.setObjectName("huge_editorial_title")
        self.editorial_huge_title.setWordWrap(True)
        center_col.addWidget(self.editorial_huge_title)

        center_col.addSpacing(16)

        self.editorial_desc = QLabel(t("hero_default_desc"))
        self.editorial_desc.setStyleSheet("color: #94a3b8; font-size: 15px; line-height: 1.5; background: transparent;")
        self.editorial_desc.setWordWrap(True)
        self.editorial_desc.setMaximumWidth(520)
        center_col.addWidget(self.editorial_desc)

        center_col.addSpacing(24)

        btn_row = QHBoxLayout()
        self.editorial_play_btn = QPushButton(t("watch_now"))
        self.editorial_play_btn.setObjectName("editorial_play_btn")
        self.editorial_play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.editorial_play_btn.clicked.connect(self._play_current_lesson)
        btn_row.addWidget(self.editorial_play_btn)

        self.editorial_pdf_btn = QPushButton("📄 " + t("materials_label"))
        self.editorial_pdf_btn.setObjectName("hero_secondary_btn")
        self.editorial_pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.editorial_pdf_btn.clicked.connect(self._open_first_course_pdf)
        btn_row.addWidget(self.editorial_pdf_btn)

        btn_row.addStretch()
        center_col.addLayout(btn_row)

        center_col.addStretch()
        es_layout.addLayout(center_col, stretch=6)

        right_graphic = QVBoxLayout()
        right_graphic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.editorial_logo_lbl = QLabel()
        self.editorial_logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_hero_logo(self.editorial_logo_lbl, 270)
        right_graphic.addWidget(self.editorial_logo_lbl)
        es_layout.addLayout(right_graphic, stretch=4)

        layout.addWidget(self.editorial_stage)
        return page

    # ════════════════════════════════════════════
    #  Page 2: Course & Materials Browser
    # ════════════════════════════════════════════

    def _build_browser_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(14)

        top_row = QHBoxLayout()
        self.browser_title_lbl = QLabel(t("browser_title"))
        self.browser_title_lbl.setObjectName("title_label")
        top_row.addWidget(self.browser_title_lbl)
        top_row.addStretch()

        self.browser_cert_btn = QPushButton(t("cert_btn"))
        self.browser_cert_btn.setObjectName("hero_play_btn")
        self.browser_cert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browser_cert_btn.clicked.connect(self._generate_certificate)
        top_row.addWidget(self.browser_cert_btn)

        self.browser_back_btn = QPushButton(t("browser_back"))
        self.browser_back_btn.setObjectName("nav_tab")
        self.browser_back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browser_back_btn.clicked.connect(self._back_to_current_skin)
        top_row.addWidget(self.browser_back_btn)
        layout.addLayout(top_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Courses panel
        course_panel = QWidget()
        cp_layout = QVBoxLayout(course_panel)
        cp_layout.setContentsMargins(0, 0, 0, 0)
        self.browser_courses_lbl = QLabel(t("courses_label"))
        cp_layout.addWidget(self.browser_courses_lbl)
        self.course_list_widget = QListWidget()
        cp_layout.addWidget(self.course_list_widget)
        splitter.addWidget(course_panel)

        # 2. Lessons panel
        lesson_panel = QWidget()
        lp_layout = QVBoxLayout(lesson_panel)
        lp_layout.setContentsMargins(0, 0, 0, 0)
        lp_layout.setSpacing(8)
        
        lp_header = QHBoxLayout()
        self.browser_lessons_lbl = QLabel(t("lessons_label"))
        lp_header.addWidget(self.browser_lessons_lbl)
        lp_header.addStretch()
        
        self.browser_play_btn = QPushButton("▶ " + t("watch_lesson"))
        self.browser_play_btn.setObjectName("hero_play_btn")
        self.browser_play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browser_play_btn.clicked.connect(self._play_current_lesson)
        lp_header.addWidget(self.browser_play_btn)
        lp_layout.addLayout(lp_header)

        self.browser_lesson_list = QListWidget()
        lp_layout.addWidget(self.browser_lesson_list)
        splitter.addWidget(lesson_panel)

        # 3. Supplementary PDF Materials panel
        material_panel = QWidget()
        mp_layout = QVBoxLayout(material_panel)
        mp_layout.setContentsMargins(0, 0, 0, 0)
        self.browser_materials_lbl = QLabel(t("materials_label"))
        mp_layout.addWidget(self.browser_materials_lbl)
        self.browser_material_list = QListWidget()
        self.browser_material_list.itemDoubleClicked.connect(self._on_material_activated)
        mp_layout.addWidget(self.browser_material_list)
        splitter.addWidget(material_panel)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 3)
        layout.addWidget(splitter)
        return page

    # ════════════════════════════════════════════
    #  Language & Translation Logic
    # ════════════════════════════════════════════

    def _retranslate_ui(self):
        self.brand_tag_lbl.setText(t("app_tag"))
        self.tab_featured.setText(t("nav_featured"))
        self.tab_courses.setText(t("nav_courses"))
        self.tab_continue.setText(t("nav_continue"))
        self.lang_btn.setText(t("lang_btn"))
        self.skin_btn.setText(t("skin_editorial") if self._current_skin == "editorial" else t("skin_hbo"))
        self.about_btn.setText(t("nav_about"))
        self.scan_btn.setToolTip(t("nav_scan_tooltip"))
        self.protect_btn.setText(t("nav_protect"))

        self.hero_category.setText(t("offline_vault"))
        self.hero_play_btn.setText(t("watch_lesson"))
        self.hero_materials_btn.setText("📄 " + t("materials_label"))
        self.hero_browse_btn.setText(t("all_lessons"))
        self.slogan_lbl.setText(t("slogan"))

        self.rail_header.setText(t("index_title"))
        self.editorial_footer_lbl.setText(t("footer_vault"))
        self.editorial_play_btn.setText(t("watch_now"))
        self.editorial_pdf_btn.setText("📄 " + t("materials_label"))

        self.browser_title_lbl.setText(t("browser_title"))
        self.browser_back_btn.setText(t("browser_back"))
        self.browser_courses_lbl.setText(t("courses_label"))
        self.browser_lessons_lbl.setText(t("lessons_label"))
        self.browser_materials_lbl.setText(t("materials_label"))

        self._update_views()

    def _toggle_language(self):
        new_lang = "en" if I18n.get_lang() == "pt" else "pt"
        I18n.set_lang(new_lang)
        self.db.set_setting("ui_language", new_lang)
        self._retranslate_ui()

    # ════════════════════════════════════════════
    #  Skin & Theme Logic
    # ════════════════════════════════════════════

    def _apply_skin(self, skin_name: str):
        self._current_skin = skin_name
        theme_qss = THEMES.get(skin_name, CINEMATIC_THEME)
        QApplication.instance().setStyleSheet(theme_qss)

        if skin_name == "editorial":
            self.skin_btn.setText(t("skin_editorial"))
            self._set_page(1)
        else:
            self.skin_btn.setText(t("skin_hbo"))
            self._set_page(0)

        self.db.set_setting("ui_skin", skin_name)

    def _toggle_skin(self):
        new_skin = "editorial" if self._current_skin == "cinematic" else "cinematic"
        self._apply_skin(new_skin)

    def _back_to_current_skin(self):
        self._set_page(1 if self._current_skin == "editorial" else 0)

    def _load_hero_logo(self, label: QLabel, size: int):
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            pix = QPixmap(str(logo_path)).scaled(
                size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            label.setPixmap(pix)

    # ════════════════════════════════════════════
    #  Signals & Events
    # ════════════════════════════════════════════

    def _connect_signals(self):
        self.tab_featured.clicked.connect(self._back_to_current_skin)
        self.tab_courses.clicked.connect(lambda: self._set_page(2))
        self.tab_continue.clicked.connect(self._show_continue_watching)

        self.scan_btn.clicked.connect(self._scan_library)
        self.protect_btn.clicked.connect(self._open_protect_dialog)

        # VLC Video Player Signals
        self.video_player.back_requested.connect(self._back_from_video_player)
        self.video_player.fullscreen_toggled.connect(self._toggle_fullscreen)
        self.video_player.playback_finished.connect(self._on_playback_finished)
        self.video_player.notes_requested.connect(self._open_notes_dialog)
        self.video_player.prev_requested.connect(self._play_previous_lesson)
        self.video_player.next_requested.connect(self._play_next_lesson)
        self.video_player.lesson_selected.connect(self._play_lesson)
        self.video_player.stop_requested.connect(self._on_player_stopped)

        self.pdf_viewer.back_requested.connect(self._back_from_pdf)

        self.course_list_widget.currentItemChanged.connect(self._on_browser_course_selected)
        self.browser_lesson_list.itemClicked.connect(self._on_browser_lesson_clicked)
        self.browser_lesson_list.itemDoubleClicked.connect(self._on_browser_lesson_activated)

    def _setup_shortcuts(self):
        # VLC Standard Shortcuts
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.video_player.toggle_play_pause)
        QShortcut(QKeySequence(Qt.Key.Key_S), self, self.video_player.stop)
        QShortcut(QKeySequence(Qt.Key.Key_P), self, self._play_previous_lesson)
        QShortcut(QKeySequence(Qt.Key.Key_N), self, self._play_next_lesson)
        QShortcut(QKeySequence(Qt.Key.Key_M), self, self.video_player.toggle_mute)
        QShortcut(QKeySequence(Qt.Key.Key_R), self, self.video_player.cycle_repeat_mode)
        QShortcut(QKeySequence(Qt.Key.Key_Z), self, self.video_player.toggle_shuffle)
        QShortcut(QKeySequence("Ctrl+L"), self, self.video_player.toggle_playlist_drawer)
        QShortcut(QKeySequence("Ctrl+E"), self, self.video_player.open_effects_dialog)

        QShortcut(QKeySequence(Qt.Key.Key_F), self, lambda: self._toggle_fullscreen(not self.video_player._is_fullscreen))
        QShortcut(QKeySequence(Qt.Key.Key_F11), self, lambda: self._toggle_fullscreen(not self.video_player._is_fullscreen))
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, lambda: self._toggle_fullscreen(False))
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.video_player.seek_forward)
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.video_player.seek_backward)
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, lambda: self.video_player.set_volume(self.video_player._volume + 5))
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, lambda: self.video_player.set_volume(self.video_player._volume - 5))

    def _start_auto_save(self):
        self._save_timer = QTimer(self)
        self._save_timer.setInterval(SAVE_PROGRESS_INTERVAL_MS)
        self._save_timer.timeout.connect(self._save_progress)
        self._save_timer.start()

    def _set_page(self, index: int):
        self._previous_page_idx = self.stack.currentIndex()
        self.stack.setCurrentIndex(index)
        if index in (0, 1):
            self.top_nav.show()
            self._update_views()
        elif index == 2:
            self.top_nav.show()
            self._fill_browser_courses()
        elif index in (3, 4):
            self.top_nav.hide()

    # ════════════════════════════════════════════
    #  Data Updates
    # ════════════════════════════════════════════

    def _load_library(self):
        self._scan_library()

    def _scan_library(self):
        self._courses = self.video_library.scan()
        if self._courses:
            if self._current_course_idx >= len(self._courses):
                self._current_course_idx = 0

            # Prefer course with video lessons
            course = self._courses[self._current_course_idx]
            self._current_lessons = self.db.get_lessons_for_course(course.id)
            self._current_materials = self.db.get_materials_for_course(course.id)

            if not self._current_lessons:
                for idx, c in enumerate(self._courses):
                    c_lessons = self.db.get_lessons_for_course(c.id)
                    if c_lessons:
                        self._current_course_idx = idx
                        self._current_lessons = c_lessons
                        self._current_materials = self.db.get_materials_for_course(c.id)
                        break

            if self._selected_lesson_idx >= len(self._current_lessons):
                self._selected_lesson_idx = 0
        else:
            self._current_lessons = []
            self._current_materials = []

        self._update_views()
        self._fill_browser_courses()

    def _update_views(self):
        self._update_cinematic_view()
        self._update_editorial_view()

    def _update_cinematic_view(self):
        if not self._courses:
            self.hero_category.setText(t("offline_vault"))
            self.hero_title.setText(t("no_courses_title"))
            self.hero_desc.setText(t("no_courses_desc"))
            self.hero_play_btn.setEnabled(False)
            self.hero_materials_btn.setEnabled(False)
            return

        course = self._courses[self._current_course_idx]
        if not self._current_lessons:
            self._current_lessons = self.db.get_lessons_for_course(course.id)
        self._current_materials = self.db.get_materials_for_course(course.id)

        self.hero_materials_btn.setEnabled(len(self._current_materials) > 0)
        self.hero_badge_pdf.setVisible(len(self._current_materials) > 0)

        if not self._current_lessons:
            self.hero_title.setText(course.name)
            self.hero_desc.setText(t("no_lessons"))
            self.hero_play_btn.setEnabled(False)
            return

        current_lesson = self._current_lessons[self._selected_lesson_idx]
        self.hero_category.setText(f"{course.name.upper()} • LESSON {self._selected_lesson_idx + 1:02d}")
        self.hero_title.setText(current_lesson.title)
        self.hero_desc.setText(course.description or t("lesson_counter", current=self._selected_lesson_idx + 1, total=len(self._current_lessons), course=course.name))
        self.hero_play_btn.setEnabled(True)

        self.hero_badge_enc.setVisible(current_lesson.is_encrypted)
        pct = 0
        if current_lesson.duration_ms > 0:
            pct = int((current_lesson.last_position_ms / current_lesson.duration_ms) * 100)
        self.hero_badge_progress.setText(f"{pct}% {t('badge_completed')}" if pct > 0 else t("badge_ready"))

        total = len(self._current_lessons)
        self.carousel_counter.setText(f"{self._selected_lesson_idx + 1:02d} / {total:02d}")
        prev_idx = (self._selected_lesson_idx - 1) % total
        next_idx = (self._selected_lesson_idx + 1) % total
        self.prev_card_title.setText(self._current_lessons[prev_idx].title)
        self.prev_card_sub.setText(course.name)
        self.next_card_title.setText(self._current_lessons[next_idx].title)
        self.next_card_sub.setText(course.name)

    def _update_editorial_view(self):
        self.editorial_index_list.blockSignals(True)
        self.editorial_index_list.clear()

        if not self._courses:
            self.editorial_huge_title.setText(t("no_courses_title").upper())
            self.editorial_kicker.setText(t("kicker_default"))
            self.editorial_play_btn.setEnabled(False)
            self.editorial_pdf_btn.setEnabled(False)
            self.editorial_index_list.blockSignals(False)
            return

        course = self._courses[self._current_course_idx]
        if not self._current_lessons:
            self._current_lessons = self.db.get_lessons_for_course(course.id)
        self._current_materials = self.db.get_materials_for_course(course.id)

        self.editorial_pdf_btn.setEnabled(len(self._current_materials) > 0)

        for idx, ls in enumerate(self._current_lessons, start=1):
            text = f"{idx:02d}  {ls.title}"
            if ls.is_encrypted:
                text += " 🔒"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, idx - 1)
            self.editorial_index_list.addItem(item)
            if idx - 1 == self._selected_lesson_idx:
                self.editorial_index_list.setCurrentItem(item)

        self.editorial_index_list.blockSignals(False)

        if self._current_lessons:
            current_lesson = self._current_lessons[self._selected_lesson_idx]
            self.editorial_kicker.setText(f"{course.name.upper()} • EPISODE {self._selected_lesson_idx + 1:02d}")
            self.editorial_huge_title.setText(current_lesson.title.upper())
            self.editorial_desc.setText(course.description or t("lesson_counter", current=self._selected_lesson_idx + 1, total=len(self._current_lessons), course=course.name))
            self.editorial_play_btn.setEnabled(True)

    def _on_editorial_item_changed(self, current, _previous):
        if not current:
            return
        idx = current.data(Qt.ItemDataRole.UserRole)
        self._selected_lesson_idx = idx
        self._update_views()

    def _step_lesson(self, delta: int):
        if not self._current_lessons:
            return
        total = len(self._current_lessons)
        self._selected_lesson_idx = (self._selected_lesson_idx + delta) % total
        self._update_views()

    def _play_current_lesson(self):
        if not self._current_lessons:
            return
        lesson = self._current_lessons[self._selected_lesson_idx]
        self._play_lesson(lesson.id)

    # ════════════════════════════════════════════
    #  Browser Handlers
    # ════════════════════════════════════════════

    def _fill_browser_courses(self):
        self.course_list_widget.clear()
        for idx, c in enumerate(self._courses):
            lessons = self.db.get_lessons_for_course(c.id)
            materials = self.db.get_materials_for_course(c.id)
            mat_info = f", {len(materials)} PDF" if materials else ""
            item = QListWidgetItem(f"📚 {c.name}  ({len(lessons)} {t('lessons_label').lower()}{mat_info})")
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.course_list_widget.addItem(item)
            if idx == self._current_course_idx:
                self.course_list_widget.setCurrentItem(item)

    def _on_browser_course_selected(self, current, _previous):
        if not current:
            return
        self._current_course_idx = current.data(Qt.ItemDataRole.UserRole)
        course = self._courses[self._current_course_idx]
        self._current_lessons = self.db.get_lessons_for_course(course.id)
        self._current_materials = self.db.get_materials_for_course(course.id)
        self._fill_browser_lessons()
        self._fill_browser_materials()

    def _fill_browser_lessons(self):
        self.browser_lesson_list.clear()
        for idx, ls in enumerate(self._current_lessons):
            badges = []
            if ls.is_encrypted:
                badges.append("🔒")
            if ls.completed:
                badges.append("✅")
            elif ls.last_position_ms > 0:
                badges.append("⏳")
            badge_str = f"  {' '.join(badges)}" if badges else ""
            wi = QListWidgetItem(f"{ls.title}{badge_str}")
            wi.setData(Qt.ItemDataRole.UserRole, idx)
            self.browser_lesson_list.addItem(wi)

    def _fill_browser_materials(self):
        self.browser_material_list.clear()
        if not self._current_materials:
            wi = QListWidgetItem(f"ℹ {t('no_materials')}")
            wi.setFlags(Qt.ItemFlag.NoItemFlags)
            self.browser_material_list.addItem(wi)
            return

        for mat in self._current_materials:
            icon = "🔒 📄" if mat.is_encrypted else "📄"
            wi = QListWidgetItem(f"{icon} {mat.title}")
            wi.setData(Qt.ItemDataRole.UserRole, mat.id)
            self.browser_material_list.addItem(wi)

    def _on_browser_lesson_clicked(self, item):
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is not None and 0 <= idx < len(self._current_lessons):
            self._selected_lesson_idx = idx

    def _on_browser_lesson_activated(self, item):
        idx = item.data(Qt.ItemDataRole.UserRole)
        self._selected_lesson_idx = idx
        lesson = self._current_lessons[idx]
        self._play_lesson(lesson.id)

    def _open_material_by_id(self, mat_id: int):
        mat = self.db.get_material(mat_id)
        if not mat:
            return

        target_path = Path(mat.file_path)
        if not target_path.exists():
            from app.config import VIDEOS_DIR
            course = self.db.get_course(mat.course_id)
            if course:
                candidate = VIDEOS_DIR / course.folder_name / mat.filename
                if candidate.exists():
                    target_path = candidate
            if not target_path.exists():
                candidate = VIDEOS_DIR / mat.filename
                if candidate.exists():
                    target_path = candidate

        if not target_path.exists():
            QMessageBox.warning(self, "Error", f"Material not found:\n{mat.file_path}")
            return

        self._cleanup_pdf_temp()

        if mat.is_encrypted or self.encryption_mgr.is_encrypted_file(target_path):
            try:
                temp_path = self.encryption_mgr.decrypt_to_cache(target_path)
                self._active_pdf_temp_path = temp_path
                target_path = temp_path
            except Exception as e:
                QMessageBox.critical(self, "Decryption Error", f"Could not load protected document:\n{str(e)}")
                return

        self.pdf_viewer.load_pdf(str(target_path), mat.title)
        self._set_page(4)

    def _on_material_activated(self, item):
        mat_id = item.data(Qt.ItemDataRole.UserRole)
        if mat_id:
            self._open_material_by_id(mat_id)

    def _open_first_course_pdf(self):
        if self._current_materials:
            self._open_material_by_id(self._current_materials[0].id)
        else:
            self._set_page(2)

    def _cleanup_pdf_temp(self):
        if self._active_pdf_temp_path:
            self.encryption_mgr.remove_cache_file(self._active_pdf_temp_path)
            self._active_pdf_temp_path = None

    def _back_from_pdf(self):
        self.pdf_viewer.cleanup()
        self._cleanup_pdf_temp()
        prev = self._previous_page_idx if self._previous_page_idx not in (3, 4) else 2
        self._set_page(prev)

    def _show_continue_watching(self):
        items = self.video_manager.get_continue_watching()
        if not items:
            QMessageBox.information(self, t("continue_dialog_title"), t("continue_none"))
            return
        first = items[0]
        self._play_lesson(first["id"])

    # ════════════════════════════════════════════
    #  Playback & Decryption
    # ════════════════════════════════════════════

    def _play_lesson(self, lesson_id: int):
        self._save_progress()
        lesson = self.video_manager.load_lesson(lesson_id)
        if not lesson:
            return

        # Synchronize selected lesson index
        for idx, ls in enumerate(self._current_lessons):
            if ls.id == lesson_id:
                self._selected_lesson_idx = idx
                break

        try:
            playable_path = self.video_manager.prepare_playback_path(lesson)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load video:\n{str(e)}")
            return

        # Switch to cinema player (Page 3)
        self._set_page(3)

        # Update in-player playlist
        course = self._courses[self._current_course_idx] if self._courses else None
        course_name = course.name if course else ""
        self.video_player.set_playlist(
            lessons=self._current_lessons,
            current_lesson_id=lesson.id,
            course_name=course_name
        )

        self.video_player.load_video(
            file_path=str(playable_path),
            title=lesson.title,
            start_position_ms=lesson.last_position_ms,
            is_encrypted=lesson.is_encrypted,
        )

    def _play_previous_lesson(self):
        if not self._current_lessons:
            return
        if self.video_player.is_shuffle():
            if self._shuffle_history:
                self._selected_lesson_idx = self._shuffle_history.pop()
            else:
                self._selected_lesson_idx = (self._selected_lesson_idx - 1) % len(self._current_lessons)
        else:
            self._selected_lesson_idx = (self._selected_lesson_idx - 1) % len(self._current_lessons)
        lesson = self._current_lessons[self._selected_lesson_idx]
        self._play_lesson(lesson.id)

    def _play_next_lesson(self):
        if not self._current_lessons:
            return
        if self.video_player.is_shuffle():
            import random
            if len(self._current_lessons) > 1:
                self._shuffle_history.append(self._selected_lesson_idx)
                # Keep history bounded
                if len(self._shuffle_history) > 50:
                    self._shuffle_history.pop(0)
                candidates = [i for i in range(len(self._current_lessons)) if i != self._selected_lesson_idx]
                self._selected_lesson_idx = random.choice(candidates)
            else:
                self._selected_lesson_idx = 0
        else:
            self._selected_lesson_idx = (self._selected_lesson_idx + 1) % len(self._current_lessons)
        lesson = self._current_lessons[self._selected_lesson_idx]
        self._play_lesson(lesson.id)

    def _on_player_stopped(self):
        self._save_progress()
        self.video_manager.cleanup_active_temp_file()

    def _back_from_video_player(self):
        self._save_progress()
        self.video_player.cleanup()
        self.video_manager.cleanup_active_temp_file()
        self._back_to_current_skin()

    def _save_progress(self):
        if self.video_manager.current_lesson:
            pos = self.video_player.get_position()
            dur = self.video_player.get_duration()
            if pos > 0:
                self.video_manager.save_progress(pos, dur)

    def _on_playback_finished(self):
        if self.video_manager.current_lesson:
            self.video_manager.mark_completed()
            self._update_views()

        repeat_mode = self.video_player.get_repeat_mode()
        if repeat_mode == "one":
            self.video_player.seek_to(0)
            self.video_player.play()
        elif repeat_mode == "all":
            self._play_next_lesson()
        elif self.video_player.is_shuffle():
            self._play_next_lesson()
        else:
            # Off: play next if available, or stop at end of course
            if self._selected_lesson_idx + 1 < len(self._current_lessons):
                self._play_next_lesson()
            else:
                self.video_player.stop()

    def _toggle_fullscreen(self, enter: bool):
        if enter:
            self.top_nav.hide()
            self.video_player.top_bar.hide()
            self.showFullScreen()
            self.video_player.set_fullscreen(True)
        else:
            self.showNormal()
            if self.stack.currentIndex() not in (3, 4):
                self.top_nav.show()
            self.video_player.top_bar.show()
            self.video_player.set_fullscreen(False)

    def _open_notes_dialog(self, current_pos_ms: int):
        if not self.video_manager.current_lesson:
            return
        lesson = self.video_manager.current_lesson
        dlg = NotesDialog(self.db, lesson.id, lesson.title, current_pos_ms, self)
        dlg.seek_requested.connect(self.video_player.seek_to)
        dlg.exec()

    def _generate_certificate(self):
        if not self._courses:
            return
        course = self._courses[self._current_course_idx]
        student_name, ok = QInputDialog.getText(
            self,
            t("cert_title"),
            "Digite o Nome Completo para o Certificado:",
            text="Aluno Dedicado",
        )
        if not ok or not student_name.strip():
            return

        try:
            device_id = self.device_binding.get_device_id()
            cert_path = CertificateGenerator.generate(
                course_name=course.name,
                student_name=student_name.strip(),
                device_id=device_id,
            )
            QMessageBox.information(
                self,
                t("cert_title"),
                f"{t('cert_saved_msg')}\n{cert_path.name}",
            )
            # Open generated certificate in native PDF viewer
            self.pdf_viewer.load_pdf(str(cert_path), f"Certificado - {course.name}")
            self._set_page(4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Falha ao gerar certificado:\n{str(e)}")

    def _open_protect_dialog(self):
        auth_dlg = AdminAuthDialog(self.auth, self)
        if auth_dlg.exec() != QDialog.DialogCode.Accepted:
            return

        dlg = EncryptDialog(self.encryption_mgr, auth=self.auth, parent=self)
        dlg.exec()
        self._scan_library()

    def _open_about_dialog(self):
        """Display the rich-text dialog about Arthur Rwoud, Jose Leandro and Icescript contacts."""
        dlg = AboutDialog(self)
        dlg.exec()

    def closeEvent(self, event):
        self._save_progress()
        self.video_player.cleanup()
        self.pdf_viewer.cleanup()
        self._cleanup_pdf_temp()
        self.video_manager.cleanup_active_temp_file()
        event.accept()
