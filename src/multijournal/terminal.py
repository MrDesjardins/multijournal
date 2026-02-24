from __future__ import annotations

import asyncio
import fcntl
import json
import os
import pty
import struct
import termios

from fastapi import WebSocket, WebSocketDisconnect


async def terminal_session(websocket: WebSocket, directory: str) -> None:
    master_fd, slave_fd = pty.openpty()
    try:
        proc = await asyncio.create_subprocess_exec(
            "bash", "--login",
            stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
            cwd=directory, close_fds=True, preexec_fn=os.setsid,
        )
    except (FileNotFoundError, PermissionError) as e:
        os.close(slave_fd)
        os.close(master_fd)
        await websocket.send_text(f"\r\nError: {e}\r\n")
        return
    os.close(slave_fd)

    loop = asyncio.get_running_loop()
    pty_queue: asyncio.Queue[bytes] = asyncio.Queue()

    def _on_readable() -> None:
        try:
            pty_queue.put_nowait(os.read(master_fd, 4096))
        except OSError:
            loop.remove_reader(master_fd)

    loop.add_reader(master_fd, _on_readable)

    try:
        while True:
            pty_task = asyncio.create_task(pty_queue.get())
            ws_task = asyncio.create_task(websocket.receive())
            done, pending = await asyncio.wait(
                [pty_task, ws_task], return_when=asyncio.FIRST_COMPLETED
            )
            for t in pending:
                t.cancel()

            if pty_task in done:
                await websocket.send_bytes(pty_task.result())

            if ws_task in done:
                msg = ws_task.result()
                if msg["type"] == "websocket.disconnect":
                    break
                if msg.get("bytes"):
                    os.write(master_fd, msg["bytes"])
                elif msg.get("text"):
                    try:
                        ctrl = json.loads(msg["text"])
                        if ctrl.get("type") == "resize":
                            _resize(master_fd, int(ctrl["cols"]), int(ctrl["rows"]))
                    except (json.JSONDecodeError, KeyError, ValueError):
                        pass
    except (WebSocketDisconnect, OSError):
        pass
    finally:
        loop.remove_reader(master_fd)
        try:
            os.close(master_fd)
        except OSError:
            pass
        proc.kill()
        await proc.wait()


def _resize(fd: int, cols: int, rows: int) -> None:
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
