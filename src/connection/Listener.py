import asyncio
from threading import Thread
BUFFER = 1024


class Listener(Thread):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    # -------------------------------------------------------------------------
    # Request handlings
    # -------------------------------------------------------------------------

    @staticmethod
    async def handle_request(reader, writer):
        while True:
            data = (await reader.readline()).strip()
            if not data:
                break
            print(data)
        writer.close()

    # -------------------------------------------------------------------------
    # Running listener functions
    # -------------------------------------------------------------------------

    async def start(self):
        self.server = await asyncio.start_server(
            Listener.handle_request,
            self.ip,
            self.port
        )
        await self.server.serve_forever()

    def run(self):
        listener_loop = asyncio.new_event_loop()
        listener_loop.run_until_complete(self.start())
