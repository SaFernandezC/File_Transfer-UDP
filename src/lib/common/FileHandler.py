import os
from .AppProtocol import AppProtocol, Encoder
from functools import partial
import logging
from ..utils import CHUNK_SIZE


class FileHandler:
    def __init__(self, protocol=None):
        self.protocol = protocol if protocol else AppProtocol()

    def filename_available(self, filename):
        path, extension = os.path.splitext(filename)
        i = 1
        while os.path.exists(filename):
            filename = path+"("+str(i)+")"+extension
            i += 1
        return filename

    def download_file(self, skt, filename):
        f = open(filename, "wb")
        type, chunk = self.protocol.recv_chunk(skt)
        while (type != Encoder.LAST_CHUNK):
            if (type != Encoder.CHUNK):
                if (type == Encoder.CLOSED_CONNECTION):
                    logging.error("The connection was closed.")
                f.close()
                self.remove_file(filename)
                return
            f.write(chunk)
            type, chunk = self.protocol.recv_chunk(skt)
        if (len(chunk) > 0):
            f.write(chunk)

        f.close()
        logging.info("File '{}' has been downloaded".format(filename))

    def upload_file(self, skt, filename):
        f = open(filename, "rb")
        f.seek(0, os.SEEK_END)
        end = f.tell()
        f.seek(0)
        for chunk in iter(partial(f.read, CHUNK_SIZE), b''):
            if (f.tell() == end):
                self.protocol.send_last_chunk(skt, chunk)
            else:
                self.protocol.send_chunk(skt, chunk)
        logging.info("File '{}' has been sent to {}:{}"
                     .format(filename, skt.host, skt.port))

    def remove_file(self, filename):
        if os.path.exists(filename):
            os.remove(filename)
