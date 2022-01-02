import asyncio
import json
from threading import Thread
from ..database import Database
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

    def handle_follower(self, message):
        print("New follower:", message["username"])
        self.peer.followers.append(message["username"])

    async def handle_request(self, reader, writer):
        print("Received request")

        line = await reader.read(-1)

        if line:
            message = Message.parse_json(line)
            print(message)

            operation = Message.get_operation(message)
            if operation == "follow":
                self.handle_follower(message)
            elif operation == "post": 
                self.handle_post(message)
            else:
                print("Invalid operation")

        writer.close()

    def handle_post(self, message):
        self.peer.database.insert(json.dumps(message))
        
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
