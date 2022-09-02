from socket import SOCK_DGRAM, AF_INET, socket
from ..common.PayloadSender import PayloadSender
from ..common.PayloadReceiver import PayloadReceiver
from .PacketSender import PacketSender
from .PacketReceiver import PacketReceiver
import logging
from ..utils import SR_SIZE


class CommunicationSocketClient:
    def __init__(self, server_host, server_port):
        self.host = server_host
        self.port = server_port
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        addr = (server_host, server_port)

        self.packet_sender = PacketSender(self.client_socket, addr)
        self.payload_sender = PayloadSender(self.packet_sender, SR_SIZE)
        self.payload_receiver = PayloadReceiver(self.packet_sender)
        self.packet_receiver = PacketReceiver(self.client_socket, addr,
                                              self.payload_sender,
                                              self.payload_receiver)

        self.packet_receiver.start()

    def connect(self):
        self.payload_sender.send_syn()

    def send(self, payload):
        self.payload_sender.send(payload)

    def recv(self, size):
        return self.payload_receiver.recv(size)

    def close(self, forced):
        logging.debug("CommunicationSocketClient close called.")
        self.payload_sender.stop(forced)
        self.packet_receiver.stop()
        self.client_socket.close()

    def __del__(self):
        self.close(False)
