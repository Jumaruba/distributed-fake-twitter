from .Node import Node
import time
import sqlite3
from .database import Database

class Peer(Node):
    def __init__(self, ip, port, b_ip=None, b_port=None):
        super().__init__(ip, port, b_ip, b_port)


    async def register(self, username):
        user_info = await self.get_username_info(username)
        if user_info is None:
           self.username = username
           await self.set_user_hash_value()
           return True
        else:
            return False


    async def login(self, username): 
        user_info = await self.get_username_info(username)
        if user_info is None: 
            return False  
        self.username = username 
        return True 


    @property
    def address(self):
        return f"{self.ip}:{self.port}"


    # Creates a message to be added to the timeline.
    def create_message(self, message_body: str):
        # should contain  the time it was created and sync this time with ntp (??)
        return {
            "username": self.username,
            "timestamp": time.now(),
            "body": message_body,
        }


    def subscribe(self): 
        ... 


    # Set's a value for the key self.username in the network.
    async def set_user_hash_value(self):
        await self.server.set(self.username, self.build_table_value())


    # Get the value associated with the given username from the network. 
    async def get_username_info(self, username: str):
        return await self.server.get(username, default=None)


    # Creates the values to the table in the kademlia. 
    def build_table_value(self):
        # Suggestions: who follows him, who he is following, whoms information he is storing, the last message sent. 
        return {"ip": self.ip, "port": self.port}


    def save_message(self):
        # async .......
        ...


    def print_timeline(self):
        print(Database.get_messages())
