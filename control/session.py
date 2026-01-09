import asyncio
import random

class ClientSession:
    def __init__(self, client_func, pattern, base_rate, lifetime):
        self.client_func = client_func
        self.pattern = pattern
        self.base_rate = base_rate
        self.lifetime = lifetime

    async def run(self, *args):
        start = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start < self.lifetime:
            rate = self.pattern.next_rate(self.base_rate)
            await self.client_func(*args, rate=rate, duration=1)

            await asyncio.sleep(random.uniform(0.2, 1.0))