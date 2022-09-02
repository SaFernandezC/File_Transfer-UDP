from ..common.PacketOrchestrator import PacketOrchestrator
from ..common.packet import PacketType, Packet


class PayloadSender:
    def __init__(self, packet_sender, window_size):
        self.packet_sender = packet_sender
        self.packet_orchestrator = PacketOrchestrator(self)
        self.not_acked = 0
        self.working = True
        self.window_size = window_size

    def check_connection_received(self, packet):
        if (self.packet_orchestrator.working()):
            ack_packet = Packet(
                bytes(0), packet.seq_num, PacketType.ACK_CHECK_CONNECTION)
            self.packet_sender.send(ack_packet)

    def ack_received(self, packet):
        self.packet_orchestrator.ack_received(packet.seq_num)

    def resend(self, packet):
        self.packet_sender.send(packet)

    def send(self, payload):
        self.packet_orchestrator.wait_until_received(self.window_size)
        new_packet = self.packet_orchestrator.new_packet(payload)
        self.packet_sender.send(new_packet)

    def syn_received(self, packet):
        self.packet_sender.send(
            Packet(bytes(0), packet.seq_num, PacketType.SYN_ACK))

    def send_syn(self):
        syn_packet = self.packet_orchestrator.syn_packet()
        self.packet_sender.send(syn_packet)
        self.packet_orchestrator.wait_until_received(1)

    def stop(self, forced):
        if (forced):
            self.packet_orchestrator.stop()
        else:
            self.packet_orchestrator.wait_until_received(1)
