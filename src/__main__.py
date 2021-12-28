import threading
from time import sleep

from .menu import Menu

from .Peer import Peer
from .database import Database

IP = "127.0.0.1"

def main():
    option = Menu.first()
    if option == 2:
        exit()

    action = Menu.main()

    # print("Creating peers...")
    # peer1 = Peer(IP, 3000)
    # peer2 = Peer(IP, 3001, IP, 3000)

    # print("Start listening on peer1...")
    # peer1.listen()

    # print("Connect peer2 to peer1...")
    # peer2.send_message(IP, 3000, "HELP ME PLEASE. A MAN NEEDS HIS NUGGS")

if __name__ == '__main__':
    main()
