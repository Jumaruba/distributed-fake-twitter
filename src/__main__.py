import asyncio
from asyncio.tasks import ensure_future
from threading import Thread
import sys

from .control import Controller
from .Peer import Peer
from .database import Database


def check_args():
    # Function to check if the arguments are correct
    try:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        ip_b = sys.argv[3]
        port_b = int(sys.argv[4])
        return ip, port, ip_b, port_b
    except:
        print("Wrong arguments. USAGE: python bootstrap.py <ip> <port> <bootstrap_ip> <bootstrap_port>")
    exit()


def main(ip: str, port: int, ip_b: str = None, port_b: int = None):
    peer = Peer(ip, port, ip_b, port_b)

    # NOTE The listening and bootstrapping are running forever.
    # Putting this before the operation, we are initializing the kademlia server.
    Thread(target=peer.loop.run_forever, daemon=True).start()

    if ip_b is not None:   
        controller = Controller(peer)
        controller.start()
    #else:
    #    input('Bootstrap running... Press ENTER to exit')


if __name__ == '__main__':
    peer = main(*check_args())
