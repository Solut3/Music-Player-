# Music Player - GPL-3.0
# Copyright (C) 2026 Music Player Contributors

"""Modelo de tabela eficiente em memória para a lista de faixas."""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from .models import Track


class TrackTableModel(QAbstractTableModel):
    """QAbstractTableModel usa menos RAM que QTableWidget."""

    HEADERS = ["Título", "Artista", "Álbum", "Duração"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._tracks: list[Track] = []

    def set_tracks(self, tracks: list[Track]) -> None:
        self.beginResetModel()
        self._tracks = tracks
        self.endResetModel()

    def tracks(self) -> list[Track]:
        return self._tracks

    def track_at(self, row: int) -> Track | None:
        if 0 <= row < len(self._tracks):
            return self._tracks[row]
        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._tracks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 4

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._tracks)):
            return None

        track = self._tracks[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            col = index.column()
            if col == 0:
                return track.display_title
            if col == 1:
                return track.display_artist
            if col == 2:
                return track.display_album
            if col == 3:
                return track.duration_label
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return None

    def find_row_by_path(self, path) -> int:
        for row, track in enumerate(self._tracks):
            if track.path == path:
                return row
        return -1
