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
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_playing = index.row() == self._playing_row

        paint_option = QStyleOptionViewItem(option)
        if is_selected:
            # A seleção é desenhada uma única vez para a linha inteira. Assim ela não
            # fica dividida em células nem recebe a cor padrão do sistema.
            table = self.parent()
            if isinstance(table, QTableView) and index.column() == 0:
                last_column = index.model().columnCount() - 1
                row_rect = table.visualRect(index.siblingAtColumn(last_column))
                row_rect.setLeft(rect.left())
                row_rect.adjust(4, 3, -4, -3)

                painter.save()
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QColor(c["selection_border"]))
                painter.drawRoundedRect(row_rect, 8, 8)
                painter.restore()

            paint_option.state &= ~QStyle.StateFlag.State_Selected
            paint_option.palette.setColor(
                QPalette.ColorRole.Text, QColor(c["selection_text"])
            )
        super().paint(painter, paint_option, index)

        if is_playing:
            painter.save()
            painter.fillRect(rect.left(), rect.top() + 7, 3, max(0, rect.height() - 14), QColor(c["accent"]))
            painter.restore()
