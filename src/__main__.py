from asyncio.tasks import ensure_future
from threading import Thread 
import asyncio
from time import sleep

from .menu import Menu

from .Peer import Peer
from .database import Database

IP = "127.0.0.1"

def main(): 
    peer_no = int(input("Peer number: "))
    operation = input("Operation: ")
    if peer_no == 1: 
        # Bootstrap peer 
        peer = Peer(IP, 3001)
    else:
        # Peer to be registered 
        peer = Peer(IP, 3006, IP, 3001)
        peer.send_message(IP, 3001, "HI".encode())


    # NOTE The listening and bootstrapping are running forever. 
    # Putting this before the operation, we are initializing the kademlia server. 
    Thread(target=peer.loop.run_forever, daemon=True).start()

    if operation == "R":
        operation_task = asyncio.run_coroutine_threadsafe(peer.register("bob"), peer.loop)
    elif operation == "L": 
        operation_task = asyncio.run_coroutine_threadsafe(peer.login("bob"), peer.loop)
    else: 
        return "OK"

    return operation_task.result()
        
if __name__ == '__main__': 
    print(main())
    (reader, writer) = await asyncio.open_connection(ip, port, loop= asyncio.get_event_loop())

    while True: 
        ...

"""
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
"""

# TODO
    # Get user form Kademlia network if it exists or create user if it does no exist?

    # print("Creating peers...")
    # peer1 = Peer(IP, 3000)
    # peer2 = Peer(IP, 3001, IP, 3000)

    # print("Start listening on peer1...")
    # peer1.listen()
    
    # print("Connect peer2 to peer1...")
    # peer2.send_message(IP, 3000, "HELP ME PLEASE. A MAN NEEDS HIS NUGGS")

