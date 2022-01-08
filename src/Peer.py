import json
from .connection import Listener, Message
from .consts import GARBAGE_COLLECTOR_FREQUENCY
from .database import Database
from .KademliaInfo import KademliaInfo
from .Node import Node
from .utils import get_time
from ntplib import NTPException
import threading
import asyncio


class Peer(Node):

    def __init__(self, ip, port, bootstrap_file: str):
        super().__init__(ip, port, bootstrap_file)
        self.info = KademliaInfo(ip, port, [], [], 0)

    # -------------------------------------------------------------------------
    # Login / Register
    # -------------------------------------------------------------------------

    async def register(self, username):
        previous_user_info = await self.get_kademlia_info(username)
        print(self.info)
        if previous_user_info is None:
            self.username = username
            await self.set_kademlia_info(self.username, self.info)
            self.init_database()
            return (True, "Registered with success!")
        else:
            return (False, "It wasn't possible to register user...")

    async def login(self, username):
        user_info = await self.get_kademlia_info(username)
        if user_info is None:
            return (False, "Username not found!")
        self.username = username
        self.info = user_info
        self.init_database()
        await self.retrieve_missing_posts()
        return (True, "Logged with success!")

    def init_database(self):
        """
        Initializes the sqlite database and the garbage collector to clean the oldest messages with some frequency.
        """
        self.database = Database(self.username)
        self.start_garbage_collection()

    def delete_account(self):
        self.server.stop()
        print("Account deleted. Thank you for your business!")
        exit()

    # -------------------------------------------------------------------------
    # Post functions
    # -------------------------------------------------------------------------

    async def post(self, message_body: str):
        try:
            message = Message.post(self.info.new_post_id,
                                   self.username, message_body)
            self.database.insert(message)
            for follower_username in self.info.followers:
                follower_info = await self.get_kademlia_info(follower_username)
                self.send_message(
                    follower_info.ip, follower_info.port, message)
            await self.set_kademlia_info(self.username, self.info)
            return (True, "Post created!")
        except NTPException:
            # Not possible to create message when there's an NTP exception.
            # So, it's necessary to recover the previous last message id.
            self.last_post_id -= 1
            return (False, "Could not get the timestamp of the new post!")
        except Exception as e:
            return (False, e)

    async def send_all_previous_posts(self, follower_username) -> None:
        """
        Send all the posts to a specific follower.
        """
        try:
            follower_info: KademliaInfo = await self.get_kademlia_info(follower_username)

            posts = self.database.get_posts(self.username, get_time())

            for post in posts:
                self.send_previous_post(
                    post, follower_info.ip,
                    follower_info.port
                )

        except Exception as e:
            print(e)

    def send_previous_post(self, post, ip: str, port: int) -> None:
        message = Message.post(
            post["post_id"],
            self.username,
            post["body"],
            post["timestamp"]
        )
        self.send_message(ip, port, message)

    async def retrieve_missing_posts(self):
        async def sync_with_user(message, user_info):
            reader, writer = await asyncio.open_connection(user_info.ip, user_info.port)

            writer.write(message.encode())
            writer.write_eof()
            await writer.drain()

            return await reader.read()

        for user in self.info.following:
            message = Message.sync_posts(
                self.username,
                self.database.last_message(user),
                user)

            # Try with the owner of the messages
            user_info = await self.get_kademlia_info(user)
            try:
                posts = await sync_with_user(message, user_info)
            except ConnectionRefusedError:
                # Otherwise try with all the other followers
                followers_username = user_info.followers
                for follower in followers_username:
                    follower_info = await self.get_kademlia_info(follower)
                    try:
                        posts = await sync_with_user(message, follower_info)
                    except ConnectionRefusedError:
                        continue
                    break
                else:
                    print("[WARNING] No peer could provide the posts of this user")
                    return
            print(posts)
            self.database.add_posts(posts)

    # -------------------------------------------------------------------------
    # Follow functions
    # -------------------------------------------------------------------------

    async def follow(self, username: str, message: str):
        user_info = await self.get_kademlia_info(username)

        if user_info is not None:
            self.send_message(user_info.ip, user_info.port, message)
            await self.add_following(username)
            return (True, f"Following {username}")
        else:
            return (False, f"The user {username} does not exist")

    async def unfollow(self, username: str, message: str):
        user_info = await self.get_kademlia_info(username)

        if user_info is not None:
            self.send_message(user_info.ip, user_info.port, message)
            await self.remove_following(username)
            return (True, f"Unfollowing {username}")
        else:
            return (False, f"The user {username} does not exist")

    async def add_follower(self, username: str) -> None:
        self.info.followers.append(username)
        await self.set_kademlia_info(self.username, self.info)

    async def add_following(self, username: str) -> None:
        self.info.following.append(username)
        await self.set_kademlia_info(self.username, self.info)

    async def remove_follower(self, username: str) -> None:
        self.info.followers.remove(username)
        await self.set_kademlia_info(self.username, self.info)

    async def remove_following(self, username: str) -> None:
        self.info.following.remove(username)
        await self.set_kademlia_info(self.username, self.info)

    # -------------------------------------------------------------------------
    # Output functions
    # -------------------------------------------------------------------------

    def show_followers(self):
        builder = "== Followers ==\n"
        for i, follower in enumerate(self.info.followers):
            builder += f"{i} - {follower}\n"
        print(builder)
        input(":")
        return (True, None)

    def show_following(self):
        builder = "== Following ==\n"
        for i, following in enumerate(self.info.following):
            builder += f"{i} - {following}\n"
        print(builder)
        input(":")
        return (True, None)

    def show_timeline(self):
        posts = self.database.get_all_posts()
        print(posts)
        input(":")
        return (True, None)

    # -------------------------------------------------------------------------
    # Garbage Collector
    # -------------------------------------------------------------------------

    def start_garbage_collection(self):
        threading.Timer(GARBAGE_COLLECTOR_FREQUENCY,
                        self.garbage_collector).start()

    def garbage_collector(self):
        self.database.delete(self.username, get_time())
        self.start_garbage_collection()

    # -------------------------------------------------------------------------
    # Network/Kademlia functions
    # -------------------------------------------------------------------------

    def start_listening(self):
        listener = Listener(self.info.ip, self.info.port, self)
        listener.daemon = True
        listener.start()
