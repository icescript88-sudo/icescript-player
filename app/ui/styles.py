"""
Theme stylesheets for Icescript Player.
- Skin 1: CINEMATIC (HBO / Streaming Dashboard style)
- Skin 2: EDITORIAL (DC Comics / Poster Grid style with vertical numbered rail)
"""

CINEMATIC_THEME = """
/* ═══════════════ Global ═══════════════ */
QWidget {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', Roboto, sans-serif;
    font-size: 14px;
}

QMainWindow {
    background-color: #0b0f19;
}

/* ═══════════════ Top Navigation Bar ═══════════════ */
QFrame#top_nav {
    background-color: rgba(11, 15, 25, 0.95);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 8px 24px;
}

QLabel#brand_logo {
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 3px;
    color: #ffffff;
    background: transparent;
}

QLabel#brand_tag {
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1.5px;
    color: #00d2fc;
    background: transparent;
    padding-left: 4px;
}

QPushButton#nav_tab {
    background-color: transparent;
    color: #8a99ad;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    border: none;
    border-radius: 4px;
    padding: 8px 14px;
    text-transform: uppercase;
}

QPushButton#nav_tab:hover {
    color: #ffffff;
}

QPushButton#nav_action_btn {
    background-color: #ffffff;
    color: #0b0f19;
    font-weight: 800;
    font-size: 12px;
    letter-spacing: 1px;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
}

QPushButton#nav_action_btn:hover {
    background-color: #00d2fc;
    color: #0b0f19;
}

QPushButton#nav_skin_btn {
    background-color: rgba(0, 210, 252, 0.12);
    color: #00d2fc;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 1px;
    border: 1px solid rgba(0, 210, 252, 0.35);
    border-radius: 6px;
    padding: 8px 14px;
}

QPushButton#nav_skin_btn:hover {
    background-color: #00d2fc;
    color: #0b0f19;
}

QPushButton#nav_icon_btn {
    background-color: transparent;
    color: #8a99ad;
    font-size: 16px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    padding: 0;
}

QPushButton#nav_icon_btn:hover {
    color: #ffffff;
    border-color: #00d2fc;
    background-color: rgba(0, 210, 252, 0.1);
}

/* ═══════════════ Hero Presentation Area ═══════════════ */
QFrame#hero_stage {
    background: qradialgradient(cx: 0.65, cy: 0.4, radius: 0.9,
        fx: 0.6, fy: 0.35,
        stop: 0 #1b2838,
        stop: 0.45 #101826,
        stop: 1 #080c14);
}

QLabel#hero_badge {
    color: #8a99ad;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    background: transparent;
}

QLabel#hero_title {
    color: #ffffff;
    font-size: 42px;
    font-weight: 900;
    letter-spacing: -0.5px;
    background: transparent;
}

QLabel#hero_desc {
    color: #94a3b8;
    font-size: 15px;
    line-height: 1.5;
    background: transparent;
}

QPushButton#hero_play_btn {
    background-color: #00d2fc;
    color: #080c14;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.5px;
    border: none;
    border-radius: 26px;
    padding: 12px 32px;
    min-height: 48px;
}

QPushButton#hero_play_btn:hover {
    background-color: #38bdf8;
    color: #000000;
}

QPushButton#hero_secondary_btn {
    background-color: rgba(255, 255, 255, 0.08);
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 24px;
    padding: 12px 24px;
    min-height: 48px;
}

QPushButton#hero_secondary_btn:hover {
    background-color: rgba(255, 255, 255, 0.16);
    border-color: rgba(255, 255, 255, 0.3);
}

/* ═══════════════ Bottom Carousel / Switcher ═══════════════ */
QFrame#carousel_bar {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(11, 15, 25, 0.7),
        stop: 1 rgba(7, 10, 18, 0.98));
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding: 14px 28px;
}

QFrame#card_widget {
    background-color: rgba(22, 30, 46, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 10px 14px;
}

QFrame#card_widget:hover {
    background-color: rgba(30, 42, 64, 0.9);
    border-color: rgba(0, 210, 252, 0.4);
}

QPushButton#circle_arrow_btn {
    background-color: #ffffff;
    color: #0b0f19;
    font-size: 15px;
    font-weight: bold;
    border: none;
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
}

QPushButton#circle_arrow_btn:hover {
    background-color: #00d2fc;
    color: #000000;
}

/* ═══════════════ Video Player Controls ═══════════════ */
QVideoWidget {
    background-color: #000000;
}

QFrame#vlc_controls_bar {
    background-color: #141923;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    padding: 6px 14px 8px 14px;
}

QPushButton.vlc_btn {
    background-color: rgba(255, 255, 255, 0.06);
    color: #e2e8f0;
    font-size: 13px;
    font-weight: bold;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 4px;
    min-width: 32px;
    max-width: 32px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
}

QPushButton.vlc_btn:hover {
    background-color: rgba(255, 255, 255, 0.16);
    border-color: rgba(255, 255, 255, 0.45);
    color: #ffffff;
}

QPushButton.vlc_btn:pressed {
    background-color: rgba(255, 255, 255, 0.28);
    border-color: #00d2fc;
}

QPushButton.vlc_btn_active {
    background-color: rgba(0, 210, 252, 0.22);
    border: 1px solid #00d2fc;
    color: #00d2fc;
}

QPushButton.vlc_btn_active:hover {
    background-color: rgba(0, 210, 252, 0.35);
    color: #ffffff;
}

QPushButton#vlc_play_btn {
    background-color: rgba(255, 255, 255, 0.08);
    color: #ffffff;
    font-size: 15px;
    font-weight: bold;
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 4px;
    min-width: 38px;
    max-width: 38px;
    min-height: 28px;
    max-height: 28px;
}

QPushButton#vlc_play_btn:hover {
    background-color: rgba(0, 210, 252, 0.25);
    border-color: #00d2fc;
    color: #00d2fc;
}

QPushButton.vlc_jump_btn {
    background: transparent;
    color: #94a3b8;
    font-size: 12px;
    font-weight: bold;
    border: none;
    min-width: 22px;
    max-width: 22px;
    min-height: 20px;
    max-height: 20px;
}

QPushButton.vlc_jump_btn:hover {
    color: #ffffff;
}

QSlider#vlc_seek_slider::groove:horizontal {
    background: rgba(255, 255, 255, 0.16);
    height: 5px;
    border-radius: 2px;
}

QSlider#vlc_seek_slider::sub-page:horizontal {
    background: #00d2fc;
    border-radius: 2px;
}

QSlider#vlc_seek_slider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #94a3b8;
    width: 10px;
    height: 14px;
    margin: -5px 0;
    border-radius: 2px;
}

QSlider#vlc_seek_slider::handle:horizontal:hover {
    background: #00d2fc;
    border-color: #ffffff;
}

QSlider#vlc_volume_slider::groove:horizontal {
    background: rgba(255, 255, 255, 0.16);
    height: 6px;
    border-radius: 3px;
}

QSlider#vlc_volume_slider::sub-page:horizontal {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #22c55e,
        stop: 0.65 #84cc16,
        stop: 0.82 #eab308,
        stop: 1.0 #ef4444);
    border-radius: 3px;
}

QSlider#vlc_volume_slider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #94a3b8;
    width: 10px;
    height: 14px;
    margin: -4px 0;
    border-radius: 2px;
}

QLabel#vlc_status_box, QPushButton#vlc_speed_box {
    background-color: rgba(0, 0, 0, 0.35);
    color: #cbd5e1;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    font-weight: bold;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 3px;
    padding: 3px 6px;
}

QPushButton#vlc_speed_box:hover, QLabel#vlc_status_box:hover {
    border-color: #00d2fc;
    color: #ffffff;
    background-color: rgba(0, 210, 252, 0.1);
}

QFrame#vlc_playlist_drawer {
    background-color: #0e131d;
    border-left: 1px solid rgba(255, 255, 255, 0.12);
}

QLineEdit#vlc_search_input {
    background-color: rgba(255, 255, 255, 0.06);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}

QLineEdit#vlc_search_input:focus {
    border-color: #00d2fc;
    background-color: rgba(0, 210, 252, 0.05);
}

/* Fallback for classic controls */
QFrame#player_controls_bar {
    background-color: rgba(11, 15, 25, 0.95);
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding: 8px 18px;
}

QListWidget {
    background-color: rgba(15, 21, 33, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 6px;
}

QListWidget::item {
    padding: 12px 14px;
    border-radius: 8px;
    margin: 3px 0;
    color: #cbd5e1;
}

QListWidget::item:selected {
    background-color: rgba(0, 210, 252, 0.18);
    color: #ffffff;
    border-left: 3px solid #00d2fc;
}
"""

EDITORIAL_THEME = """
/* ═══════════════ EDITORIAL SKIN (DC Comics / Poster Style) ═══════════════ */
QWidget {
    background-color: #12151c;
    color: #e6edf3;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', 'Cinzel', serif;
    font-size: 14px;
}

QMainWindow {
    background-color: #12151c;
}

QFrame#top_nav {
    background-color: rgba(18, 21, 28, 0.96);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding: 10px 32px;
}

QLabel#brand_logo {
    font-size: 22px;
    font-weight: 900;
    letter-spacing: 4px;
    color: #ffffff;
    background: transparent;
}

QLabel#brand_tag {
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 2px;
    color: #00f0ff;
    background: transparent;
}

QPushButton#nav_tab {
    background-color: transparent;
    color: #94a3b8;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1.5px;
    border: none;
    padding: 8px 16px;
    text-transform: capitalize;
}

QPushButton#nav_tab:hover {
    color: #ffffff;
}

QPushButton#nav_action_btn {
    background-color: #00f0ff;
    color: #0f141c;
    font-weight: 800;
    font-size: 12px;
    letter-spacing: 1.5px;
    border: none;
    border-radius: 4px;
    padding: 8px 20px;
}

QPushButton#nav_skin_btn {
    background-color: rgba(255, 255, 255, 0.08);
    color: #ffffff;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 1px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    padding: 8px 14px;
}

QPushButton#nav_skin_btn:hover {
    background-color: rgba(255, 255, 255, 0.16);
}

/* ═══════════════ Editorial Rail & Stage ═══════════════ */
QFrame#editorial_rail {
    background-color: rgba(14, 17, 24, 0.98);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    padding: 30px 18px;
}

QFrame#editorial_stage {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #121620,
        stop: 0.5 #18202d,
        stop: 1 #0f131a);
}

QLabel#kicker_label {
    color: #c9a86a;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 8px;
    text-transform: uppercase;
    background: transparent;
}

QLabel#huge_editorial_title {
    color: #ffffff;
    font-size: 56px;
    font-weight: 900;
    letter-spacing: 1px;
    background: transparent;
    text-transform: uppercase;
}

QPushButton#editorial_play_btn {
    background-color: #ffffff;
    color: #12151c;
    font-size: 15px;
    font-weight: 900;
    letter-spacing: 2px;
    border: none;
    border-radius: 4px;
    padding: 14px 36px;
}

QPushButton#editorial_play_btn:hover {
    background-color: #00f0ff;
    color: #000000;
}

/* ═══════════════ Video Player & VLC Controls ═══════════════ */
QVideoWidget {
    background-color: #000000;
}

QFrame#vlc_controls_bar {
    background-color: #121620;
    border-top: 1px solid rgba(255, 255, 255, 0.10);
    padding: 6px 14px 8px 14px;
}

QPushButton.vlc_btn {
    background-color: rgba(255, 255, 255, 0.05);
    color: #e2e8f0;
    font-size: 13px;
    font-weight: bold;
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 4px;
    min-width: 32px;
    max-width: 32px;
    min-height: 28px;
    max-height: 28px;
    padding: 0;
}

QPushButton.vlc_btn:hover {
    background-color: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.4);
    color: #ffffff;
}

QPushButton.vlc_btn:pressed {
    background-color: rgba(255, 255, 255, 0.25);
    border-color: #00f0ff;
}

QPushButton.vlc_btn_active {
    background-color: rgba(0, 240, 255, 0.22);
    border: 1px solid #00f0ff;
    color: #00f0ff;
}

QPushButton.vlc_btn_active:hover {
    background-color: rgba(0, 240, 255, 0.35);
    color: #ffffff;
}

QPushButton#vlc_play_btn {
    background-color: rgba(255, 255, 255, 0.08);
    color: #ffffff;
    font-size: 15px;
    font-weight: bold;
    border: 1px solid rgba(255, 255, 255, 0.26);
    border-radius: 4px;
    min-width: 38px;
    max-width: 38px;
    min-height: 28px;
    max-height: 28px;
}

QPushButton#vlc_play_btn:hover {
    background-color: rgba(0, 240, 255, 0.25);
    border-color: #00f0ff;
    color: #00f0ff;
}

QPushButton.vlc_jump_btn {
    background: transparent;
    color: #94a3b8;
    font-size: 12px;
    font-weight: bold;
    border: none;
    min-width: 22px;
    max-width: 22px;
    min-height: 20px;
    max-height: 20px;
}

QPushButton.vlc_jump_btn:hover {
    color: #ffffff;
}

QSlider#vlc_seek_slider::groove:horizontal {
    background: rgba(255, 255, 255, 0.15);
    height: 5px;
    border-radius: 2px;
}

QSlider#vlc_seek_slider::sub-page:horizontal {
    background: #00f0ff;
    border-radius: 2px;
}

QSlider#vlc_seek_slider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #94a3b8;
    width: 10px;
    height: 14px;
    margin: -5px 0;
    border-radius: 2px;
}

QSlider#vlc_seek_slider::handle:horizontal:hover {
    background: #00f0ff;
    border-color: #ffffff;
}

QSlider#vlc_volume_slider::groove:horizontal {
    background: rgba(255, 255, 255, 0.15);
    height: 6px;
    border-radius: 3px;
}

QSlider#vlc_volume_slider::sub-page:horizontal {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #22c55e,
        stop: 0.65 #84cc16,
        stop: 0.82 #eab308,
        stop: 1.0 #ef4444);
    border-radius: 3px;
}

QSlider#vlc_volume_slider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #94a3b8;
    width: 10px;
    height: 14px;
    margin: -4px 0;
    border-radius: 2px;
}

QLabel#vlc_status_box, QPushButton#vlc_speed_box {
    background-color: rgba(0, 0, 0, 0.35);
    color: #cbd5e1;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    font-weight: bold;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 3px;
    padding: 3px 6px;
}

QPushButton#vlc_speed_box:hover, QLabel#vlc_status_box:hover {
    border-color: #00f0ff;
    color: #ffffff;
    background-color: rgba(0, 240, 255, 0.1);
}

QFrame#vlc_playlist_drawer {
    background-color: #0d1017;
    border-left: 1px solid rgba(255, 255, 255, 0.10);
}

QLineEdit#vlc_search_input {
    background-color: rgba(255, 255, 255, 0.06);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}

QLineEdit#vlc_search_input:focus {
    border-color: #00f0ff;
    background-color: rgba(0, 240, 255, 0.05);
}

QSlider::groove:horizontal {
    background: rgba(255, 255, 255, 0.15);
    height: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}

QSlider::sub-page:horizontal {
    background: #00f0ff;
}

QListWidget {
    background-color: #0e1118;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 4px;
    padding: 4px;
}

QListWidget::item {
    padding: 12px 14px;
    margin: 2px 0;
    color: #94a3b8;
}

QListWidget::item:selected {
    background-color: rgba(255, 255, 255, 0.08);
    color: #ffffff;
    border-left: 3px solid #00f0ff;
}
"""

THEMES = {
    "cinematic": CINEMATIC_THEME,
    "editorial": EDITORIAL_THEME,
}

DARK_THEME = CINEMATIC_THEME
