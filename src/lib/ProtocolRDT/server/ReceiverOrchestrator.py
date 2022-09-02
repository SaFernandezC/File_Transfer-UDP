from threading import Thread
import logging
from socket import timeout
from ..common.packet import MAX_PACKET_SIZE


class ReceiverOrchestrator(Thread):
    def __init__(self, listener_queue, listener_socket, clients):
        super().__init__()
        self.clients = clients
        self.listener_socket = listener_socket
        self.listener_queue = listener_queue
        self.listener_socket.settimeout(1)
        self.working = True

    def run(self):
        try:
            while (self.working):
                try:
                    msg, addr = self.listener_socket.recvfrom(MAX_PACKET_SIZE)
                    if (len(msg) <= 0):
                        continue
                    client = self.clients.get_client(addr)
                    if (client):
                        client.push(msg)
                    else:
                        self.listener_queue.put((msg, addr))
                except timeout:
                    pass
        except OSError:
            logging.error("Server listener is closed.")

    def stop(self):
        self.working = False
        self.join()

    def __del__(self):
        if (self.working):
            self.stop()
