from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ServiceConfig:
    name: str
    unit: str


@dataclass
class Settings:
    host: str = "0.0.0.0"
    port: int = 8080
    lines: int = 100


@dataclass
class AppConfig:
    settings: Settings = field(default_factory=Settings)
    services: list[ServiceConfig] = field(default_factory=list)


def load_config(path: Path | None = None) -> AppConfig:
    if path is None:
        env_path = os.environ.get("MULTIJOURNAL_CONFIG")
        if env_path:
            path = Path(env_path)
        else:
            path = Path("config.toml")

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "rb") as f:
        data = tomllib.load(f)

    settings_data = data.get("settings", {})
    settings = Settings(
        host=settings_data.get("host", "0.0.0.0"),
        port=settings_data.get("port", 8080),
        lines=settings_data.get("lines", 100),
    )

    services = [
        ServiceConfig(name=s["name"], unit=s["unit"])
        for s in data.get("services", [])
    ]

    return AppConfig(settings=settings, services=services)
