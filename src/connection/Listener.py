import asyncio
from threading import Thread

from .Message import Message

BUFFER = 1024
class Listener(Thread):
    def __init__(self, ip, port, peer):
        super().__init__()
        self.ip = ip
        self.port = port
        self.peer = peer

    # -------------------------------------------------------------------------
    # Request handlings
    # -------------------------------------------------------------------------

    def handle_follow(self, message):
        print("New follower:", message["username"])
        self.peer.followers.append(message)

    async def handle_request(self, reader, writer):
        print("Received request")

        line = await reader.read(-1)

        if line:
            message = Message.parse_json(line)
            print(message)

            operation = Message.get_operation(message)
            if operation == "follow":
                self.handle_follow(message)

            else:
                print("Invalid operation")

        writer.close()

    # -------------------------------------------------------------------------
    # Running listener functions
    # -------------------------------------------------------------------------

    async def serve(self):
        self.server = await asyncio.start_server(
            self.handle_request,
            self.ip,
            self.port
        )
        await self.server.serve_forever()

    def run(self):
        listener_loop = asyncio.new_event_loop()
        listener_loop.run_until_complete(self.serve())
