from threading import Lock


class PacketSender:
    def __init__(self, socket, server_addr):
        self.socket = socket
        self.server_addr = server_addr
        self.lock = Lock()

    def send(self, packet):
        bytes_packet = packet.packet_to_bytes()
        with self.lock:
            size_data = len(bytes_packet)
            sended = 0
            while (sended < size_data):
                sended = self.socket.sendto(bytes_packet, self.server_addr)
