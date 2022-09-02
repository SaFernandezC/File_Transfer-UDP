from enum import Enum
from ..utils import LEN_TYPE, LEN_LENGTH


class Encoder(Enum):
    CHUNK = 1
    LAST_CHUNK = 2
    DOWNLOAD_REQUEST = 3
    UPLOAD_REQUEST = 4
    ERROR_MSG = 5
    CLOSED_CONNECTION = 6
    SUCCESS_OPERATION = 7


class AppProtocol:
    def send_tlv(self, skt, msg, type):
        payload = type.value.to_bytes(LEN_TYPE, "big")
        payload += len(msg).to_bytes(LEN_LENGTH, "big")
        payload += msg
        skt.send(payload)

    def send_download_request(self, skt, filename):
        self.send_tlv(skt, filename.encode(), Encoder.DOWNLOAD_REQUEST)

    def send_upload_request(self, skt, filename):
        self.send_tlv(skt, filename.encode(), Encoder.UPLOAD_REQUEST)

    def send_chunk(self, skt, chunk):
        self.send_tlv(skt, chunk, Encoder.CHUNK)

    def send_last_chunk(self, skt, chunk):
        self.send_tlv(skt, chunk, Encoder.LAST_CHUNK)

    def send_error(self, skt, error):
        self.send_tlv(skt, error.encode(), Encoder.ERROR_MSG)

    def send_success(self, skt, filename):
        self.send_tlv(skt, filename.encode(), Encoder.SUCCESS_OPERATION)

    def _recv_tlv(self, skt):
        type = int.from_bytes(skt.recv(LEN_TYPE), "big")
        if (type == 0):
            return (Encoder.CLOSED_CONNECTION, bytes(0))
        length = int.from_bytes(skt.recv(LEN_LENGTH), "big")

        if (length > 0):
            return (Encoder(type), skt.recv(length))
        else:
            return (Encoder(type), bytes(0))

    def recv_success(self, skt):
        encoder, msg = self._recv_tlv(skt)
        return (encoder, msg.decode())

    def recv_request(self, skt):
        encoder, msg = self._recv_tlv(skt)
        return (encoder, msg.decode())

    def recv_chunk(self, skt):
        return self._recv_tlv(skt)
