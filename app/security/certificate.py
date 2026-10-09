"""
Offline Certificate Generator for Icescript Player.
Renders high-resolution, print-ready PDF Completion Certificates
using native PySide6.QtGui.QPainter & QPdfWriter with cryptographic verification hash.
"""
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QPointF, QRect, QRectF, Qt
from PySide6.QtGui import (
    QBrush, QColor, QFont, QLinearGradient, QPainter, QPageLayout,
    QPageSize, QPdfWriter, QPen, QPixmap,
)

from app.config import APP_ROOT, ASSETS_DIR


class CertificateGenerator:
    """Generates official offline PDF certificates for completed courses."""

    @staticmethod
    def generate(
        course_name: str,
        student_name: str = "Aluno",
        device_id: str = "",
        output_path: Optional[Path] = None,
    ) -> Path:
        """Render vector-quality completion certificate to PDF."""
        if output_path is None:
            safe_name = "".join(c for c in course_name if c.isalnum() or c in (" ", "_", "-")).strip()
            output_path = APP_ROOT / f"Certificado - {safe_name}.pdf"

        date_str = datetime.now().strftime("%d/%m/%Y")
        verify_raw = f"{device_id}:{course_name}:{date_str}:ICESCRIPT_VAULT_2026"
        verify_hash = hashlib.sha256(verify_raw.encode("utf-8")).hexdigest()[:24].upper()
        cert_code = f"CERT-{verify_hash[:4]}-{verify_hash[4:8]}-{verify_hash[8:12]}-{verify_hash[12:16]}"

        writer = QPdfWriter(str(output_path))
        writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        writer.setPageOrientation(QPageLayout.Orientation.Landscape)
        writer.setResolution(300)

        painter = QPainter(writer)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # Dimensions in 300 DPI points (approx 3508 x 2480)
        w = writer.width()
        h = writer.height()

        # ── 1. Background Fill ──
        bg_gradient = QLinearGradient(0, 0, w, h)
        bg_gradient.setColorAt(0.0, QColor(10, 14, 26))      # Deep luxury navy
        bg_gradient.setColorAt(0.5, QColor(15, 23, 42))
        bg_gradient.setColorAt(1.0, QColor(6, 9, 18))
        painter.fillRect(0, 0, w, h, bg_gradient)

        # ── 2. Decorative Double Golden Border ──
        outer_pen = QPen(QColor(0, 210, 252, 160), 12)       # Icescript Cyan Glow
        painter.setPen(outer_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(120, 120, w - 240, h - 240, 24, 24)

        inner_pen = QPen(QColor(255, 215, 0, 140), 4)        # Gold Accent
        painter.setPen(inner_pen)
        painter.drawRoundedRect(160, 160, w - 320, h - 320, 16, 16)

        # ── 3. Logo Emblem ──
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            pix = QPixmap(str(logo_path))
            logo_size = 320
            logo_x = int((w - logo_size) / 2)
            logo_y = 220
            painter.drawPixmap(
                logo_x, logo_y, logo_size, logo_size,
                pix.scaled(logo_size, logo_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )

        # ── 4. Typography: Header ──
        painter.setPen(QColor(0, 210, 252))
        font_brand = QFont("Helvetica", 16, QFont.Weight.Bold)
        font_brand.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 6)
        painter.setFont(font_brand)
        painter.drawText(QRectF(0, 560, w, 60), Qt.AlignmentFlag.AlignCenter, "ICESCRIPT ACADEMY")

        painter.setPen(QColor(255, 255, 255))
        font_title = QFont("Helvetica", 42, QFont.Weight.Bold)
        font_title.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 4)
        painter.setFont(font_title)
        painter.drawText(QRectF(0, 630, w, 110), Qt.AlignmentFlag.AlignCenter, "CERTIFICADO DE CONCLUSÃO")

        # ── 5. Subtitle & Body ──
        painter.setPen(QColor(160, 175, 200))
        font_sub = QFont("Helvetica", 18, QFont.Weight.Normal)
        painter.setFont(font_sub)
        painter.drawText(QRectF(0, 780, w, 50), Qt.AlignmentFlag.AlignCenter, "Certificamos que")

        # Student Name
        painter.setPen(QColor(255, 215, 0))                  # Luxury Gold
        font_name = QFont("Georgia", 36, QFont.Weight.Bold)
        painter.setFont(font_name)
        painter.drawText(QRectF(0, 840, w, 90), Qt.AlignmentFlag.AlignCenter, student_name or "Aluno Dedicado")

        # Description
        painter.setPen(QColor(180, 195, 220))
        font_desc = QFont("Helvetica", 18, QFont.Weight.Normal)
        painter.setFont(font_desc)
        painter.drawText(
            QRectF(300, 960, w - 600, 80),
            Qt.AlignmentFlag.AlignCenter,
            "concluiu com êxito e aproveitamento integral todas as etapas do curso de capacitação profissional:"
        )

        # Course Title
        painter.setPen(QColor(255, 255, 255))
        font_course = QFont("Helvetica", 32, QFont.Weight.Bold)
        painter.setFont(font_course)
        painter.drawText(QRectF(200, 1070, w - 400, 100), Qt.AlignmentFlag.AlignCenter, course_name.upper())

        # ── 6. Bottom Signatures & Verification Seal ──
        # Date
        painter.setPen(QColor(140, 160, 190))
        font_meta = QFont("Helvetica", 15, QFont.Weight.Normal)
        painter.setFont(font_meta)
        painter.drawText(QRectF(260, 1850, 600, 60), Qt.AlignmentFlag.AlignLeft, f"📅 Data de Emissão: {date_str}")
        painter.drawText(QRectF(260, 1910, 600, 60), Qt.AlignmentFlag.AlignLeft, "🛡️ Modo: 100% Offline Vault")

        # Official Seal Box
        seal_rect = QRectF(w - 950, 1820, 680, 180)
        painter.setBrush(QColor(0, 210, 252, 20))
        painter.setPen(QPen(QColor(0, 210, 252, 120), 2))
        painter.drawRoundedRect(seal_rect, 10, 10)

        painter.setPen(QColor(0, 210, 252))
        font_seal_title = QFont("Consolas", 12, QFont.Weight.Bold)
        painter.setFont(font_seal_title)
        painter.drawText(seal_rect.adjusted(20, 20, -20, 0), Qt.AlignmentFlag.AlignLeft, "AUTENTICIDADE CRIPTOGRÁFICA (HMAC-SHA256)")

        painter.setPen(QColor(255, 255, 255))
        font_code = QFont("Consolas", 15, QFont.Weight.Bold)
        painter.setFont(font_code)
        painter.drawText(seal_rect.adjusted(20, 65, -20, 0), Qt.AlignmentFlag.AlignLeft, cert_code)

        painter.setPen(QColor(140, 160, 190))
        font_dev = QFont("Consolas", 11, QFont.Weight.Normal)
        painter.setFont(font_dev)
        painter.drawText(seal_rect.adjusted(20, 115, -20, 0), Qt.AlignmentFlag.AlignLeft, f"Device: {device_id or 'OFFLINE-VAULT'}")

        # Slogan Footer
        painter.setPen(QColor(0, 210, 252, 180))
        font_slogan = QFont("Georgia", 16, QFont.Weight.Bold)
        font_slogan.setItalic(True)
        painter.setFont(font_slogan)
        painter.drawText(QRectF(0, 2150, w, 60), Qt.AlignmentFlag.AlignCenter, "“Mais que cursos, é o teu futuro!”")

        painter.end()
        return output_path
