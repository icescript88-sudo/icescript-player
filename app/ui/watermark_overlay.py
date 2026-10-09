"""
Dynamic Anti-Piracy Watermark Overlay.
Renders floating, semi-transparent student Hardware ID and forensic tags
over video playback surfaces and PDF handouts to deter unauthorized screen recording.
"""
import random
from typing import Optional

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRect, QPoint, QEvent
from PySide6.QtGui import QPainter, QColor, QFont, QPen


class WatermarkOverlay(QWidget):
    """Transparent click-through overlay that paints a floating dynamic watermark."""

    def __init__(self, device_id: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.device_id = device_id or "ICESCRIPT-SECURE-VAULT"
        self._pos_x = 40
        self._pos_y = 60
        self._opacity = 0.28   # 28% opacity: legible on camera/screen record, non-intrusive for study

        # Make fully transparent to mouse/touch events
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        if parent:
            parent.installEventFilter(self)
            self.resize(parent.size())

        # Timer to periodically change watermark position
        self._move_timer = QTimer(self)
        self._move_timer.setInterval(18_000)  # Move every 18 seconds
        self._move_timer.timeout.connect(self._reposition_watermark)
        self._move_timer.start()

        self._reposition_watermark()

    def set_device_id(self, device_id: str):
        """Update displayed device or student identifier."""
        self.device_id = device_id
        self.update()

    def _reposition_watermark(self):
        """Pick a new randomized quadrant or position inside the visible surface."""
        w = max(100, self.width() - 320)
        h = max(60, self.height() - 80)
        self._pos_x = random.randint(30, max(35, w))
        self._pos_y = random.randint(40, max(45, h))
        self.update()

    def eventFilter(self, watched, event):
        """Ensure overlay follows parent dimensions."""
        if watched == self.parent() and event.type() == QEvent.Type.Resize:
            self.resize(watched.size())
            self._reposition_watermark()
        return super().eventFilter(watched, event)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ── 1. Subtle Faint Center Diagonal Mark (Extra forensic layer) ──
        center_w = self.width()
        center_h = self.height()
        if center_w > 200 and center_h > 150:
            painter.save()
            painter.translate(center_w / 2, center_h / 2)
            painter.rotate(-22)
            faint_color = QColor(255, 255, 255, int(255 * 0.08))  # 8% faint center
            painter.setPen(faint_color)
            font_diag = QFont("Consolas", 14, QFont.Weight.Bold)
            font_diag.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
            painter.setFont(font_diag)
            text_diag = f"ICESCRIPT SECURE VAULT  •  {self.device_id}"
            painter.drawText(-220, 0, text_diag)
            painter.restore()

        # ── 2. Floating Dynamic Badge (Changes location) ──
        badge_text = f"ID: {self.device_id}"
        badge_font = QFont("Consolas", 11, QFont.Weight.Bold)
        painter.setFont(badge_font)

        metrics = painter.fontMetrics()
        text_w = metrics.horizontalAdvance(badge_text)
        text_h = metrics.height()
        pad_x = 12
        pad_y = 6
        rect_w = text_w + (pad_x * 2)
        rect_h = text_h + (pad_y * 2)

        # Draw semi-transparent pill backdrop
        bg_color = QColor(0, 0, 0, int(255 * (self._opacity * 0.75)))
        border_color = QColor(0, 210, 252, int(255 * (self._opacity * 0.6)))
        painter.setBrush(bg_color)
        painter.setPen(QPen(border_color, 1))
        pill_rect = QRect(self._pos_x, self._pos_y, rect_w, rect_h)
        painter.drawRoundedRect(pill_rect, 6, 6)

        # Draw text with high-contrast glow
        text_color = QColor(255, 255, 255, int(255 * self._opacity))
        painter.setPen(text_color)
        painter.drawText(
            self._pos_x + pad_x,
            self._pos_y + pad_y + metrics.ascent(),
            badge_text,
        )
        painter.end()
