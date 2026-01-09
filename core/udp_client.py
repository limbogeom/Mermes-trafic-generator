import asyncio
import socket
from control.rate_limiter import RateLimiter
from stats import GLOBAL_STATS

async def udp_client(host, port, payload: bytes, rate: float, duration: int):
    limiter = RateLimiter(rate)
    end_time = asyncio.get_event_loop().time() + duration

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    sent = 0
    loop = asyncio.get_event_loop()

    try:
        while loop.time() < end_time:
            await limiter.wait()
            await loop.sock_sendto(sock, payload, (host, port))
            sent += 1
            GLOBAL_STATS.inc()

    except asyncio.CancelledError:
        pass

    finally:
        sock.close()
        
    return sent