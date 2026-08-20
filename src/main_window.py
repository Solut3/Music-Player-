# Music Player - GPL-3.0
# Copyright (C) 2026 Music Player Contributors

"""Janela principal do player."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QIcon, QKeySequence, QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QProgressBar,
    QPushButton,
    QSlider,
    QStatusBar,
    QSystemTrayIcon,
    QTableView,
    QToolBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .config import AppConfig, load_config, save_config
from .about_tab import AboutTab
from .library_scanner import LibraryScanner, get_discoverable_folders
from .models import Track
from .player import AudioPlayer, RepeatMode
from .themes import THEMES, apply_theme
from .track_delegate import TrackItemDelegate


def _format_time(ms: int) -> str:
    total_seconds = max(0, ms // 1000)
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def _make_tray_icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#7c5cfc"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(4, 4, 56, 56, 14, 14)
    painter.setBrush(QColor("#ffffff"))
    painter.drawEllipse(20, 16, 12, 12)
    painter.drawRect(28, 22, 5, 26)
    painter.end()
    return QIcon(pixmap)


class MainWindow(QMainWindow):
    """Interface principal do Music Player."""

    def __init__(self, config: AppConfig | None = None) -> None:
        super().__init__()
        self._config = config or load_config()
        self._player = AudioPlayer(self)
        self._player.set_volume(self._config.volume)
        self._seeking = False
        self._scanner: LibraryScanner | None = None
        self._scan_generation = 0
        self._theme = self._config.theme if self._config.theme in THEMES else "dark"

        self.setWindowTitle("Music Player")
        self.resize(1024, 680)
        self.setMinimumSize(720, 480)

        self._build_ui()
        self._setup_tray()
        self._connect_signals()
        self._setup_shortcuts()
        self._apply_current_theme()
        self._start_initial_load()

    def _build_ui(self) -> None:
        toolbar = QToolBar("Principal", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        open_action = QAction("📁 Abrir pasta", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_folder)
        toolbar.addAction(open_action)

        scan_action = QAction("🔍 Escanear PC", self)
        scan_action.triggered.connect(self._scan_system)
        toolbar.addAction(scan_action)

        toolbar.addSeparator()

        self._theme_button = QPushButton(self)
        self._theme_button.setObjectName("themeBtn")
        self._theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_button.clicked.connect(self._toggle_theme)
        toolbar.addWidget(self._theme_button)

        central = QWidget(self)
        central.setObjectName("centralArea")
        self.setCentralWidget(central)
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(16, 12, 16, 12)
        central_layout.setSpacing(0)

        self._tabs = QTabWidget(self)
        central_layout.addWidget(self._tabs)

        library_page = QWidget(self)
        library_page.setObjectName("libraryPage")
        root = QVBoxLayout(library_page)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)

        # Header card — now playing
        header = QFrame(self)
        header.setObjectName("headerCard")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)

        art = QLabel("♪")
        art.setFixedSize(64, 64)
        art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        art.setStyleSheet(
            "background-color: #227c5cfc; border-radius: 12px; "
            "font-size: 28px; color: #7c5cfc;"
        )
        header_layout.addWidget(art)

        info = QVBoxLayout()
        self._now_title = QLabel("Nenhuma faixa")
        self._now_title.setObjectName("nowPlayingTitle")
        self._now_artist = QLabel("Abra uma pasta ou escaneie o PC")
        self._now_artist.setObjectName("nowPlayingArtist")
        info.addWidget(self._now_title)
        info.addWidget(self._now_artist)
        header_layout.addLayout(info, stretch=1)

        self._track_count_label = QLabel("")
        self._track_count_label.setObjectName("sectionLabel")
        self._track_count_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(self._track_count_label)

        root.addWidget(header)

        # Scan progress
        self._scan_progress = QProgressBar(self)
        self._scan_progress.setVisible(False)
        self._scan_progress.setTextVisible(False)
        self._scan_progress.setFixedHeight(6)
        root.addWidget(self._scan_progress)

        # Track list
        from .track_model import TrackTableModel

        self._model = TrackTableModel(self)
        self._table = QTableView(self)
        self._table.setModel(self._model)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._track_delegate = TrackItemDelegate(self._theme, self._table)
        self._table.setItemDelegate(self._track_delegate)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table.doubleClicked.connect(self._play_selected)
        root.addWidget(self._table, stretch=1)

        # Player bar
        player_bar = QFrame(self)
        player_bar.setObjectName("playerBar")
        bar_layout = QVBoxLayout(player_bar)
        bar_layout.setContentsMargins(20, 14, 20, 14)
        bar_layout.setSpacing(10)

        seek_row = QHBoxLayout()
        self._position_label = QLabel("0:00")
        self._position_label.setFixedWidth(40)
        self._seek_slider = QSlider(Qt.Orientation.Horizontal)
        self._seek_slider.setRange(0, 0)
        self._duration_label = QLabel("0:00")
        self._duration_label.setFixedWidth(40)
        self._duration_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        seek_row.addWidget(self._position_label)
        seek_row.addWidget(self._seek_slider, stretch=1)
        seek_row.addWidget(self._duration_label)
        bar_layout.addLayout(seek_row)

        controls_row = QHBoxLayout()
        controls_row.addStretch()

        self._shuffle_btn = QPushButton("🔀")
        self._shuffle_btn.setToolTip("Aleatório")
        self._prev_btn = QPushButton("⏮")
        self._prev_btn.setToolTip("Anterior")
        self._play_btn = QPushButton("▶")
        self._play_btn.setObjectName("playBtn")
        self._play_btn.setToolTip("Play / Pause")
        self._next_btn = QPushButton("⏭")
        self._next_btn.setToolTip("Próximo")
        self._repeat_btn = QPushButton("🔁")
        self._repeat_btn.setToolTip("Repetir")

        for btn in (self._shuffle_btn, self._prev_btn, self._play_btn, self._next_btn, self._repeat_btn):
            if btn is not self._play_btn:
                btn.setObjectName("controlBtn")
            controls_row.addWidget(btn)
        controls_row.addStretch()
        bar_layout.addLayout(controls_row)

        volume_row = QHBoxLayout()
        vol_icon = QLabel("🔊")
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(int(self._player.volume() * 100))
        self._volume_slider.setFixedWidth(120)
        volume_row.addStretch()
        volume_row.addWidget(vol_icon)
        volume_row.addWidget(self._volume_slider)
        bar_layout.addLayout(volume_row)

        root.addWidget(player_bar)

        self._tabs.addTab(library_page, "Biblioteca")
        self._tabs.addTab(AboutTab(self), "Sobre")

        self._status = QStatusBar(self)
        self.setStatusBar(self._status)

    def _setup_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self._tray = None
            return

        self._tray = QSystemTrayIcon(_make_tray_icon(), self)
        tray_menu = QMenu(self)

        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self._show_from_tray)
        tray_menu.addAction(show_action)

        play_action = QAction("Play / Pause", self)
        play_action.triggered.connect(self._player.toggle_play_pause)
        tray_menu.addAction(play_action)

        tray_menu.addSeparator()

        quit_action = QAction("Sair", self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)

        self._tray.setContextMenu(tray_menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _connect_signals(self) -> None:
        self._prev_btn.clicked.connect(self._player.previous_track)
        self._play_btn.clicked.connect(self._player.toggle_play_pause)
        self._next_btn.clicked.connect(self._player.next_track)
        self._shuffle_btn.clicked.connect(self._toggle_shuffle)
        self._repeat_btn.clicked.connect(self._cycle_repeat)

        self._volume_slider.valueChanged.connect(self._on_volume_changed)
        self._seek_slider.sliderPressed.connect(lambda: setattr(self, "_seeking", True))
        self._seek_slider.sliderReleased.connect(self._on_seek_released)

        self._player.position_changed.connect(self._on_position_changed)
        self._player.duration_changed.connect(self._on_duration_changed)
        self._player.state_changed.connect(self._on_state_changed)
        self._player.track_changed.connect(self._on_track_changed)

        self._position_timer = QTimer(self)
        self._position_timer.setInterval(1000)
        self._position_timer.timeout.connect(self._refresh_position)

    def _setup_shortcuts(self) -> None:
        for key, slot in (
            (Qt.Key.Key_Space, self._player.toggle_play_pause),
            (Qt.Key.Key_Right, self._player.next_track),
            (Qt.Key.Key_Left, self._player.previous_track),
        ):
            action = QAction(self)
            action.setShortcut(key)
            action.triggered.connect(slot)
            self.addAction(action)

    def _apply_current_theme(self) -> None:
        app = QApplication.instance()
        if app:
            apply_theme(app, self._theme)
        self._track_delegate.set_theme(self._theme)
        self._table.viewport().update()
        if self._theme == "dark":
            self._theme_button.setText("🌙 Tema: escuro")
            self._theme_button.setToolTip("Mudar para o tema claro")
        else:
            self._theme_button.setText("☀️ Tema: claro")
            self._theme_button.setToolTip("Mudar para o tema escuro")

    def _toggle_theme(self) -> None:
        self._theme = "light" if self._theme == "dark" else "dark"
        self._config.theme = self._theme
        save_config(self._config)
        self._apply_current_theme()

    def _start_initial_load(self) -> None:
        folders = get_discoverable_folders()
        folder_names = ", ".join(p.name for p in folders[:3])
        if len(folders) > 3:
            folder_names += "…"

        if self._config.library_cache:
            self._status.showMessage("Carregando biblioteca em cache…")
            self._scan_system(silent=True)
        elif self._config.auto_scan:
            self._status.showMessage(f"Escaneando músicas em {folder_names}…")
            self._scan_system(silent=True)
        elif self._config.last_folder:
            self._load_folder(Path(self._config.last_folder), save=False)
        else:
            self._status.showMessage("Use 'Escanear PC' ou 'Abrir pasta' para começar.")

    def _open_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Selecionar pasta de músicas")
        if folder:
            self._load_folder(Path(folder))

    def _load_folder(self, folder: Path, save: bool = True) -> None:
        # Invalida qualquer varredura anterior antes de limpar a interface. Dessa
        # forma, o resultado do escaneamento geral não pode reaparecer na lista.
        self._scan_generation += 1
        generation = self._scan_generation
        self._clear_library_view(f"Lendo músicas de {folder.name}…")

        self._scan_progress.setVisible(True)
        self._scan_progress.setRange(0, 0)

        if self._scanner and self._scanner.isRunning():
            self._scanner.requestInterruption()
            self._scanner.wait(2000)

        self._scanner = LibraryScanner(
            folders=[folder],
            cache=self._config.library_cache,
            recursive=False,
        )
        self._scanner.progress.connect(self._on_scan_progress)
        self._scanner.finished_scan.connect(
            lambda tracks, cache, current=generation: self._on_scan_done(
                tracks, cache, folder if save else None, current
            )
        )
        self._scanner.error.connect(self._on_scan_error)
        self._scanner.start()

    def _scan_system(self, silent: bool = False) -> None:
        self._scan_generation += 1
        generation = self._scan_generation
        if not silent:
            folders = get_discoverable_folders()
            self._status.showMessage(
                f"Escaneando {len(folders)} pasta(s): Music, Downloads…"
            )

        self._scan_progress.setVisible(True)
        self._scan_progress.setRange(0, 0)

        if self._scanner and self._scanner.isRunning():
            self._scanner.requestInterruption()
            self._scanner.wait(2000)

        self._scanner = LibraryScanner(cache=self._config.library_cache, auto=True)
        self._scanner.progress.connect(self._on_scan_progress)
        self._scanner.finished_scan.connect(
            lambda tracks, cache, current=generation: self._on_scan_done(
                tracks, cache, None, current
            )
        )
        self._scanner.error.connect(self._on_scan_error)
        self._scanner.start()

    def _on_scan_progress(self, current: int, total: int) -> None:
        self._scan_progress.setRange(0, total)
        self._scan_progress.setValue(current)

    def _clear_library_view(self, message: str) -> None:
        """Remove imediatamente a biblioteca anterior antes de trocar de pasta."""
        self._player.stop()
        self._model.set_tracks([])
        self._player.set_tracks([])
        self._track_delegate.set_playing_row(-1)
        self._table.viewport().update()
        self._now_title.setText("Nenhuma faixa")
        self._now_artist.setText("Carregando a pasta selecionada…")
        self._track_count_label.setText("Carregando…")
        self._seek_slider.setRange(0, 0)
        self._position_label.setText("0:00")
        self._duration_label.setText("0:00")
        self._status.showMessage(message)

    def _on_scan_done(
        self, tracks: list, cache: dict, folder: Path | None, generation: int
    ) -> None:
        if generation != self._scan_generation:
            return
        self._scan_progress.setVisible(False)

        if not tracks:
            self._status.showMessage("Nenhuma música encontrada.")
            return

        self._config.library_cache = cache
        if folder:
            self._config.last_folder = str(folder)
        save_config(self._config)

        self._model.set_tracks(tracks)
        self._player.set_tracks(tracks)
        if folder:
            self._track_count_label.setText(f"{len(tracks)} faixas · {folder.name}")
            self._status.showMessage(f"{len(tracks)} música(s) em {folder.name}.")
        else:
            self._track_count_label.setText(f"{len(tracks)} faixas")
            self._status.showMessage(f"{len(tracks)} música(s) encontrada(s) no PC.")

        if self._tray:
            self._tray.setToolTip(f"Music Player — {len(tracks)} faixas")

    def _on_scan_error(self, message: str) -> None:
        self._scan_progress.setVisible(False)
        self._status.showMessage(f"Erro ao escanear: {message}")

    def _play_selected(self, index) -> None:
        row = index.row()
        if row >= 0:
            self._player.play_index(row)

    def _toggle_shuffle(self) -> None:
        enabled = not self._player.shuffle
        self._player.set_shuffle(enabled)
        self._shuffle_btn.setProperty("active", enabled)
        self._shuffle_btn.style().unpolish(self._shuffle_btn)
        self._shuffle_btn.style().polish(self._shuffle_btn)

    def _cycle_repeat(self) -> None:
        mode = self._player.cycle_repeat()
        active = mode != RepeatMode.OFF
        tips = {
            RepeatMode.OFF: "Repetir: desligado",
            RepeatMode.ALL: "Repetir: todas",
            RepeatMode.ONE: "Repetir: uma",
        }
        self._repeat_btn.setToolTip(tips[mode])
        self._repeat_btn.setProperty("active", active)
        self._repeat_btn.style().unpolish(self._repeat_btn)
        self._repeat_btn.style().polish(self._repeat_btn)

    def _on_volume_changed(self, value: int) -> None:
        level = value / 100
        self._player.set_volume(level)
        self._config.volume = level
        save_config(self._config)

    def _on_seek_released(self) -> None:
        self._seeking = False
        self._player.seek(self._seek_slider.value())

    def _on_position_changed(self, position_ms: int) -> None:
        if not self._seeking:
            self._seek_slider.blockSignals(True)
            self._seek_slider.setValue(position_ms)
            self._seek_slider.blockSignals(False)
            self._position_label.setText(_format_time(position_ms))

    def _on_duration_changed(self, duration_ms: int) -> None:
        self._seek_slider.setRange(0, max(0, duration_ms))
        self._duration_label.setText(_format_time(duration_ms))

    def _on_state_changed(self, playing: bool) -> None:
        self._play_btn.setText("⏸" if playing else "▶")
        if playing:
            self._position_timer.start()
        else:
            self._position_timer.stop()

        if self._tray and self._player.current_track:
            track = self._player.current_track
            icon_text = f"{track.display_title} — {track.display_artist}"
            state = "▶" if playing else "⏸"
            self._tray.setToolTip(f"{state} {icon_text}")

    def _on_track_changed(self, track: Track) -> None:
        self._now_title.setText(track.display_title)
        self._now_artist.setText(track.display_artist)
        row = self._model.find_row_by_path(track.path)
        if row >= 0:
            self._table.selectRow(row)
            self._track_delegate.set_playing_row(row)
            self._table.viewport().update()
            self._table.scrollTo(self._model.index(row, 0))

    def _refresh_position(self) -> None:
        if not self._seeking and self._player.is_playing:
            position = self._player.position()
            self._seek_slider.blockSignals(True)
            self._seek_slider.setValue(position)
            self._seek_slider.blockSignals(False)
            self._position_label.setText(_format_time(position))

    def _show_from_tray(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_from_tray()

    def _quit_app(self) -> None:
        self._config.minimize_to_tray = False
        save_config(self._config)
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._config.minimize_to_tray and self._tray and self._tray.isVisible():
            event.ignore()
            self.hide()
            self._tray.showMessage(
                "Music Player",
                "Rodando em segundo plano. Clique duplo no ícone para abrir.",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
            return
        save_config(self._config)
        super().closeEvent(event)

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized() and self._config.minimize_to_tray and self._tray:
                QTimer.singleShot(0, self.hide)
