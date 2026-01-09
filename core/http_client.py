import aiohttp
import asyncio
from control.rate_limiter import RateLimiter
from stats import GLOBAL_STATS

async def http_client(url, rate: float, duration: int):
    limiter = RateLimiter(rate)
    end_time = asyncio.get_event_loop().time() + duration
    sent = 0

    async with aiohttp.ClientSession() as session:
        try:
            while asyncio.get_event_loop().time() < end_time:
                await limiter.wait()
                async with session.get(url) as resp:
                    await resp.read()
                    sent += 1
                    GLOBAL_STATS.inc()
        except asyncio.CancelledError:
            pass
    
    return sent