# Music Player - GPL-3.0
# Copyright (C) 2026 Music Player Contributors

"""Aba Sobre o criador."""

from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

CREATOR = {
    "nick": "Solut333",
    "role": "Criador & Desenvolvedor",
    "bio": (
        "Music Player é um reprodutor de música open source para Windows e Linux, "
        "feito com Python e Qt. Projeto licenciado sob GPL-3.0."
    ),
    "links": {
        "GitHub": "https://github.com/Solut3",
        "Instagram": "https://instagram.com/s0lut3/",
        "YouTube": "https://youtube.com/@Solut333",
    },
}

_LINK_ICONS = {
    "GitHub": "⌘",
    "Instagram": "📷",
    "YouTube": "▶",
}


class AboutTab(QWidget):
    """Página About com informações do criador."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.addStretch()

        card = QFrame(self)
        card.setObjectName("aboutCard")
        card.setMaximumWidth(520)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(16)

        avatar = QLabel(CREATOR["nick"][:1].upper())
        avatar.setFixedSize(72, 72)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setObjectName("artFrame")
        avatar.setStyleSheet("font-size: 28px; font-weight: 700;")
        card_layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignHCenter)

        title = QLabel("Music Player")
        title.setObjectName("aboutTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        nick = QLabel(CREATOR["nick"])
        nick.setObjectName("aboutNick")
        nick.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(nick)

        role = QLabel(CREATOR["role"])
        role.setObjectName("sectionLabel")
        role.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(role)

        desc = QLabel(CREATOR["bio"])
        desc.setObjectName("aboutDesc")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(desc)

        card_layout.addSpacing(8)

        links_row = QHBoxLayout()
        links_row.setSpacing(10)
        for name, url in CREATOR["links"].items():
            btn = QPushButton(f"{_LINK_ICONS.get(name, '🔗')}  {name}")
            btn.setObjectName("linkBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _checked=False, u=url: QDesktopServices.openUrl(QUrl(u)))
            links_row.addWidget(btn)
        card_layout.addLayout(links_row)

        license_label = QLabel("Licenciado sob GNU GPL v3.0 — Software Livre")
        license_label.setObjectName("sectionLabel")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(license_label)

        outer.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch()
