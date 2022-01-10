import asyncio
import json
from threading import Thread
from ..database import Database
from .Message import Message
from ..utils import run_in_loop

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

    async def handle_request(self, reader, writer):
        # TODO: delete print in the future.
        print("Received request")

        line = await reader.read(-1)

        if line:
            message = Message.parse_json(line)
            # TODO: delete print in the future.
            print(message)

            operation = Message.get_operation(message)
            if operation == "follow":
                self.handle_follower(message)
            elif operation == "unfollow":
                self.handle_unfollow(message)
            elif operation == "post":
                self.handle_post(message)
            elif operation == "sync_posts":
                await self.handle_sync_posts(message, writer)
            else:
                print("Invalid operation")

        writer.close()

    def handle_follower(self, message) -> None:
        # TODO: delete print in the future?
        print("New follower:", message["user"])
        run_in_loop(self.peer.add_follower(message["user"]), self.peer.loop)
        run_in_loop(self.peer.send_all_previous_posts(message["user"]),
                    self.peer.loop)

    def handle_unfollow(self, message) -> None:
        # TODO: delete print in the future?
        print("This user unfollowed you:", message["user"])
        run_in_loop(self.peer.remove_follower(
            message["user"]), self.peer.loop)

    def handle_post(self, message) -> None:
        """
        Handles the reception of a post from a user that this peer is following.
        """
        if message["user"] in self.peer.info.following:
            self.peer.database.insert_post(message)

    async def handle_sync_posts(self, message, writer) -> None:
        """
        When the user is back online it requests the posts it losts while offline
        """
        posts = json.dumps(self.peer.database.get_posts_after(
            message["username"],
            message["last_post_id"]))
        writer.write(posts.encode())
        writer.write_eof()
        await writer.drain()

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
