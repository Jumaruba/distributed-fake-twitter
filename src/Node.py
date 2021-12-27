from kademlia.network import Server 
import logging 
import asyncio


class Node: 
    def __init__(self, port, b_ip, b_port = None):
        self.set_logger()
        
        self.server = Server()
        
        self.node_port = port
        
        # Create new node
        if b_port is not None:
            self.b_node = (b_ip, b_port)
            self.connect_to_bootstrap_node()

        # Create bootstrap node
        else:
            self.create_bootstrap_node()
    
    def set_logger(self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log = logging.getLogger('kademlia')
        log.addHandler(handler)
        # log.setLevel(logging.DEBUG)

    def create_bootstrap_node(self):  
        loop = asyncio.get_event_loop()
        # loop.set_debug(True)

        loop.run_until_complete(self.server.listen(self.node_port))

        try: 
            loop.run_forever()
        except:
            pass 
        finally: 
            self.server.stop()
            self.server.close() 

    def connect_to_bootstrap_node(self): 
        loop = asyncio.get_event_loop()
        # loop.set_debug(True)

        loop.run_until_complete(self.server.listen(self.node_port))
        loop.run_until_complete(self.server.bootstrap([self.b_node]))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass 
        finally:
            self.server.stop() 
            loop.close()