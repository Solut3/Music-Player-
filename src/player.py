# Music Player - GPL-3.0
# Copyright (C) 2026 Music Player Contributors

"""Motor de reprodução com fila, shuffle e repeat."""

from __future__ import annotations

import random
from enum import Enum, auto

from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

from .models import Track


class RepeatMode(Enum):
    OFF = auto()
    ALL = auto()
    ONE = auto()


class AudioPlayer(QObject):
    """Encapsula QMediaPlayer com fila de reprodução."""

    position_changed = Signal(int)
    duration_changed = Signal(int)
    state_changed = Signal(bool)
    track_changed = Signal(object)
    queue_changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)

        self._tracks: list[Track] = []
        self._queue: list[int] = []
        self._queue_pos = -1
        self._shuffle = False
        self._repeat = RepeatMode.OFF
        self._manual_stop = False

        self._player.positionChanged.connect(self.position_changed.emit)
        self._player.durationChanged.connect(self.duration_changed.emit)
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)

        self._audio_output.setVolume(0.75)

    @property
    def current_track(self) -> Track | None:
        if 0 <= self._queue_pos < len(self._queue):
            return self._tracks[self._queue[self._queue_pos]]
        return None

    @property
    def is_playing(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    @property
    def shuffle(self) -> bool:
        return self._shuffle

    @property
    def repeat(self) -> RepeatMode:
        return self._repeat

    def set_tracks(self, tracks: list[Track]) -> None:
        self._tracks = tracks
        self._queue = list(range(len(tracks)))
        self._queue_pos = -1
        self.queue_changed.emit()

    def set_shuffle(self, enabled: bool) -> None:
        if self._shuffle == enabled:
            return
        self._shuffle = enabled
        current_index = self._current_track_index()
        self._rebuild_queue(preserve_current=current_index)
        self.queue_changed.emit()

    def cycle_repeat(self) -> RepeatMode:
        modes = list(RepeatMode)
        index = modes.index(self._repeat)
        self._repeat = modes[(index + 1) % len(modes)]
        return self._repeat

    def set_volume(self, level: float) -> None:
        self._audio_output.setVolume(max(0.0, min(1.0, level)))

    def volume(self) -> float:
        return self._audio_output.volume()

    def play_index(self, index: int) -> None:
        if not (0 <= index < len(self._tracks)):
            return
        if index not in self._queue:
            self._queue = [index]
            self._queue_pos = 0
        else:
            self._queue_pos = self._queue.index(index)
        self._load_current()

    def toggle_play_pause(self) -> None:
        if self.current_track is None and self._tracks:
            self.play_index(0)
            return
        if self.is_playing:
            self._player.pause()
        else:
            self._player.play()

    def stop(self) -> None:
        self._manual_stop = True
        self._player.stop()

    def next_track(self) -> None:
        if not self._queue:
            return
        if self._queue_pos + 1 < len(self._queue):
            self._queue_pos += 1
            self._load_current()
        elif self._repeat == RepeatMode.ALL:
            self._queue_pos = 0
            self._load_current()

    def previous_track(self) -> None:
        if self._player.position() > 3000 and self.current_track is not None:
            self._player.setPosition(0)
            return
        if not self._queue:
            return
        if self._queue_pos > 0:
            self._queue_pos -= 1
            self._load_current()
        elif self._repeat == RepeatMode.ALL:
            self._queue_pos = len(self._queue) - 1
            self._load_current()

    def seek(self, position_ms: int) -> None:
        self._player.setPosition(max(0, position_ms))

    def position(self) -> int:
        return self._player.position()

    def duration(self) -> int:
        return self._player.duration()

    def _current_track_index(self) -> int | None:
        if 0 <= self._queue_pos < len(self._queue):
            return self._queue[self._queue_pos]
        return None

    def _rebuild_queue(self, preserve_current: int | None) -> None:
        indices = list(range(len(self._tracks)))
        if preserve_current is not None and preserve_current in indices:
            indices.remove(preserve_current)
            if self._shuffle:
                random.shuffle(indices)
            self._queue = [preserve_current] + indices
            self._queue_pos = 0
        else:
            if self._shuffle:
                random.shuffle(indices)
            self._queue = indices
            self._queue_pos = -1

    def _load_current(self) -> None:
        track = self.current_track
        if track is None:
            return
        self._manual_stop = False
        self._player.setSource(QUrl.fromLocalFile(str(track.path)))
        self.track_changed.emit(track)
        self._player.play()

    @Slot(QMediaPlayer.PlaybackState)
    def _on_playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        self.state_changed.emit(state == QMediaPlayer.PlaybackState.PlayingState)

    @Slot(QMediaPlayer.MediaStatus)
    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if status != QMediaPlayer.MediaStatus.EndOfMedia:
            return
        if self._manual_stop:
            return
        if self._repeat == RepeatMode.ONE:
            self._player.setPosition(0)
            self._player.play()
            return
        self.next_track()
