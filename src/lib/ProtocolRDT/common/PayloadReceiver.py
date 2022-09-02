from telnetlib import KERMIT
from ..common.packet import PacketType, Packet
from threading import Lock, Condition, Timer
import logging
from ..utils import MAX_TRIES, TIMEOUT_LIMIT
from .Buffer import OrderedBuffer


class PayloadReceiver:
    def __init__(self, packet_sender):
        self.packet_sender = packet_sender
        self.uncompleted_message = bytes(0)
        self.last_delivered = 0
        self.finished = False
        self.cv = Condition(Lock())
        self.buffer = OrderedBuffer()

        self.timer = self.create_timer()
        self.tries = 0

    def create_timer(self):
        return Timer(TIMEOUT_LIMIT, self.check_alive, [], {})

    def reset_timer(self):
        self.timer = self.create_timer()
        if (not self.finished):
            self.timer.start()

    def timer_is_alive(self):
        return (self.tries > 0 or self.timer.is_alive())

    def tries_exceded(self):
        if (self.tries > MAX_TRIES):
            with self.cv:
                self.finished = True
                self.cv.notify_all()
            return True
        else:
            return False

    def check_alive(self):
        try:
            if(not self.tries_exceded()):
                packet = Packet(bytes(0), 0, PacketType.CHECK_CONNECTION)
                self.packet_sender.send(packet)
                self.tries += 1
                self.reset_timer()
        except (Exception, KeyboardInterrupt, OSError):
            self.stop()

    def send_ack_packet(self, seq_num):
        ack_packet = Packet(bytes(0), seq_num, PacketType.ACK)
        self.packet_sender.send(ack_packet)
        logging.debug(f"Packet received with sequence number {seq_num}")

    def add_payload(self, seq_num, payload):
        if (self.last_delivered >= seq_num):
            return
        if (self.buffer.push((seq_num, payload), self.last_delivered+1)):
            self.send_ack_packet(seq_num)

    def check_finished(self):
        if (self.finished):
            raise Exception("Receiver is closed.")

    def wait_until_received(self):
        with self.cv:
            next_expected = self.last_delivered + 1
            while ((self.buffer.first_element() != next_expected) and (
                                                not self.finished)):
                if (not self.timer_is_alive()):
                    self.timer.start()
                self.cv.wait()

            self.check_finished()

    def obtain_payload(self):
        self.wait_until_received()
        seq_num, payload = self.buffer.get_first()
        self.last_delivered = seq_num
        return payload

    def notify_packet(self):
        with self.cv:
            if (self.timer.is_alive()):
                self.timer.cancel()
            self.tries = 0
            self.timer = self.create_timer()
            self.cv.notify_all()

    def push(self, packet):
        if (self.last_delivered >= packet.seq_num):
            self.send_ack_packet(packet.seq_num)
        else:
            self.add_payload(packet.seq_num, packet.data)

        self.notify_packet()

    def recv_if_uncompleted(self, size):
        if (len(self.uncompleted_message) <= 0):
            return bytes(0)

        if (len(self.uncompleted_message) > size):
            msg = self.uncompleted_message[0:size]
            self.uncompleted_message = self.uncompleted_message[size:]
        else:
            msg = self.uncompleted_message
            self.uncompleted_message = bytes(0)

        return msg

    def recv_from_socket(self, size):
        size_read = 0
        msg = bytes(0)

        while (size_read < size):
            payload = self.obtain_payload()
            if (not payload):
                raise Exception("Packet is none, payload receiver closed.")
            if (len(payload) > size - size_read):
                msg += payload[0:size - size_read]
                self.uncompleted_message = payload[size - size_read:]
                size_read += len(payload)
            else:
                msg += payload
                size_read += len(payload)

        return msg

    def recv(self, size):
        msg = self.recv_if_uncompleted(size)
        if (len(msg) >= size):
            return msg

        size_read = len(msg) if msg else 0
        msg_socket = self.recv_from_socket(size - size_read)

        return msg + msg_socket

    def stop(self):
        with self.cv:
            if (self.timer.is_alive()):
                self.timer.cancel()
            self.finished = True
            self.cv.notify_all()
