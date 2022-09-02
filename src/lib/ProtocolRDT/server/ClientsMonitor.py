from threading import Lock
import logging


class ClientsMonitor:
    def __init__(self):
        self.clients = {}
        self.lock = Lock()

    def get_client(self, addr):
        with self.lock:
            if (addr in self.clients):
                return self.clients[addr]
            return None

    def add_client_if_absent(self, addr, client):
        with self.lock:
            if (addr not in self.clients):
                self.clients[addr] = client
                return True
            client = self.clients[addr]
            logging.debug("New reference CommunicationSocketServer.")
            return False

    def clean_clients(self):
        with self.lock:
            self.clients = {key: value for (key, value)
                            in self.clients.items() if value.is_working()}
