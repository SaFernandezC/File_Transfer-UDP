from threading import Timer, Lock, Condition
from .packet import PacketType, Packet
import logging
from ..utils import MAX_TRIES, TIMEOUT_LIMIT, SYN_SEQ_NUM


class PacketOrchestrator:
    def __init__(self, sender, timeout_limit=TIMEOUT_LIMIT):
        self.sender = sender
        self.packets = {}
        self.next_seq_num = 1
        self.timeout_limit = timeout_limit
        self.closed = False
        self.tries = 0

        self.lock = Lock()
        self.cv = Condition(self.lock)

    def working(self):
        return not self.closed

    def create_timer(self, packet):
        return Timer(self.timeout_limit, self.resend_packet, [packet], {})

    def cancel_timer(self, seq_num):
        if (seq_num in self.packets):
            self.packets[seq_num].cancel()
            self.packets.pop(seq_num)

    def add_packet(self, packet):
        if (self.closed):
            raise Exception("Sender is closed.")

        self.cancel_timer(packet.seq_num)
        self.packets[packet.seq_num] = self.create_timer(packet)
        self.packets[packet.seq_num].start()

    def new_packet(self, data):
        with self.lock:
            packet = Packet(data, self.next_seq_num)
            self.add_packet(packet)
            self.next_seq_num += 1
            return packet

    def syn_packet(self):
        with self.lock:
            packet = Packet(bytes(0), SYN_SEQ_NUM, PacketType.SYN)
            self.add_packet(packet)
            return packet

    def ack_received(self, ack_num):
        logging.debug("ACK received: {}".format(ack_num))
        with self.cv:
            self.tries = 0
            self.cancel_timer(ack_num)
            self.cv.notify_all()

    def tries_exceded(self):
        if (self.tries >= MAX_TRIES):
            self.shutdown()
            return True
        else:
            return False

    def check_connection(self, packet):
        with self.cv:
            if packet.seq_num in self.packets:
                if (not self.tries_exceded()):
                    self.tries += 1
                    self.add_packet(packet)
                    self.sender.resend(packet)

    def resend_packet(self, packet):
        try:
            logging.debug("Timeout packet: {} - {}"
                          .format(packet.seq_num, packet.packet_type))
            self.check_connection(packet)
        except (OSError, Exception) as e:
            logging.error("Packet Orchestrator Timer was stopped")
            logging.error(str(e))

    def wait_until_received(self, window_size):
        with self.cv:
            while (len(self.packets) >= window_size):
                self.cv.wait()

    def cancel_all_timers(self):
        packets_non_acked = list(self.packets.keys())
        for seq_num in packets_non_acked:
            self.cancel_timer(seq_num)

    def shutdown(self):
        self.cancel_all_timers()
        self.closed = True
        self.cv.notify_all()

    def stop(self):
        with self.cv:
            self.shutdown()

    def __del__(self):
        self.stop()
