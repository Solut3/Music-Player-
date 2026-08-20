# Music Player - GPL-3.0
# Copyright (C) 2026 Music Player Contributors

"""Persistência de configurações e cache da biblioteca."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    theme: str = "dark"
    last_folder: str | None = None
    minimize_to_tray: bool = True
    auto_scan: bool = True
    volume: float = 0.75
    library_cache: dict[str, dict] = field(default_factory=dict)


def config_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".config"
    path = base / "music-player"
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_path() -> Path:
    return config_dir() / "config.json"


def load_config() -> AppConfig:
    path = config_path()
    if not path.exists():
        return AppConfig()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return AppConfig(
            theme=data.get("theme", "dark"),
            last_folder=data.get("last_folder"),
            minimize_to_tray=data.get("minimize_to_tray", True),
            auto_scan=data.get("auto_scan", True),
            volume=float(data.get("volume", 0.75)),
            library_cache=data.get("library_cache", {}),
        )
    except Exception:
        return AppConfig()


def save_config(config: AppConfig) -> None:
    data = asdict(config)
    config_path().write_text(json.dumps(data, indent=2), encoding="utf-8")
