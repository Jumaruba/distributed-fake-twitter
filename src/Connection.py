import socket  

class Connection:
    def __init__(self, ip, port): 
        self.ip = ip
        self.port = port 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def bind(self):
        socket_address = (self.ip, self.ip)
        self.socket.bind(socket_address)

    def connect(self):
        socket_address = (self.ip, self.ip)
        self.socket.connect(socket_address)

    def listen(self, ):
        user_socket, user_address  = self.socket.accept()
        # TODO: a follower must receive info from the user it subscribes?


    def send(self, msg):
        try:
            self.socket.sendmsg(msg)
        except:
            print("Error while sending message")
        finally:
            self.socket.close()
            

    def stop(self):
        self.socket.close()
        