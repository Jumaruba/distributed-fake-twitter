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
        self.listener = Listener(self.ip, self.port)

        # Create new node
        if b_port is not None:
            self.b_node = (b_ip, b_port)
            self.connect_to_bootstrap_node()
        # Create bootstrap node
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
        loop = self.create_node()
        loop.run_until_complete(self.server.bootstrap([self.b_node]))
        return loop

    def create_bootstrap_node(self):  
        return self.create_node()

    def create_node(self):
        loop = asyncio.get_event_loop()
        # loop.set_debug(True)
        loop.run_until_complete(self.server.listen(self.port))
        return loop

    # --------------------------------------------------------------------------
    # Communication with other nodes
    # --------------------------------------------------------------------------

    def listen(self):
        self.listener_thread = threading.Thread(target=self.listener.listen)
        self.listener_thread.start()

    def send_message(self, destiny_ip, detiny_port, message):
        sender = Sender(destiny_ip, detiny_port)
        sender.send(message.encode())
