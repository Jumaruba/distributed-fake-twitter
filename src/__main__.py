import threading
from time import sleep

from .Connection import Connection
from .Node import Node

IP = "127.0.0.1"

if __name__ == '__main__':
    print("Creating nodes...")
    node_1 = Node(3000)
    node_2 = Node(3001, IP, 3000)

    print("Connecting nodes...")
    connection_1 = Connection(IP, node_1.node_port)
    connection_2 = Connection(IP, node_1.node_port)

    print("EVENT 0")
    connection_1.bind() 
    print("EVENT 1")
    listener = threading.Thread(target=connection_1.listen)
    listener.start()

    print("Connecting to bootstrap node...")
    connection_2.connect()
    connection_2.send("HELP ME PLEASE. A MAN NEEDS HIS NUGGS".encode())
    print("EVENT 3")