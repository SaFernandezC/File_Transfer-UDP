from threading import Lock


class SenderOrchestrator:
    def __init__(self, listener_socket):
        self.listener_socket = listener_socket
        self.lock = Lock()

    def push(self, data, addr):
        with self.lock:
            size_data = len(data)
            sended = 0
            while (sended < size_data):
                sended = self.listener_socket.sendto(data, addr)
