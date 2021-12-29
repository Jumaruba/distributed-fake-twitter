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
        ip_b = None
        port_b = None
        if len(sys.argv) > 3:
            ip_b = sys.argv[3]
            port_b = int(sys.argv[4])
        return ip, port, ip_b, port_b
    except:
        print("Wrong arguments")
    exit()


def main(ip: str, port: int, ip_b: str = None, port_b: int = None):
    peer = Peer(ip, port, ip_b, port_b)

    # NOTE The listening and bootstrapping are running forever.
    # Putting this before the operation, we are initializing the kademlia server.
    Thread(target=peer.loop.run_forever, daemon=True).start()

    controller = Controller(peer)
    controller.start()
    while True:
        controller.run()

    return peer


if __name__ == '__main__':
    peer = main(*check_args())
    # (reader, writer) = await asyncio.open_connection(ip, port, loop= asyncio.get_event_loop())
