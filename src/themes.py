# Music Player - GPL-3.0
# Copyright (C) 2026 Music Player Contributors

"""Temas visual dark e light."""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

THEMES = ("dark", "light")

_PALETTES = {
    "dark": {
        # O fundo principal acompanha os painéis para que os espaços entre os
        # componentes não pareçam uma área preta separada.
        "bg": "#16161e",
        "surface": "#16161e",
        "surface2": "#1e1e28",
        "surface3": "#262632",
        "border": "#2a2a38",
        "text": "#eeeef2",
        "text_dim": "#7a7a92",
        "accent": "#8b72ff",
        "accent_soft": "#188b72ff",
        "accent_hover": "#9d86ff",
        "accent_pressed": "#6e54e8",
        "selection": "#1a8b72ff",
        "selection_border": "#558b72ff",
        "selection_text": "#ddd6ff",
        "hover": "#08ffffff",
        "playing": "#288b72ff",
        "link": "#a594ff",
    },
    "light": {
        "bg": "#f3f3f7",
        "surface": "#ffffff",
        "surface2": "#f0f0f6",
        "surface3": "#e6e6ef",
        "border": "#dddde8",
        "text": "#18181f",
        "text_dim": "#68687a",
        "accent": "#6c52f0",
        "accent_soft": "#146c52f0",
        "accent_hover": "#7c64f8",
        "accent_pressed": "#5740d4",
        "selection": "#126c52f0",
        "selection_border": "#406c52f0",
        "selection_text": "#3d2e9e",
        "hover": "#06000000",
        "playing": "#1a6c52f0",
        "link": "#5a42d4",
    },
}


def get_palette(theme: str) -> dict[str, str]:
    return _PALETTES.get(theme, _PALETTES["dark"])


def _build_stylesheet(theme: str) -> str:
    c = _PALETTES[theme]
    return f"""
    * {{
        font-family: "Segoe UI", "Ubuntu", "Cantarell", sans-serif;
        font-size: 13px;
    }}

    QMainWindow, QDialog {{
        background-color: {c["bg"]};
        color: {c["text"]};
    }}

    QWidget {{
        background-color: transparent;
        color: {c["text"]};
    }}

    QWidget#centralArea, QWidget#libraryPage, QTabWidget::pane {{
        background-color: {c["bg"]};
    }}

    QToolBar {{
        background-color: {c["surface"]};
        border: none;
        border-bottom: 1px solid {c["border"]};
        padding: 8px 14px;
        spacing: 8px;
    }}

    QToolBar QToolButton {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 10px;
        padding: 7px 16px;
        color: {c["text"]};
    }}

    QToolBar QToolButton:hover {{
        background-color: {c["surface2"]};
        border-color: {c["border"]};
    }}

    QStatusBar {{
        background-color: {c["surface"]};
        border-top: 1px solid {c["border"]};
        color: {c["text_dim"]};
        padding: 4px 10px;
    }}

    QTabWidget::pane {{
        border: none;
        top: -1px;
    }}

    QTabBar {{
        background: transparent;
    }}

    QTabBar::tab {{
        background: {c["surface2"]};
        color: {c["text_dim"]};
        border: 1px solid {c["border"]};
        border-bottom: none;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        padding: 10px 22px;
        margin-right: 4px;
        min-width: 80px;
    }}

    QTabBar::tab:selected {{
        background: {c["surface"]};
        color: {c["text"]};
        border-color: {c["border"]};
        font-weight: 600;
    }}

    QTabBar::tab:hover:!selected {{
        background: {c["surface3"]};
        color: {c["text"]};
    }}

    QLabel#nowPlayingTitle {{
        font-size: 20px;
        font-weight: 700;
        color: {c["text"]};
    }}

    QLabel#nowPlayingArtist {{
        font-size: 13px;
        color: {c["text_dim"]};
    }}

    QLabel#sectionLabel {{
        font-size: 11px;
        font-weight: 600;
        color: {c["text_dim"]};
        letter-spacing: 0.5px;
    }}

    QLabel#aboutTitle {{
        font-size: 26px;
        font-weight: 700;
        color: {c["text"]};
    }}

    QLabel#aboutNick {{
        font-size: 18px;
        font-weight: 600;
        color: {c["accent"]};
    }}

    QLabel#aboutDesc {{
        font-size: 13px;
        color: {c["text_dim"]};
        line-height: 1.5;
    }}

    QTableView {{
        background-color: {c["surface"]};
        alternate-background-color: {c["surface2"]};
        border: 1px solid {c["border"]};
        border-radius: 14px;
        gridline-color: transparent;
        selection-background-color: {c["selection"]};
        selection-color: {c["selection_text"]};
        outline: none;
    }}

    QTableView::viewport {{
        background-color: {c["surface"]};
        border-radius: 13px;
    }}

    QTableView::item {{
        padding: 8px 12px;
        border: none;
        border-left: 3px solid transparent;
    }}

    QTableView::item:hover {{
        background-color: {c["hover"]};
    }}

    QTableView::item:selected {{
        background-color: {c["selection"]};
        color: {c["selection_text"]};
        border-left: 3px solid {c["accent"]};
    }}

    QTableView::item:selected:active {{
        background-color: {c["selection"]};
        color: {c["selection_text"]};
    }}

    QHeaderView::section {{
        background-color: {c["surface2"]};
        color: {c["text_dim"]};
        border: none;
        border-bottom: 1px solid {c["border"]};
        padding: 10px 12px;
        font-weight: 600;
        font-size: 11px;
    }}

    QPushButton {{
        background-color: {c["surface2"]};
        color: {c["text"]};
        border: 1px solid {c["border"]};
        border-radius: 10px;
        padding: 8px 16px;
        min-width: 36px;
        min-height: 36px;
    }}

    QPushButton:hover {{
        background-color: {c["surface3"]};
        border-color: {c["accent"]};
    }}

    QPushButton:pressed {{
        background-color: {c["accent_pressed"]};
        color: #ffffff;
    }}

    QPushButton#themeBtn {{
        background-color: {c["accent_soft"]};
        color: {c["accent"]};
        border: 1px solid {c["selection_border"]};
        border-radius: 20px;
        padding: 6px 14px;
        min-height: 32px;
        font-weight: 600;
    }}

    QPushButton#themeBtn:hover {{
        background-color: {c["selection"]};
        border-color: {c["accent"]};
    }}

    QPushButton#playBtn {{
        background-color: {c["accent"]};
        color: #ffffff;
        border: none;
        font-size: 18px;
        min-width: 52px;
        min-height: 52px;
        max-width: 52px;
        max-height: 52px;
        border-radius: 26px;
    }}

    QPushButton#playBtn:hover {{
        background-color: {c["accent_hover"]};
    }}

    QPushButton#playBtn:pressed {{
        background-color: {c["accent_pressed"]};
    }}

    QPushButton#controlBtn {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 20px;
        min-width: 40px;
        min-height: 40px;
        max-width: 40px;
        max-height: 40px;
        font-size: 15px;
        padding: 0;
    }}

    QPushButton#controlBtn:hover {{
        background-color: {c["surface3"]};
        border-color: {c["border"]};
    }}

    QPushButton[active="true"] {{
        background-color: {c["accent_soft"]};
        color: {c["accent"]};
        border-color: {c["selection_border"]};
    }}

    QPushButton#linkBtn {{
        background-color: {c["surface2"]};
        color: {c["link"]};
        border: 1px solid {c["border"]};
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 600;
        min-width: 120px;
    }}

    QPushButton#linkBtn:hover {{
        background-color: {c["selection"]};
        border-color: {c["accent"]};
        color: {c["accent"]};
    }}

    QSlider::groove:horizontal {{
        height: 5px;
        background: {c["border"]};
        border-radius: 2px;
    }}

    QSlider::handle:horizontal {{
        width: 14px;
        height: 14px;
        margin: -5px 0;
        background: {c["accent"]};
        border-radius: 7px;
    }}

    QSlider::sub-page:horizontal {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {c["accent_pressed"]}, stop:1 {c["accent"]});
        border-radius: 2px;
    }}

    QProgressBar {{
        background-color: {c["surface2"]};
        border: none;
        border-radius: 4px;
        height: 6px;
        text-align: center;
        color: transparent;
    }}

    QProgressBar::chunk {{
        background-color: {c["accent"]};
        border-radius: 4px;
    }}

    QFrame#playerBar {{
        background-color: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 18px;
    }}

    QFrame#headerCard {{
        background-color: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 18px;
    }}

    QFrame#aboutCard {{
        background-color: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 20px;
    }}

    QFrame#artFrame {{
        background-color: {c["accent_soft"]};
        border: 1px solid {c["selection_border"]};
        border-radius: 16px;
    }}

    QMenu {{
        background-color: {c["surface"]};
        border: 1px solid {c["border"]};
        border-radius: 10px;
        padding: 6px;
    }}

    QMenu::item {{
        padding: 8px 24px;
        border-radius: 6px;
    }}

    QMenu::item:selected {{
        background-color: {c["selection"]};
        color: {c["selection_text"]};
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 4px 2px;
    }}

    QScrollBar::handle:vertical {{
        background: {c["border"]};
        border-radius: 4px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {c["text_dim"]};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    """


def apply_theme(app: QApplication, theme: str) -> None:
    if theme not in THEMES:
        theme = "dark"
    c = _PALETTES[theme]

    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Highlight, QColor(c["selection"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(c["selection_text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(c["surface"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(c["surface2"]))
    palette.setColor(QPalette.ColorRole.Window, QColor(c["bg"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(c["text"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(c["text"]))
    app.setPalette(palette)
    app.setStyleSheet(_build_stylesheet(theme))
