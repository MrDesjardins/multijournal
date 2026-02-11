# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**multijournal** streams systemd journal logs (`journalctl`) to a web UI via WebSockets. Users configure which services to monitor in `config.toml`, and the web page displays logs in a grid layout with full-screen toggle per service.

## Development Commands

- Install deps: `uv sync`
- Run: `uv run multijournal`
- Lint: `uv run ruff check src/`
- Format: `uv run ruff format src/`
- Type check: `uv run mypy src/`

## Architecture

- **Stack**: Python 3.12+, FastAPI, uvicorn, vanilla HTML/CSS/JS frontend
- **Package manager**: uv
- **Config**: `config.toml` (TOML, loaded via stdlib `tomllib`)
- **Entry point**: `src/multijournal/main.py` — FastAPI app with `run()` CLI entry

### Key files

- `src/multijournal/config.py` — TOML config loading with dataclasses
- `src/multijournal/journal.py` — async journalctl subprocess streaming
- `src/multijournal/main.py` — FastAPI routes (HTTP + WebSocket)
- `src/multijournal/static/index.html` — single-page web UI

### Design

- One WebSocket per service, each backed by a `journalctl -f` subprocess
- No JS framework; vanilla JS with auto-reconnect on disconnect
- Static files served directly by FastAPI
