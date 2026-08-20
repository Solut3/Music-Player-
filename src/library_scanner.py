# Music Player - GPL-3.0
# Copyright (C) 2026 Music Player Contributors

"""Varredura de biblioteca em thread separada para não bloquear a UI."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from .library import build_library, discover_music_folders, scan_system_folders


class LibraryScanner(QThread):
    """Escaneia pastas em background."""

    progress = Signal(int, int)
    finished_scan = Signal(list, dict)
    error = Signal(str)

    def __init__(
        self,
        folders: list[Path] | None = None,
        cache: dict | None = None,
        auto: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._folders = folders
        self._cache = cache or {}
        self._auto = auto

    def run(self) -> None:
        try:
            def on_progress(current: int, total: int) -> None:
                self.progress.emit(current, total)

            if self._auto:
                tracks, new_cache = scan_system_folders(self._cache, on_progress)
            elif self._folders:
                tracks, new_cache = build_library(self._folders, self._cache, on_progress)
            else:
                tracks, new_cache = [], {}

            self.finished_scan.emit(tracks, new_cache)
        except Exception as exc:
            self.error.emit(str(exc))


def get_discoverable_folders() -> list[Path]:
    return discover_music_folders()
