import json

from ..connection import Message
from ..Peer import Peer
from .Menu import Menu
from ..utils import run_in_loop
from ..consts import MIN_USERNAME_SIZE, MAX_USERNAME_SIZE, MAX_POST_SIZE


class Controller:
    def __init__(self, peer: Peer) -> None:
        self.peer = peer

    def handle(self, title, options):
        option = Menu.get_option(title, list(options.keys()))
        return options[option]()

    def ignore(self):
        return

    def notify(self, result, error_callback):
        status, message = result

        # Check if there was an error
        if not status:
            print("[ERROR]", message)
            error_callback()
        elif message is not None:
            print("[SUCCESS]", message)

    def start(self):
        self.menu_1()
        while True:
            self.menu_2()

    def menu_1(self):
        # NOTE, to get the results from operations task it's necessary to use function_name.result()
        options = {
            "Register": self.register,
            "Login": self.login,
            "Exit": exit
        }
        result = self.handle("Welcome", options)
        self.notify(result, exit)

    def menu_2(self):
        options = {
            "Create post": self.post,
            "Show timeline": self.peer.show_timeline,
            "Show followers": self.peer.show_followers,
            "Show following": self.peer.show_following,
            "Follow a user": self.follow,
            "Unfollow a user": self.unfollow,
            "Exit": self.peer.delete_account
        }
        result = self.handle("Main Menu", options)
        self.notify(result, self.ignore)

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def post(self):
        message = input("What\'s happening? ")
        if len(message) > MAX_POST_SIZE:
            return (
                False,
                f"The post can have at maximum {MAX_POST_SIZE} characters!"
            )
        if len(message) == 0:
            return (
                False,
                "Was that an empty post?"
            )
        message = run_in_loop(self.peer.post(message), self.peer.loop)
        return message.result()

    def follow(self):
        username = input("Username: ")
        if len(username) > MAX_USERNAME_SIZE or len(username) < MIN_USERNAME_SIZE:
            return (
                False,
                "That's not even a valid username!"
            )
        if username == self.peer.username:
            return (
                False,
                "You can't follow yourself!"
            )
        if username in self.peer.info.following:
            return (
                False,
                f"You're already following {username}!"
            )

        message = Message.follow(self.peer.username)
        future = run_in_loop(self.peer.follow(
            username, message), self.peer.loop)
        return future.result()

    def unfollow(self):
        username = input("Username: ")

        if len(username) > MAX_USERNAME_SIZE or len(username) < MIN_USERNAME_SIZE:
            return (
                False,
                "That's not even a valid username!"
            )
        if username not in self.peer.info.following:
            return (
                False,
                f"You're not following {username}!"
            )

        message = Message.unfollow(self.peer.username)
        future = run_in_loop(self.peer.unfollow(
            username, message), self.peer.loop)
        return future.result()

    # -------------------------------------------------------------------------
    # Register/Login
    # -------------------------------------------------------------------------

    def register(self):
        username = input("Type your username: ")
        if len(username) > MAX_USERNAME_SIZE:
            return (
                False,
                f"The username cannot have more than {MAX_USERNAME_SIZE} characters!"
            )
        if len(username) < MIN_USERNAME_SIZE:
            return (
                False,
                f"The username needs to have at least {MIN_USERNAME_SIZE} characters!"
            )

        future = run_in_loop(self.peer.register(username), self.peer.loop)
        return future.result()

    def login(self):
        username = input("Type your username: ")
        future = run_in_loop(self.peer.login(username), self.peer.loop)
        return future.result()
