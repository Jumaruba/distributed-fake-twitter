from asyncio.tasks import ensure_future
import threading
import asyncio
from time import sleep

from .menu import Menu

from .Peer import Peer
from .database import Database

IP = "127.0.0.1"

async def main(): 
    print("Gimme gimme gimme a man after midnight!")
    username = input("Gimme your name, now... ")
    port = int(input("Gimme your port, user..."))
    operation = input("Gimme your desire!")
    if port != 3000:
        peer = Peer(IP, port, IP, 3000)
    else:
       peer = Peer(IP, 3000)

    if operation == "register": 
        is_registered = await peer.register(username)
        if is_registered:
            print(f"You're registered: {is_registered}")
    elif operation == "login": 
        is_logged = await peer.login(username)
        if is_logged:
            print(f"You're logged: {username}")

    peer.listen()


if __name__ == '__main__':
    asyncio.run(main())


# TODO
    # Get user form Kademlia network if it exists or create user if it does no exist?

    # print("Creating peers...")
    # peer1 = Peer(IP, 3000)
    # peer2 = Peer(IP, 3001, IP, 3000)

    # print("Start listening on peer1...")
    # peer1.listen()
    
    # print("Connect peer2 to peer1...")
    # peer2.send_message(IP, 3000, "HELP ME PLEASE. A MAN NEEDS HIS NUGGS")

