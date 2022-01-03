import logging
import asyncio
import threading

from kademlia.network import Server

from .connection import Sender
from .connection import Listener


class Node:
    def __init__(self, ip, port, b_ip, b_port):
        self.set_logger()
        self.server = Server()
        self.ip = ip
        self.port = port

        # NOTE When a function reaches an io operation, it will switch between the functions called with this loop.
        # The program has only one event loop.
        self.loop = asyncio.get_event_loop()

        self.b_node = (b_ip, b_port)
        self.loop.run_until_complete(self.server.listen(self.port))
        self.loop.run_until_complete(self.server.bootstrap([self.b_node]))

    # --------------------------------------------------------------------------
    # Logger
    # --------------------------------------------------------------------------

    def set_logger(self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log = logging.getLogger('kademlia')
        log.addHandler(handler)

    # --------------------------------------------------------------------------
    # Communication with other nodes
    # --------------------------------------------------------------------------

    def send_message(self, destiny_ip, detiny_port, message):
        asyncio.run_coroutine_threadsafe(Sender.send_message(destiny_ip, detiny_port, message), loop=self.loop)
