import asyncio
import websockets
from control.rate_limiter import RateLimiter
from stats import GLOBAL_STATS

async def websocket_client(uri, message: str, rate: float, duration: int):
    limiter = RateLimiter(rate)
    end = asyncio.get_event_loop().time() + duration
    sent = 0

    async with websockets.connect(uri) as ws:
        try:
            while asyncio.get_event_loop().time() < end:
                await limiter.wait()
                await ws.send(message)
                sent += 1
                GLOBAL_STATS.inc()
        except asyncio.CancelledError:
            pass

    return sent