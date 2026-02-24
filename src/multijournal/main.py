from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse

from multijournal.config import load_config
from multijournal.journal import stream_journal
from multijournal.terminal import terminal_session

config = load_config()
allowed_units = {s.unit for s in config.services}

app = FastAPI(title="multijournal")

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/services")
async def get_services() -> JSONResponse:
    return JSONResponse([
        {"index": i, "name": s.name, "unit": s.unit, "has_terminal": s.directory is not None}
        for i, s in enumerate(config.services)
    ])


@app.websocket("/ws/terminal/{service_index}")
async def ws_terminal(websocket: WebSocket, service_index: int) -> None:
    if service_index < 0 or service_index >= len(config.services):
        await websocket.close(code=4001, reason="Unknown service")
        return
    service = config.services[service_index]
    if service.directory is None:
        await websocket.close(code=4002, reason="No directory configured")
        return
    await websocket.accept()
    await terminal_session(websocket, service.directory)


@app.websocket("/ws/{unit}")
async def ws_journal(websocket: WebSocket, unit: str) -> None:
    if unit not in allowed_units:
        await websocket.close(code=4001, reason="Unknown unit")
        return

    await websocket.accept()

    try:
        async for line in stream_journal(unit, config.settings.lines):
            await websocket.send_text(line)
    except WebSocketDisconnect:
        pass


def run() -> None:
    uvicorn.run(
        "multijournal.main:app",
        host=config.settings.host,
        port=config.settings.port,
    )


if __name__ == "__main__":
    run()
