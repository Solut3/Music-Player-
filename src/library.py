# Music Player - GPL-3.0
# Copyright (C) 2026 Music Player Contributors

"""Leitura de metadados, varredura e detecção automática de músicas."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from mutagen import File as MutagenFile

from .models import SUPPORTED_EXTENSIONS, Track


def _first_tag(tags: dict, *keys: str, default: str = "") -> str:
    for key in keys:
        value = tags.get(key)
        if value:
            if isinstance(value, list):
                return str(value[0])
            return str(value)
    return default


def discover_music_folders() -> list[Path]:
    """Retorna pastas comuns onde músicas costumam estar no PC."""
    home = Path.home()
    candidates: list[Path] = []

    if sys.platform == "win32":
        user_profile = Path(os.environ.get("USERPROFILE", home))
        candidates.extend([
            user_profile / "Music",
            user_profile / "Downloads",
            user_profile / "Desktop",
            user_profile / "Documents",
            user_profile / "Videos",
        ])
        for drive in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            drive_music = Path(f"{drive}:\\Music")
            if drive_music.is_dir():
                candidates.append(drive_music)
    else:
        xdg_music = os.environ.get("XDG_MUSIC_DIR")
        xdg_download = os.environ.get("XDG_DOWNLOAD_DIR")
        candidates.extend([
            Path(xdg_music) if xdg_music else home / "Music",
            Path(xdg_download) if xdg_download else home / "Downloads",
            home / "Downloads" / "Music",
            home / "Área de trabalho",
            home / "Desktop",
        ])

    seen: set[Path] = set()
    result: list[Path] = []
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved.is_dir() and resolved not in seen:
            seen.add(resolved)
            result.append(resolved)
    return result


def _track_from_cache(path: Path, cached: dict) -> Track:
    return Track(
        path=path,
        title=cached.get("title", path.stem),
        artist=cached.get("artist", ""),
        album=cached.get("album", ""),
        duration_ms=int(cached.get("duration_ms", 0)),
    )


def _track_to_cache(track: Track) -> dict:
    return {
        "title": track.title,
        "artist": track.artist,
        "album": track.album,
        "duration_ms": track.duration_ms,
    }


def read_track(path: Path) -> Track:
    """Extrai metadados de um arquivo de áudio."""
    title = path.stem
    artist = ""
    album = ""
    duration_ms = 0

    try:
        audio = MutagenFile(path, easy=True)
        if audio is not None:
            tags = audio.tags or {}
            title = _first_tag(tags, "title", default=title)
            artist = _first_tag(tags, "artist")
            album = _first_tag(tags, "album")
            if audio.info and hasattr(audio.info, "length"):
                duration_ms = int(audio.info.length * 1000)
    except Exception:
        pass

    return Track(
        path=path.resolve(),
        title=title,
        artist=artist,
        album=album,
        duration_ms=duration_ms,
    )


def collect_audio_paths(folders: list[Path], recursive: bool = True) -> list[Path]:
    """Coleta caminhos de áudio sem ler metadados (rápido, baixo uso de RAM)."""
    paths: list[Path] = []
    seen: set[Path] = set()

    for folder in folders:
        if not folder.is_dir():
            continue
        try:
            entries = folder.rglob("*") if recursive else folder.iterdir()
            for path in entries:
                if not path.is_file():
                    continue
                if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue
                try:
                    resolved = path.resolve()
                except OSError:
                    continue
                if resolved not in seen:
                    seen.add(resolved)
                    paths.append(resolved)
        except PermissionError:
            continue

    paths.sort()
    return paths


def build_library(
    folders: list[Path],
    cache: dict[str, dict] | None = None,
    progress_callback=None,
    recursive: bool = True,
) -> tuple[list[Track], dict[str, dict]]:
    """
    Monta biblioteca usando cache por mtime.
    Só relê metadados de arquivos novos ou modificados.
    """
    cache = dict(cache or {})
    paths = collect_audio_paths(folders, recursive=recursive)
    tracks: list[Track] = []
    new_cache: dict[str, dict] = {}
    total = len(paths)

    for index, path in enumerate(paths):
        key = str(path)
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue

        cached = cache.get(key)
        if cached and cached.get("mtime") == mtime:
            track = _track_from_cache(path, cached)
        else:
            track = read_track(path)
            cached = _track_to_cache(track)

        new_cache[key] = {**cached, "mtime": mtime}
        tracks.append(track)

        if progress_callback and (index % 20 == 0 or index == total - 1):
            progress_callback(index + 1, total)

    tracks.sort(
        key=lambda t: (
            t.display_artist.lower(),
            t.display_album.lower(),
            t.display_title.lower(),
        )
    )
    return tracks, new_cache


def scan_folder(folder: Path, cache: dict[str, dict] | None = None) -> tuple[list[Track], dict[str, dict]]:
    """Varre apenas os arquivos de áudio da pasta escolhida."""
    return build_library([folder], cache, recursive=False)


def scan_system_folders(cache: dict[str, dict] | None = None, progress_callback=None) -> tuple[list[Track], dict[str, dict]]:
    """Varre automaticamente as pastas de música do sistema."""
    folders = discover_music_folders()
    return build_library(folders, cache, progress_callback)
