"""
About Dialog for Icescript Player.
Displays information about the project creators, collaboration, and official contacts.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon

from app.config import ASSETS_DIR, APP_NAME, APP_VERSION


class AboutDialog(QDialog):
    """Bilingual modern rich-text dialog introducing Arthur Rwoud and Jose Leandro."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Sobre os Criadores — {APP_NAME}")
        self.setFixedSize(560, 640)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b1118;
                color: #e2e8f0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            QLabel {
                color: #e2e8f0;
            }
            QFrame#card {
                background-color: #131d2a;
                border: 1px solid #1e293b;
                border-radius: 12px;
                padding: 16px;
            }
            QPushButton#close_btn {
                background-color: #0077b6;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
            }
            QPushButton#close_btn:hover {
                background-color: #0096c7;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        self._build_ui()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(14)

        # Scrollable container for smooth viewing
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(4, 4, 4, 4)

        # Header with Logo
        header_box = QHBoxLayout()
        logo_path = ASSETS_DIR / "logo_small.png"
        if not logo_path.exists():
            logo_path = ASSETS_DIR / "icon.png"
        if logo_path.exists():
            logo_lbl = QLabel()
            pix = QPixmap(str(logo_path)).scaled(
                48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pix)
            header_box.addWidget(logo_lbl)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        h_title = QLabel(f"<b style='font-size: 20px; color: #00d2fc;'>{APP_NAME}</b>")
        h_sub = QLabel(f"<span style='color: #94a3b8; font-size: 13px;'>Versão {APP_VERSION} • Plataforma de Cursos Privada & Segura</span>")
        title_box.addWidget(h_title)
        title_box.addWidget(h_sub)
        header_box.addLayout(title_box)
        header_box.addStretch()
        layout.addLayout(header_box)

        # Card 1: Criadores
        card_creators = QFrame()
        card_creators.setObjectName("card")
        c_layout = QVBoxLayout(card_creators)
        c_layout.setSpacing(12)

        title_creators = QLabel("<b style='font-size: 16px; color: #38bdf8;'>👥 Conheça os Criadores</b>")
        c_layout.addWidget(title_creators)

        # Arthur
        arthur_text = QLabel("""
        <b>👨‍💻 Arthur Rwoud</b> — <i>Criador & Fundador da Icescript</i><br>
        <span style='color: #cbd5e1; font-size: 13px;'>
        Idealizador do Icescript Player e responsável por arquitetar as soluções de criptografia, 
        segurança de conteúdo e desenvolvimento de software da marca.
        </span>
        """)
        arthur_text.setWordWrap(True)
        c_layout.addWidget(arthur_text)

        # Divisor suave
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color: #1e293b;")
        c_layout.addWidget(div)

        # Leandro
        leandro_text = QLabel("""
        <b>🤝 José Leandro</b> — <i>Colaborador de Desenvolvimento</i><br>
        <span style='color: #cbd5e1; font-size: 13px;'>
        Parceiro fundamental no desenvolvimento, colaborando ativamente na usabilidade, 
        estabilidade e experiência do aluno.
        </span>
        """)
        leandro_text.setWordWrap(True)
        c_layout.addWidget(leandro_text)

        layout.addWidget(card_creators)

        # Card 2: Contatos e Links Úteis
        card_links = QFrame()
        card_links.setObjectName("card")
        l_layout = QVBoxLayout(card_links)
        l_layout.setSpacing(10)

        title_links = QLabel("<b style='font-size: 16px; color: #38bdf8;'>🔗 Contato & Suporte Oficial</b>")
        l_layout.addWidget(title_links)

        contact_html = """
        <div style='font-size: 13px; line-height: 1.8; color: #e2e8f0;'>
            🌐 <b>Site Oficial:</b> <a style='color: #38bdf8; text-decoration: none;' href='https://icescript.netlify.app/'>icescript.netlify.app</a><br>
            📱 <b>WhatsApp Suporte:</b> <span style='color: #22c55e; font-weight: bold;'>+244 935 935 960</span><br>
            📘 <b>Facebook:</b> <a style='color: #38bdf8; text-decoration: none;' href='https://web.facebook.com/ArthurRwoud/'>Perfil do Arthur Rwoud</a><br>
            ✉️ <b>E-mails:</b> <span style='color: #cbd5e1;'>icescript88@gmail.com</span> | <span style='color: #cbd5e1;'>felisminoartur5@gmail.com</span>
        </div>
        """
        contact_lbl = QLabel(contact_html)
        contact_lbl.setOpenExternalLinks(True)
        contact_lbl.setWordWrap(True)
        l_layout.addWidget(contact_lbl)

        layout.addWidget(card_links)

        scroll.setWidget(container)
        root_layout.addWidget(scroll)

        # Bottom Close Button
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        close_btn = QPushButton("Fechar")
        close_btn.setObjectName("close_btn")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)
        root_layout.addLayout(btn_box)
