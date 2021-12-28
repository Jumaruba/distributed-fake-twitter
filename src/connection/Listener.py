import socket  

BUFFER = 1024
class Listener:
    def __init__(self, ip, port): 
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.bind()
    
    def bind(self):
        socket_address = (self.ip, self.port)
        self.socket.bind(socket_address)

    def listen(self):
        try:
            self.socket.listen()
            while True:
                user_socket, user_address  = self.socket.accept()
                print("Received :: " + user_socket.recv(BUFFER).decode("utf-8"))
                # TODO: a follower must receive info from the user it subscribes? 
        except:
            print("Error while listening")
            
    def stop(self):
        self.socket.close()
        