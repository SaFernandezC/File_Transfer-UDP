from threading import Thread
from ..common.packet import Packet
import logging
from queue import Queue


class PacketReceiver(Thread):
    def __init__(self, payload_sender, payload_receiver):
        super().__init__()
        self.payload_sender = payload_sender
        self.payload_receiver = payload_receiver
        self.queue = Queue()
        self.working = True

    def run(self):
        while(self.working):
            packet = self.queue.get()
            if (not packet):
                logging.debug("An invalid packet was received.")
            else:
                if (packet.is_check_connection()):
                    self.payload_sender.check_connection_received(packet)
                elif (packet.is_ack()):
                    self.payload_sender.ack_received(packet)
                elif (packet.is_syn()):
                    self.payload_sender.syn_received(packet)
                else:
                    self.payload_receiver.push(packet)

    def push(self, bytes_packet):
        packet = Packet.packet_from_bytes(bytes_packet)
        self.queue.put(packet)

    def stop(self):
        self.working = False
        self.queue.put(None)
        if self.is_alive():
            self.join()

    def __del__(self):
        self.stop()
