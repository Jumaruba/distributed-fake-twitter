import json
from .connection import Listener, Message
from .consts import GARBAGE_COLLECTOR_FREQUENCY, POST_LIFETIME
from .database import Database
from .Node import Node
from .utils import get_time
from ntplib import NTPException
import threading
import asyncio 

class Peer(Node):

    def __init__(self, ip, port, b_ip, b_port):
        super().__init__(ip, port, b_ip, b_port)
        self.last_message_id = 0
        self.followers = []
        self.following = []

    @property
    def new_message_id(self):
        self.last_message_id += 1
        return self.last_message_id

    # -------------------------------------------------------------------------
    # Main Actions
    # -------------------------------------------------------------------------

    async def register(self, username):
        user_info = await self.get_username_info(username)
        if user_info is None:
            self.username = username
            await self.set_user_hash_value()
            self.init_database()
            return (True, "Registered with success!")
        else:
            return (False, "It wasn't possible to register user...")

    async def login(self, username):
        user_info = await self.get_username_info(username)
        if user_info is None:
            return (False, "Username not found!")
        self.username = username
        self.init_database()

        await self.retrieve_kademlia_info()
        await self.retrieve_missing_posts()
        return (True, "Logged with success!")

    async def post(self, message_body: str):
        try:
            message = Message.post(self.new_message_id,
                                   self.username, message_body)
            # Adding to the database.
            self.database.insert(message)
            for follower_username in self.followers:
                follower_info = await self.get_username_info(follower_username)
                self.send_message(
                    follower_info["ip"], follower_info["port"], message)
            await self.set_user_hash_value()
            print("Post created!")
        except NTPException:
            # Not possible to create message when there's an NTP exception.
            # So, it's necessary to recover the previous last message id.
            self.last_message_id -= 1
            print("Error while trying to get the timestamp of the new post!")

    async def follow(self, username: str, message: str):
        user_info = await self.get_username_info(username)

        if user_info is not None:
            self.send_message(user_info['ip'], user_info['port'], message)
            await self.add_following(username)
            return f"Following {username}"
        else:
            return f"The user {username} does not exists"

    def show_followers(self):
        builder = "== Followers ==\n"
        for i, follower in enumerate(self.followers):
            builder += f"{str(i)} - {follower}\n"
        print(builder)

    def show_following(self):
        builder = "== Following ==\n"
        for i, following in enumerate(self.following):
            builder += f"{str(i)} - {following}\n"
        print(builder)

    def show_timeline(self):
        posts = self.database.get_all_posts()
        print(posts)

    # -------------------------------------------------------------------------
    # Handle followers/following
    # -------------------------------------------------------------------------

    async def add_follower(self, username: str):
        self.followers.append(username)
        await self.set_user_hash_value()

    async def add_following(self, username: str):
        self.following.append(username)
        await self.set_user_hash_value()

    async def send_all_posts(self, follower_username):
        try:
            follower_info = await self.get_username_info(follower_username)

            posts = self.database.get_posts(self.username)
            for post in posts:
                message = Message.post(
                    post["post_id"],
                    self.username,
                    post["body"],
                    post["timestamp"]
                )
                self.send_message(follower_info["ip"],
                                  follower_info["port"], message)
        except Exception as e:
            print(e)

    def init_database(self):
        self.database = Database(self.username)
        self.start_garbage_collection()

    # -------------------------------------------------------------------------
    # Network functions
    # -------------------------------------------------------------------------

    def start_listening(self):
        listener = Listener(self.ip, self.port, self)
        listener.daemon = True
        listener.start()

    async def set_user_hash_value(self):
        # Set's a value for the key self.username in the network.
        await self.server.set(self.username, json.dumps(self.build_table_value()))

    async def get_username_info(self, username: str) -> dict:
        # Get the value associated with the given username from the network.
        username_info = await self.server.get(username)
        if username_info is None:
            return None
        return json.loads(username_info)

    def build_table_value(self):
        # Creates the values to the table in the kademlia.
        # Suggestions: who follows him, who he is following,
        # whoms information he is storing, the last message sent.
        return {
            "ip": self.ip,
            "port": self.port,
            "last_message_id": self.last_message_id,
            "followers": self.followers,
            "following": self.following
        }

    async def retrieve_kademlia_info(self):
        user_info = await self.get_username_info(self.username)
        self.followers = user_info["followers"]
        self.following = user_info["following"]
        self.last_message_id = user_info["last_message_id"]

    async def retrieve_missing_posts(self):
        async def sync_with_user(message, user_info):
            reader, writer = await asyncio.open_connection(user_info["ip"], user_info["port"])

            writer.write(message.encode())
            writer.write_eof()
            await writer.drain()

            return await reader.read()

        for user in self.following:
            message = Message.sync_posts(
                self.username,
                self.database.last_message(user),
                user)

            # Try with the owner of the messages
            user_info = await self.get_username_info(user)
            try: 
                posts = await sync_with_user(message, user_info)
            except ConnectionRefusedError:
                # Otherwise try with all the other followers
                followers_username = user_info["followers"]
                for follower in followers_username:
                    follower_info = await self.get_username_info(follower) 
                    try: 
                        posts = await sync_with_user(message, follower_info) 
                    except ConnectionRefusedError:
                        continue
                    break
                else:
                    raise "No peer could provide the posts"
            print(posts)
            self.database.add_posts(posts)

    def print_timeline(self):
        print(self.database.get_all_posts())

    # -------------------------------------------------------------------------
    # Garbage Collector
    # -------------------------------------------------------------------------

    def start_garbage_collection(self):
        threading.Timer(GARBAGE_COLLECTOR_FREQUENCY,
                        self.garbage_collector).start()

    def garbage_collector(self):
        self.database.delete(self.username, get_time())
        self.start_garbage_collection()
