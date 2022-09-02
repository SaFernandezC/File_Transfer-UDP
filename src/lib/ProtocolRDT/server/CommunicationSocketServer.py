from ..common.PayloadSender import PayloadSender
from ..common.PayloadReceiver import PayloadReceiver
from .PacketSender import PacketSender
from .PacketReceiver import PacketReceiver
import logging
from ..utils import SR_SIZE


class CommunicationSocketServer:
    def __init__(self, host, port, sender_orchestrator):
        self.closed = False
        self.host = host
        self.port = port

        self.packet_sender = PacketSender(sender_orchestrator, (host, port))
        self.payload_sender = PayloadSender(self.packet_sender, SR_SIZE)

        self.payload_receiver = PayloadReceiver(self.packet_sender)
        self.packet_receiver = PacketReceiver(self.payload_sender,
                                              self.payload_receiver)
        self.packet_receiver.start()

        self.working = True

    def push(self, payload):
        self.packet_receiver.push(payload)

    def syn_received(self, packet):
        self.payload_sender.syn_received(packet)

    def is_working(self):
        return self.working

    def check_working(self):
        if (not self.working):
            raise Exception("Socket is closed")

    def send(self, payload):
        self.check_working()
        self.payload_sender.send(payload)

    def recv(self, size):
        self.check_working()
        return self.payload_receiver.recv(size)

    def close(self, forced):
        self.working = False
        self.payload_sender.stop(forced)
        self.payload_receiver.stop()
        self.packet_receiver.stop()
        logging.debug("CommunicationSocketServer close, addr: {}:{}"
                      .format(self.host, self.port))

    def __del__(self):
        logging.debug("CommunicationSocketServer destructor, addr: {}:{}"
                      .format(self.host, self.port))
        self.close(False)
