import asyncio
from control.rate_limiter import RateLimiter
from stats import GLOBAL_STATS

async def tcp_client(host, port, payload: bytes, rate: float, duration: int):
    limiter = RateLimiter(rate)
    end_time = asyncio.get_event_loop().time() + duration

    reader, writer = await asyncio.open_connection(host, port)


    sent = 0
    try:
        while asyncio.get_event_loop().time() < end_time:
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