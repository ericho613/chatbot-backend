import json
from typing import AsyncGenerator


async def json_line_stream(generator) -> AsyncGenerator[str, None]:
    """
    Streams newline-delimited JSON chunks.
    """
    async for chunk in generator:
        yield json.dumps({"type": "chunk", "data": chunk}) + "\n"

    yield json.dumps({"type": "done"}) + "\n"