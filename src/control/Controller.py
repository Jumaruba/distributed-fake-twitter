import asyncio
import time

from ..connection import Message
from ..Peer import Peer
from .Menu import Menu


class Controller:
    def __init__(self, peer: Peer) -> None:
        self.peer = peer

    def handle(self, title, options):
        option = Menu.get_option(title, list(options.keys()))
        return options[option]()

    def run(self):
        options = {
            "Create post": self.create_post,
            "Show timeline": Controller.undefined,
            "Show followers": Controller.undefined,
            "Follow a user": self.follow,
            "Exit": exit
        }
        self.handle("Main Menu", options)

    def run_in_loop(self, function):
        return asyncio.run_coroutine_threadsafe(function, self.peer.loop)

    def create_post(self):
        message_body = input("What\'s happening? ")
        message = Message.post(self.peer.new_message_id, self.peer.username, message_body)
        # TODO send to all the followers.
        self.peer.last_message_id += 1

    def follow(self):
        message = Message.follow(self.peer.username)
        self.peer.send_message("127.0.0.1", 3000, message)

    @staticmethod
    def undefined():
        print("Handling not implemented...")

    # -------------------------------------------------------------------------
    # Start menu
    # -------------------------------------------------------------------------

    def start(self):
        # NOTE, to get the results from operations task it's necessary to use function_name.result()
        options = {
            "Register": self.register,
            "Login": self.login,
            "Exit": exit
        }
        future = self.handle("Welcome", options)

        # Check result
        status, message = future.result()
        if not status:
            print("[ ERROR ]", message)
            exit()

        print("[ SUCCESS ]", message)
        self.peer.start_listening()

    def register(self):
        username = input("Type your username: ")
        return self.run_in_loop(self.peer.register(username))

    def login(self):
        username = input("Type your username: ")
        return self.run_in_loop(self.peer.login(username))
