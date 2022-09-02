from threading import Thread
from .ClientThread import ClientThread
import logging
from ..ProtocolRDT.server.SocketListener import SocketListener
from .FilenamesMonitor import FilenamesMonitor


class Listener(Thread):
    def __init__(self, port, host, dir):
        super().__init__()
        self.welcoming_skt = SocketListener(port, host)
        logging.info("SERVER started in {}:{}"
                     .format(self.welcoming_skt.addr[0], port))
        self.clients = []
        self.dir = dir
        self.filenames_monitor = FilenamesMonitor()

    def run(self):
        try:
            working = True
            while (working):
                skt = self.welcoming_skt.accept()
                if (skt):
                    client = ClientThread(skt, self.dir,
                                          self.filenames_monitor)
                    client.start()
                    self.clients.append(client)
                    self.clean_clients()
                else:
                    working = False
            self.stop_clients()
        except Exception as e:
            logging.error("Error: {}".format(e))
        logging.info("SERVER finished in {}:{}"
                     .format(self.welcoming_skt.addr[0],
                             self.welcoming_skt.addr[1]))

    def clean_clients(self):
        new_list = []
        for i, client in enumerate(self.clients):
            if (client.finished()):
                client.join()
            else:
                new_list.append(client)

        self.clients = new_list
        logging.debug("Clients were cleaned.")

    def stop_clients(self):
        for client in self.clients:
            client.stop()
            client.join()
        logging.debug("All clients were stopped.")

    def stop(self):
        self.stop_clients()
        self.welcoming_skt.close()
