from threading import Lock


class PacketSender:
    def __init__(self, sender_orchestrator, addr):
        self.sender_orchestrator = sender_orchestrator
        self.addr = addr
        self.lock = Lock()

    def send(self, packet):
        with self.lock:
            bytes_packet = packet.packet_to_bytes()
            self.sender_orchestrator.push(bytes_packet, self.addr)
