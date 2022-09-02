from socket import *
from lib.ProtocolRDT.client.CommunicationSocketClient import CommunicationSocketClient
import logging 


logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.DEBUG) # Es el peor caso! 

def start():
    client_socket = CommunicationSocketClient("127.0.0.1", 8080)

    client_socket.send("Hola servidor".encode())

    print(client_socket.recv(len("recibi tu msg")))

if __name__ == '__main__':
    start()