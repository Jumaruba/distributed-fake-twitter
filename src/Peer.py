from .connection import Listener, Message
from .database import Database
from .Node import Node
from ntplib import NTPException
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

    async def post(self, message_body: str): 
        try: 
            message = Message.post(self.new_message_id, self.username, message_body) 
            # Adding to the database.  
            Database().insert(message)
            for follower_username in self.followers: 
                follower_info = await self.get_username_info(follower_username)
                print(follower_info)
                print("after await")
                self.send_message(follower_info.ip, int(follower_info.port), message) 
            print("After for loop")
        except NTPException:
            # Not possible to create message when there's an NTP exception. 
            # So, it's necessary to recover the previous last message id.  
            self.last_message_id -= 1
            print("Error creating post!")
        
        print("Post created!")
        
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
