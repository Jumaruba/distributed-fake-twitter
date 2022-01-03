import logging
import asyncio
from threading import Thread
from kademlia.network import Server
import sys


class Bootstrap(Thread):
    def __init__(self, ip, port): 
        Thread.__init__(self)
        self.set_logger()
        self.server = Server()
        self.ip = ip
        self.port = port

    def run(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.server.listen(self.port))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("Bootstrap stoped!") 
        finally:
            loop.stop()

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

def check_args():
    try:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        return ip, port
    except:
        print("Wrong number of argumets. USAGE: python bootstrap.py <ip> <port>")
    exit()
    


if __name__ == '__main__':
    Bootstrap(*check_args()).start()