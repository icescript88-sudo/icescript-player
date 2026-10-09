"""
Generate application icons (icon.png and icon.ico) for Icescript Player.
Uses PySide6 QPainter for vector rendering with antialiasing.
"""
from pathlib import Path
from PySide6.QtGui import QImage, QPainter, QColor, QLinearGradient, QPainterPath, QPolygonF, QPen
from PySide6.QtCore import Qt, QPointF

from app.config import ASSETS_DIR


def generate_icon(size: int = 256) -> QImage:
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    margin = size * 0.06
    rect_size = size - (margin * 2)

    # Outer rounded square with icy dark blue / cyan border
    bg_gradient = QLinearGradient(margin, margin, margin + rect_size, margin + rect_size)
    bg_gradient.setColorAt(0.0, QColor("#0d1b2a"))
    bg_gradient.setColorAt(0.5, QColor("#1b263b"))
    bg_gradient.setColorAt(1.0, QColor("#0d1b2a"))

    path = QPainterPath()
    path.addRoundedRect(margin, margin, rect_size, rect_size, size * 0.22, size * 0.22)
    painter.fillPath(path, bg_gradient)

    # Glowing Cyan Border
    border_pen = QPen(QColor("#00d2fc"), size * 0.03)
    painter.strokePath(path, border_pen)

    # Ice crystal diamond / play triangle in center
    play_gradient = QLinearGradient(size * 0.35, size * 0.25, size * 0.75, size * 0.75)
    play_gradient.setColorAt(0.0, QColor("#ffffff"))
    play_gradient.setColorAt(0.3, QColor("#00d2fc"))
    play_gradient.setColorAt(1.0, QColor("#0077b6"))

    # Play triangle
    p1 = QPointF(size * 0.38, size * 0.28)
    p2 = QPointF(size * 0.74, size * 0.50)
    p3 = QPointF(size * 0.38, size * 0.72)

    play_path = QPainterPath()
    play_path.moveTo(p1)
    play_path.lineTo(p2)
    play_path.lineTo(p3)
    play_path.closeSubpath()

    painter.fillPath(play_path, play_gradient)

    # Accent shine
    shine_pen = QPen(QColor(255, 255, 255, 180), size * 0.015)
    painter.strokePath(play_path, shine_pen)

    painter.end()
    return img


def main():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    png_path = ASSETS_DIR / "icon.png"
    ico_path = ASSETS_DIR / "icon.ico"

    # Generate 256x256 PNG
    img256 = generate_icon(256)
    img256.save(str(png_path), "PNG")
    print(f"Generated: {png_path}")

    # Generate ICO file with standard icon sizes
    try:
        from PIL import Image
        pil_img = Image.open(str(png_path))
        pil_img.save(str(ico_path), format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print(f"Generated multi-res ICO with Pillow: {ico_path}")
    except ImportError:
        # If pillow is not installed, QImage can save .ico directly
        img256.save(str(ico_path), "ICO")
        print(f"Generated ICO with Qt: {ico_path}")


if __name__ == "__main__":
    main()
