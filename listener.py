# coding: utf-8
import asyncio

import aiozmq
import zmq


async def do():
    stream = await aiozmq.stream.create_zmq_stream(
        zmq_type=zmq.SUB,
        connect='tcp://192.168.1.222:5556',
    )
    stream.transport.subscribe(b'')

    while True:
        msg = await stream.read()
        print(ord(msg[0]))

loop = asyncio.get_event_loop()
loop.run_until_complete(do())