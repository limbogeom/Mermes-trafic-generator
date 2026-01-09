import asyncio
import struct
import random
import socket

async def dns_query(domain, dns_server="8.8.8.8"):
    tid = random.randint(0, 65535)
    flags = 0x0100
    qdcount = 1

    header = struct.pack("!HHHHHH", tid, flags, qdcount, 0, 0, 0)

    question = b""
    for part in domain.split("."):
        question += bytes([len(part)]) + part.encode()
    question += b"\x00"
    question += struct.pack("!HH", 1, 1)

    packet = header + question

    loop = asyncio.get_event_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    await loop.sock_sendto(sock, packet, (dns_server, 53))
    data, _ = await loop.sock_recvfrom(sock, 512)

    sock.close()
    return data