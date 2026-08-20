# Music Player - GPL-3.0
# Copyright (C) 2026 Music Player Contributors

"""Configuração da aplicação Qt."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from .config import load_config
from .main_window import MainWindow
from .themes import apply_theme


def run() -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Music Player")
    app.setOrganizationName("MusicPlayer")
    app.setApplicationDisplayName("Music Player")
    app.setQuitOnLastWindowClosed(False)

    config = load_config()
    apply_theme(app, config.theme)

    window = MainWindow(config)
    window.show()

    return app.exec()
