import socket  

class Sender:
    def __init__(self, ip, port): 
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connect()

    def connect(self): 
        connected = False 
        # Some errors may occur, when trying to do fast connection. 
        # For this motive, it tries the connection util it works. 
        while not connected: 
            try: 
                socket_address = (self.ip, self.port)
                self.socket.connect(socket_address)
                connected = True 
            except Exception: 
                pass

    def send(self, msg): 
        print("Sending :: ", msg.decode("utf-8"))
        try:
            self.socket.send(msg)
        except Exception as e:
            print("Error while sending message:", e)
        finally:
            self.socket.close()
            

    def stop(self):
        self.socket.close()
        