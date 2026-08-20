# Music Player - GPL-3.0
# Copyright (C) 2026 Music Player Contributors

"""Modelos de dados do player."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXTENSIONS = {".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aac", ".opus", ".wma"}


@dataclass(frozen=True)
class Track:
    """Representa uma faixa de áudio na biblioteca."""

    path: Path
    title: str
    artist: str
    album: str
    duration_ms: int

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def duration_label(self) -> str:
        total_seconds = max(0, self.duration_ms // 1000)
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes}:{seconds:02d}"

    @property
    def display_title(self) -> str:
        return self.title or self.filename

    @property
    def display_artist(self) -> str:
        return self.artist or "Artista desconhecido"

    @property
    def display_album(self) -> str:
        return self.album or "Álbum desconhecido"
