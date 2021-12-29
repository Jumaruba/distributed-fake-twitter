import asyncio
from threading import Thread
from ..Peer import Peer
from .Message import Message

BUFFER = 1024
class Listener(Thread):
    def __init__(self, ip, port, peer: Peer):
        super().__init__()
        self.ip = ip
        self.port = port
        self.peer = peer

    def __new__(cls, ip, port, peer: Peer):
        # Singleton class
        if not hasattr(cls, 'instance'):
            cls.instance = super(Listener, cls).__new__(cls)
            cls.instance.__init__(ip, port, peer)
        return cls.instance

    @staticmethod
    def get_instance():
        return cls.instance

    # -------------------------------------------------------------------------
    # Request handlings
    # -------------------------------------------------------------------------

    def handle_follow(self, message):
        print("New follower:", message["username"])
        self.peer.followers.append(message)

    @staticmethod
    async def handle_request(reader, writer):
        print("Received request")

        listener = Listener.get_instance()
        line = await reader.read(-1)

        if line:
            message = Message.parse_json(line)
            print(message)

            operation = Message.get_operation(message)
            if operation == "follow":
                listener.handle_follow(message)

            else:
                print("Invalid operation")

        writer.close()

    # -------------------------------------------------------------------------
    # Running listener functions
    # -------------------------------------------------------------------------

    async def serve(self):
        self.server = await asyncio.start_server(
            Listener.handle_request,
            self.ip,
            self.port
        )
        await self.server.serve_forever()

    def run(self):
        listener_loop = asyncio.new_event_loop()
        listener_loop.run_until_complete(self.serve())
