from socket import SO_REUSEADDR, SOL_SOCKET, SOCK_DGRAM, AF_INET, socket
from lib.ProtocolRDT.server.CommunicationSocketServer import (
                                                    CommunicationSocketServer)
from .ReceiverOrchestrator import ReceiverOrchestrator
from .SenderOrchestrator import SenderOrchestrator
from .ClientsMonitor import ClientsMonitor
from queue import Queue
import logging
from ..common.packet import Packet, PacketType
from ..utils import HOST_DEFAULT


class SocketListener:
    def __init__(self, port, host=HOST_DEFAULT):
        self.addr = (host, port)
        self.skt = socket(AF_INET, SOCK_DGRAM)
        self.skt.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.skt.bind((host, port))

        self.listener_queue = Queue()
        self.clients = ClientsMonitor()
        self.init_orchestrators()

        logging.debug("Socket Accepter was innitialized.")
        self.closed = False

    def init_orchestrators(self):
        self.recv_orchestrator = ReceiverOrchestrator(
            self.listener_queue, self.skt, self.clients)
        self.send_orchestrator = SenderOrchestrator(self.skt)

        self.recv_orchestrator.start()

    def check_syn_packet(self, packet):
        if (not packet.is_syn()):
            logging.debug("First message is not SYN. The type is: {}"
                          .format(PacketType(packet.packet_type)))
            return False
        else:
            return True

    def generate_new_client(self, packet, addr):
        client_socket = CommunicationSocketServer(addr[0], addr[1],
                                                  self.send_orchestrator)
        new_client = self.clients.add_client_if_absent(addr, client_socket)

        logging.debug("New client, with syn received.")
        client_socket.push(packet.packet_to_bytes())

        return new_client, client_socket

    def accept(self):
        new_client = False
        client_socket = None
        self.clients.clean_clients()

        while (not new_client and not self.closed):
            bytes_msg, addr = self.listener_queue.get()
            packet = Packet.packet_from_bytes(bytes_msg)
            if (not packet):
                logging.debug("A (None, None) is received to stop the accept.")
                continue
            if (self.check_syn_packet(packet)):
                new_client, client_socket = (
                                self.generate_new_client(packet, addr))

        logging.debug("Accept finished.")
        return client_socket

    def close(self):
        try:
            if (not self.closed):
                self.skt.close()
                logging.debug("Listener Socket File Descriptor is closed.")
        except OSError as e:
            logging.error("An error occurred while"
                          " closing the listener file descriptor.")
            logging.error(str(e))
        self.closed = True
        self.listener_queue.put((None, None))
        logging.debug("Listener Socket was closed.")
