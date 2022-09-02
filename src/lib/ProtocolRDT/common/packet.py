from enum import Enum
from ..utils import LEN_LENGTH, TYPE_LENGTH, SEQNUM_LENGTH, MAX_PACKET_SIZE
from ..utils import TYPE_POS, SEQNUM_POS, LEN_POS, DATA_POS


class PacketType(Enum):
    ACK = 0
    SEND_DATA = 1
    SYN = 2
    SYN_ACK = 3
    CHECK_CONNECTION = 4
    ACK_CHECK_CONNECTION = 5


class Packet:
    def __init__(self, data, seq_num, pkt_type=PacketType.SEND_DATA):
        self.data = data
        self.len = len(data)

        if (self.len > MAX_PACKET_SIZE):
            raise Exception("Maximo permitido del paquete superado.")

        self.packet_type = pkt_type
        self.seq_num = seq_num

    @classmethod
    def packet_from_bytes(self, bytes_packet):
        if (not bytes_packet):
            return None

        byte_array = bytearray(bytes_packet)

        pkt_len = int.from_bytes(byte_array[LEN_POS: LEN_LENGTH], "big")
        pkt_type = PacketType(int.from_bytes(
                    byte_array[TYPE_POS: (TYPE_POS + TYPE_LENGTH)], "big"))
        pkt_seq_num = int.from_bytes(byte_array[SEQNUM_POS: (
                                    SEQNUM_POS + SEQNUM_LENGTH)], "big")
        bytes_data = byte_array[DATA_POS:]

        if (pkt_len != len(bytes_data)):
            return None

        return Packet(bytes_data, pkt_seq_num, pkt_type)

    def is_ack(self):
        return self.packet_type == PacketType.ACK

    def is_syn(self):
        return self.packet_type == PacketType.SYN

    def is_syn_ack(self):
        return self.packet_type == PacketType.SYN_ACK

    def is_check_connection(self):
        return self.packet_type == PacketType.CHECK_CONNECTION

    def is_ack_check_connection(self):
        return self.packet_type == PacketType.ACK_CHECK_CONNECTION

    def packet_to_bytes(self):
        len_bytes = self.len.to_bytes(LEN_LENGTH, "big")
        type_bytes = self.packet_type.value.to_bytes(TYPE_LENGTH, "big")
        data_bytes = self.data
        seq_num_bytes = self.seq_num.to_bytes(SEQNUM_LENGTH, "big")

        return len_bytes + type_bytes + seq_num_bytes + data_bytes
