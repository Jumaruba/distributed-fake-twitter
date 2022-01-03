import json

from ..connection import Message
from ..Peer import Peer
from .Menu import Menu
from ..utils import run_in_loop


class Controller:
    def __init__(self, peer: Peer) -> None:
        self.peer = peer
    

    def handle(self, title, options):
        option = Menu.get_option(title, list(options.keys())) 
        return options[option]() 


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
        status, message = self.handle("Welcome", options)

        # Check result
        if not status:
            print("[ ERROR ]", message)
            exit()

        print("[ SUCCESS ]", message)
        self.peer.start_listening() 


    def menu_2(self):
        options = {
            "Create post": self.post,
            "Show timeline": self.peer.show_timeline,
            "Show followers": self.peer.show_followers,
            "Show following": self.peer.show_following,
            "Follow a user": self.follow,
            "Exit": exit
        }
        self.handle("Main Menu", options)

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def post(self): 
        message = input("What\'s happening? ")
        run_in_loop(self.peer.post(message), self.peer.loop)


    def follow(self):
        username = input("Username: ")
        message = Message.follow(self.peer.username)

        if username == self.peer.username:
            print("[ERROR] You can't follow yourself!")
        elif username not in self.peer.following:
            message = run_in_loop(self.peer.follow(username, message), self.peer.loop)
            print(message.result())
        else:
            print(f"[ERROR] You're already following {username}")

    # -------------------------------------------------------------------------
    # Register/Login
    # -------------------------------------------------------------------------

    def register(self):
        username = input("Type your username: ")
        if username:
            future = run_in_loop(self.peer.register(username), self.peer.loop)
            return future.result()
        return (False, "Empty user is not allowed!")


    def login(self):
        username = input("Type your username: ")
        future = run_in_loop(self.peer.login(username), self.peer.loop)
        return future.result()
