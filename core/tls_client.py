import asyncio
import ssl
from control.rate_limiter import RateLimiter
from stats import GLOBAL_STATS

async def tls_client(host, port, payload: bytes, rate: float, duration: int):
    ssl_ctx = ssl.create_default_context()
    limiter = RateLimiter(rate)

    end = asyncio.get_event_loop().time() + duration

    reader, writer = await asyncio.open_connection(
        host=host,
        port=port,
        ssl=ssl_ctx,
        server_hostname=host
    )

    sent = 0
    try:
        while asyncio.get_event_loop().time() < end:
            await limiter.wait()
            writer.write(payload)
            await writer.drain()
            sent += 1
            GLOBAL_STATS.inc()

    except asyncio.CancelledError:
        pass
    
    finally:
        writer.close()
        await writer.wait_closed()

    return sent