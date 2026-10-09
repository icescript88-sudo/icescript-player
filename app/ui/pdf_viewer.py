"""
Native PDF Viewer for Icescript Player.
Provides hardware-accelerated, offline PDF reading for course handouts,
slides, exercises, and supplementary materials.
Uses PySide6.QtPdf and PySide6.QtPdfWidgets.
"""
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView

from app.ui.i18n import t


class PdfViewer(QWidget):
    """Integrated, dark-themed PDF Viewer widget."""

    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._document = QPdfDocument(self)
        self._current_page = 0
        self._zoom_factor = 1.0

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Top Bar ──
        self.top_bar = QFrame()
        self.top_bar.setStyleSheet(
            "background-color: rgba(11, 15, 25, 0.98); padding: 8px 16px; border-bottom: 1px solid rgba(255,255,255,0.08);"
        )
        tb_layout = QHBoxLayout(self.top_bar)
        tb_layout.setContentsMargins(0, 0, 0, 0)
        tb_layout.setSpacing(12)

        # Back button
        self.back_btn = QPushButton(t("player_browser_btn"))
        self.back_btn.setObjectName("nav_tab")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        tb_layout.addWidget(self.back_btn)

        tb_layout.addSpacing(12)

        # Document Title
        self.title_label = QLabel("Document Viewer")
        self.title_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; background: transparent;")
        tb_layout.addWidget(self.title_label)

        tb_layout.addStretch()

        # Page navigation controls
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setObjectName("ctrl_btn")
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self._prev_page)
        tb_layout.addWidget(self.prev_btn)

        self.page_label = QLabel("0 / 0")
        self.page_label.setStyleSheet("color: #8a99ad; font-size: 13px; font-weight: bold; background: transparent;")
        tb_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("▶")
        self.next_btn.setObjectName("ctrl_btn")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self._next_page)
        tb_layout.addWidget(self.next_btn)

        tb_layout.addSpacing(16)

        # Zoom controls
        self.zoom_out_btn = QPushButton("🔍 -")
        self.zoom_out_btn.setObjectName("ctrl_btn")
        self.zoom_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        tb_layout.addWidget(self.zoom_out_btn)

        self.fit_width_btn = QPushButton("↔ Fit")
        self.fit_width_btn.setObjectName("ctrl_btn")
        self.fit_width_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fit_width_btn.clicked.connect(self._fit_to_width)
        tb_layout.addWidget(self.fit_width_btn)

        self.zoom_in_btn = QPushButton("🔍 +")
        self.zoom_in_btn.setObjectName("ctrl_btn")
        self.zoom_in_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        tb_layout.addWidget(self.zoom_in_btn)

        layout.addWidget(self.top_bar)

        # ── PDF View Surface ──
        self.pdf_view = QPdfView(self)
        self.pdf_view.setDocument(self._document)
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self.pdf_view.setStyleSheet("background-color: #1a1d26; border: none;")
        layout.addWidget(self.pdf_view)

    def _connect_signals(self):
        self._document.statusChanged.connect(self._on_document_status_changed)
        self.pdf_view.pageNavigator().currentPageChanged.connect(self._on_page_changed)

    # ────────────────────────────────────────────
    #  Public API
    # ────────────────────────────────────────────

    def load_pdf(self, file_path: str, title: str = ""):
        """Load and display a local PDF file."""
        p = Path(file_path)
        if not p.exists():
            self.title_label.setText(f"File not found: {p.name}")
            return

        self.title_label.setText(title or p.stem)
        self._document.load(str(p))
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

    def cleanup(self):
        """Close document and clear viewer memory."""
        self._document.close()

    # ────────────────────────────────────────────
    #  Internal Handlers
    # ────────────────────────────────────────────

    def _on_document_status_changed(self, status):
        if status == QPdfDocument.Status.Error:
            self.title_label.setText(f"Erro ao abrir PDF ({self._document.error()})")
            self.page_label.setText("0 / 0")
            return
        total = self._document.pageCount()
        if total > 0:
            current = self.pdf_view.pageNavigator().currentPage() + 1
            self.page_label.setText(f"{current} / {total}")
            self.prev_btn.setEnabled(current > 1)
            self.next_btn.setEnabled(current < total)
        else:
            self.page_label.setText("0 / 0")

    def _on_page_changed(self, page_index: int):
        total = self._document.pageCount()
        current = page_index + 1
        self.page_label.setText(f"{current} / {total}")
        self.prev_btn.setEnabled(current > 1)
        self.next_btn.setEnabled(current < total)

    def _prev_page(self):
        nav = self.pdf_view.pageNavigator()
        if nav.currentPage() > 0:
            nav.jump(nav.currentPage() - 1, nav.currentLocation(), nav.currentZoom())

    def _next_page(self):
        nav = self.pdf_view.pageNavigator()
        if nav.currentPage() < self._document.pageCount() - 1:
            nav.jump(nav.currentPage() + 1, nav.currentLocation(), nav.currentZoom())

    def _zoom_in(self):
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        self._zoom_factor = min(self._zoom_factor * 1.25, 4.0)
        self.pdf_view.setZoomFactor(self._zoom_factor)

    def _zoom_out(self):
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        self._zoom_factor = max(self._zoom_factor * 0.8, 0.25)
        self.pdf_view.setZoomFactor(self._zoom_factor)

    def _fit_to_width(self):
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self._zoom_factor = 1.0
