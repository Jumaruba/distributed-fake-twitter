import logging
import asyncio
import threading

from kademlia.network import Server

from .connection import Sender
from .connection.Listener import Listener


class Node:
    def __init__(self, ip, port, b_ip=None, b_port=None):
        self.set_logger()
        self.server = Server()
        self.ip = ip
        self.port = port

        # NOTE When a function reaches an io operation, it will switches between the functions called with this loop.
        # The program has only one event loop.
        self.loop = asyncio.get_event_loop()

        if b_port is not None:
            self.b_node = (b_ip, b_port)
            self.connect_to_bootstrap_node()
        else:
            self.create_bootstrap_node()

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
        # log.setLevel(logging.DEBUG)

    # --------------------------------------------------------------------------
    # Node Creation
    # --------------------------------------------------------------------------

    def connect_to_bootstrap_node(self):
        self.loop.run_until_complete(self.server.listen(self.port))
        self.loop.run_until_complete(self.server.bootstrap([self.b_node]))

    def create_bootstrap_node(self):
        self.loop.run_until_complete(self.server.listen(self.port))

    # --------------------------------------------------------------------------
    # Communication with other nodes
    # --------------------------------------------------------------------------

    def send_message(self, destiny_ip, detiny_port, message):
        asyncio.run_coroutine_threadsafe(Sender.send_message(destiny_ip, detiny_port, message), loop=self.loop)

    def start_listening(self):
        self.listener = Listener(self.ip, self.port)
        self.listener.daemon = True
        self.listener.start()
