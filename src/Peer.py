from .connection import Listener
from .database import Database
from .Node import Node


class Peer(Node):
    def __init__(self, ip, port, b_ip=None, b_port=None):
        super().__init__(ip, port, b_ip, b_port)
        self.last_message_id = 0
        self.followers = []         # The followers username

    @property
    def new_message_id(self):
        self.last_message_id += 1
        return self.last_message_id

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    async def register(self, username):
        user_info = await self.get_username_info(username)
        if user_info is None:
            self.username = username
            await self.set_user_hash_value()
            return (True, "Registered with success!")
        else:
            return (False, "It wasn't possible to register user...")

    async def login(self, username):
        user_info = await self.get_username_info(username)
        if user_info is None:
            return (False, "Username not found!")
        self.username = username
        return (True, "Logged with success!")

    def subscribe(self):
        ...

    # -------------------------------------------------------------------------
    # Network functions
    # -------------------------------------------------------------------------

    def start_listening(self):
        listener = Listener(self.ip, self.port, self)
        listener.daemon = True
        listener.start()

    async def set_user_hash_value(self):
        # Set's a value for the key self.username in the network.
        await self.server.set(self.username, str(self.build_table_value()))

    async def get_username_info(self, username: str):
        # Get the value associated with the given username from the network.
        return await self.server.get(username)

    def build_table_value(self):
        # Creates the values to the table in the kademlia.
        # Suggestions: who follows him, who he is following,
        # whoms information he is storing, the last message sent.
        return {
            "ip": self.ip,
            "port": self.port,
            "last_message_id": self.last_message_id,
            "followers": self.followers
        }

    def save_message(self):
        # async .......
        ...

    def print_timeline(self):
        print(Database.get_messages())
