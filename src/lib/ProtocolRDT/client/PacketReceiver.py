from threading import Thread
from ..common.packet import Packet
from socket import timeout
import logging
from ..utils import TIMEOUT_RECVFROM, MAX_PACKET_SIZE


class PacketReceiver(Thread):
    def __init__(self, socket, server_addr, payload_sender, payload_receiver):
        super().__init__()
        self.payload_sender = payload_sender
        self.payload_receiver = payload_receiver

        self.socket = socket
        socket.settimeout(TIMEOUT_RECVFROM)

        self.working = True
        self.server_addr = server_addr

    def send_type_packet(self, packet):
        if (packet.is_check_connection()):
            self.payload_sender.check_connection_received(packet)
        elif (packet.is_ack() or packet.is_syn_ack()):
            self.payload_sender.ack_received(packet)
        else:
            self.payload_receiver.push(packet)

    def run(self):
        while (self.working):
            try:
                bytes_packet, addr = self.socket.recvfrom(MAX_PACKET_SIZE)

                if (addr != self.server_addr):
                    logging.error("A packet from an"
                                  " invalid address was received.")
                    continue

                packet = Packet.packet_from_bytes(bytes_packet)
                if (not packet):
                    logging.debug("An invalid packet was received.")
                else:
                    self.send_type_packet(packet)
            except timeout:
                pass
            except (OSError, Exception):
                logging.error("Packet Receiver was closed.")
                break

        logging.debug("Packet Receiver finished its execution.")

    def stop(self):
        self.working = False
        self.payload_receiver.stop()
        self.join()
