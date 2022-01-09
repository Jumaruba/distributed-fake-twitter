import json
from .connection import Listener, Message, Sender
from .consts import GARBAGE_COLLECTOR_FREQUENCY
from .database import Database
from .KademliaInfo import KademliaInfo
from .Node import Node
from .utils import get_time
from ntplib import NTPException
import json 
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

    def logout(self):
        self.server.stop()
        print("Thank you for your business!")
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
            self.info.last_post_id -= 1
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

    async def repost(self, post_id: int):  
        
        try:   
            # Update timestamp and id of the old post
            self.database.update_post(post_id, self.username, get_time(), self.info.new_post_id) 
            post = self.database.get_post(self.info.last_post_id) 
            post['operation'] = 'post'
            post_json = json.dumps(post)

            # Resend post to followers
            for follower_username in self.info.followers:
                follower_info = await self.get_kademlia_info(follower_username)
                self.send_message(
                        follower_info.ip, follower_info.port, post_json)
            
            # Update Last Post ID
            await self.set_kademlia_info(self.username, self.info)
            return (True, "Message reposted with success")
        except NTPException:
            self.info.last_post_id -= 1
            return (False, "Could not get the timestamp of the new post!")
        except Exception as e:
            return (False, e)

    # -------------------------------------------------------------------------
    # Follow functions
    # -------------------------------------------------------------------------

    async def follow(self, username: str, message: str):
        user_info = await self.get_kademlia_info(username)

        if user_info is not None:
            messageSent = await Sender.send_message(user_info.ip, user_info.port, message)  
            # The message could not be send, because the user is offline and no one has its information stored.
            if not messageSent:
                return (False, f"You can't follow {username} right now. Lo siento...")
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
        
        def parse_post(post):
            _, post_creator, post_time, post_content = post
            post_time = post_time.split()
            post_day = post_time[0]
            post_hour = post_time[1]
            return post_creator, post_day, post_hour, post_content

        posts = map(parse_post, posts)

        for post_creator, _, post_hour, post_content in posts:
            print("[" + post_hour + "]", end=" ")
            print("<" + post_creator + ">", end=" ")
            print(post_content)
            
        input(":")
        return (True, None)

    # TODO refactor urgente
    def select_post(self):
        posts = self.database.get_old_posts(self.username, get_time())   
        
        def parse_post(post):
            post_id, post_creator, post_time, post_content = post 
            post_time = post_time.split()
            post_day = post_time[0]
            post_hour = post_time[1]
            return post_id, post_creator, post_day, post_hour, post_content

        posts = map(parse_post, posts)

        for post_id, post_creator, _, post_hour, post_content in posts:
            print("#" + str(post_id), end= " ")
            print("[" + post_hour + "]", end=" ")
            print("<" + post_creator + ">", end=" ")
            print(post_content)

        while True:
            post_id = input("Which post would you like to reshare (id or q to exit)?:")
            if post_id == "q": 
                return (False, "No post was selected to reshare")  
            # elif post_id == "": 
            #    print("You should provide an input")
            #    continue
            try:
                option = int(post_id)
                print(f"option {option}")
                has_post = self.database.has_post(option, self.username) 
                if not has_post:
                    print(f"Post {option} does not exists. Try again...")
                    continue
                return (True, option)
            except ValueError:
                print(f"Please select a valid option.") 

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
