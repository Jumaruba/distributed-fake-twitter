import socket  

BUFFER = 1024
class Connection:
    def __init__(self, ip, port): 
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def bind(self):
        socket_address = self.address
        self.socket.bind(socket_address)

    def connect(self): 
        connected = False 
        # Some errors may occur, when trying to do fast connection. 
        # For this motive, it tries the connection util it works. 
        while not connected: 
            try: 
                socket_address = self.address
                self.socket.connect(socket_address)
                connected = True 
            except Exception as e: 
                pass

    def listen(self):
        try:
            self.socket.listen()
            while True:
                user_socket, user_address  = self.socket.accept()
                print(user_socket.recv(BUFFER).decode("utf-8"))
                # TODO: a follower must receive info from the user it subscribes? 
        except:
            print("Error while listening")


    def send(self, msg): 
        print("Sending", msg)
        try:
            self.socket.send(msg)
        except Exception as e:
            print("Error while sending message:", e)
        finally:
            self.socket.close()
            

    def stop(self):
        self.socket.close()
        