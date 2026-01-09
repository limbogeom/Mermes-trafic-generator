import asyncio
import time

class RateLimiter:
    def __init__(self, rate_per_sec: float):
        self.interval = 1.0 / rate_per_sec
        self._last = 0.0

    async def wait(self):
        now = time.monotonic()
        delta = now - self._last
        if delta < self.interval:
            await asyncio.sleep(self.interval - delta)
        self._last = time.monotonic()