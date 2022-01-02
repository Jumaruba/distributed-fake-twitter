import asyncio
import json
import time

from threading import Thread 
from src.database.Database import Database

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
            "Create post": self.post,
            "Show timeline": Controller.undefined,
            "Show followers": self.peer.show_followers,
            "Show following": self.peer.show_following,
            "Follow a user": self.follow,
            "Exit": exit
        }
        self.handle("Main Menu", options)

    def run_in_loop(self, function):
        return asyncio.run_coroutine_threadsafe(function, self.peer.loop)

    def post(self): 
        message = input("What\'s happening? ")
        self.run_in_loop(self.peer.post(message))
        #Thread(target=self.run_in_loop(self.peer.post(message))).start()

    def follow(self):
        username = input("Username: ")
        message = Message.follow(self.peer.username)

        if username == self.peer.username:
            print("You can't follow yourself!")
        elif username not in self.peer.following:
            user_info_json = self.run_in_loop(self.peer.get_username_info(username)).result()
            
            if user_info_json is not None:  
                user_info = json.loads(user_info_json)
                self.peer.send_message(user_info['ip'], user_info['port'], message)
                self.peer.following.append(username)
            else:
                print(f"The user {username} does not exists")
        else:
            print(f"You're already following {username}")
    
    def register(self):
        username = input("Type your username: ")
        return self.run_in_loop(self.peer.register(username))


    def login(self):
        username = input("Type your username: ")
        return self.run_in_loop(self.peer.login(username))


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


