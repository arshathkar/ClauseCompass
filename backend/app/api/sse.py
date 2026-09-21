import json
from typing import AsyncGenerator, Any
from fastapi.responses import StreamingResponse

async def sse_format(generator: AsyncGenerator[Any, None]) -> AsyncGenerator[str, None]:
    async for item in generator:
        event = item.get("event", "message")
        data = item.get("data", {})
        yield f"event: {event}\ndata: {json.dumps(data)}\n\n"

def sse_response(generator: AsyncGenerator[Any, None]) -> StreamingResponse:
    return StreamingResponse(
        sse_format(generator),
        media_type="text/event-stream"
    )
