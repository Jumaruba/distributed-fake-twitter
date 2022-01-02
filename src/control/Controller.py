import asyncio
import json
import time

from threading import Thread 

from ..connection import Message
from ..Peer import Peer
from .Menu import Menu


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
        future = self.handle("Welcome", options)

        # Check result
        status, message = future.result()
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
                self.run_in_loop(self.peer.set_user_hash_value())
            else:
                print(f"The user {username} does not exists")
        else:
            print(f"You're already following {username}")

    


    # -------------------------------------------------------------------------
    # Register/Login
    # -------------------------------------------------------------------------

    def register(self):
        username = input("Type your username: ")
        return self.run_in_loop(self.peer.register(username))


    def login(self):
        username = input("Type your username: ")
        return self.run_in_loop(self.peer.login(username))

    # -----------------------------------------------------------------
    # Utils
    # -----------------------------------------------------------------

    def run_in_loop(self, function):
        return asyncio.run_coroutine_threadsafe(function, self.peer.loop)

