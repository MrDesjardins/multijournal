from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator


async def stream_journal(unit: str, lines: int) -> AsyncGenerator[str, None]:
    process = await asyncio.create_subprocess_exec(
        "journalctl",
        "-u",
        unit,
        "-n",
        str(lines),
        "-f",
        "--no-pager",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )

    try:
        assert process.stdout is not None
        async for line in process.stdout:
            yield line.decode("utf-8", errors="replace").rstrip("\n")
    finally:
        process.kill()
        await process.wait()
