# Music Player - GPL-3.0
# Copyright (C) 2026 Music Player Contributors

"""Delegate visual para linhas da biblioteca."""

from __future__ import annotations

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QColor, QPainter, QPalette
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem, QTableView

from .themes import get_palette


class TrackItemDelegate(QStyledItemDelegate):
    """Renderiza seleção sutil e destaque da faixa em reprodução."""

    def __init__(self, theme: str = "dark", parent=None) -> None:
        super().__init__(parent)
        self._theme = theme
        self._playing_row = -1

    def set_theme(self, theme: str) -> None:
        self._theme = theme

    def set_playing_row(self, row: int) -> None:
        self._playing_row = row

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        c = get_palette(self._theme)
        rect = option.rect
        table = self.parent()
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)
        if isinstance(table, QTableView) and table.selectionModel():
            is_selected = table.selectionModel().isRowSelected(index.row(), QModelIndex())
        is_playing = index.row() == self._playing_row

        paint_option = QStyleOptionViewItem(option)
        if is_selected:
            paint_option.state &= ~QStyle.StateFlag.State_Selected
            paint_option.palette.setColor(
                QPalette.ColorRole.Text, QColor(c["selection_text"])
            )
        super().paint(painter, paint_option, index)

        # Desenha depois do conteúdo da última coluna: assim o contorno não é
        # interrompido pelos widgets de cada célula.
        if (
            is_selected
            and isinstance(table, QTableView)
            and index.column() == index.model().columnCount() - 1
        ):
            row_rect = table.visualRect(index.siblingAtColumn(0))
            row_rect.setRight(rect.right())
            row_rect.adjust(4, 3, -4, -3)

            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QColor(c["selection_border"]))
            painter.drawRoundedRect(row_rect, 8, 8)
            painter.restore()

        if is_playing:
            painter.save()
            painter.fillRect(rect.left(), rect.top() + 7, 3, max(0, rect.height() - 14), QColor(c["accent"]))
            painter.restore()
