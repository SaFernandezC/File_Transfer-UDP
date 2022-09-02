from threading import Thread
from ..common.AppProtocol import Encoder, AppProtocol
from ..common.FileHandler import FileHandler
import logging


class ClientThread(Thread):
    def __init__(self, socket, dir, filenames_monitor):
        super().__init__()
        self.peer_skt = socket
        self.protocol = AppProtocol()
        self.file_handler = FileHandler()
        self.dir = dir
        self.filenames_monitor = filenames_monitor
        self.working = True

        logging.info("[{}:{}] has connected".format(socket.host, socket.port))

    def run(self):
        try:
            type_encoder, msg = self.protocol.recv_request(self.peer_skt)
            logging.info("[{}:{}] requested {} of '{}'"
                         .format(self.peer_skt.host,
                                 self.peer_skt.port, type_encoder, msg))

            filename = self.dir+"/"+msg

            if type_encoder == Encoder.DOWNLOAD_REQUEST:
                if (not self.filenames_monitor.is_locked(filename)):
                    self.file_handler.upload_file(self.peer_skt, filename)
                else:
                    self.protocol.send_error(f"Filename is in use {filename}.")
            elif type_encoder == Encoder.UPLOAD_REQUEST:
                filename = self.filenames_monitor.lock_file(filename)
                try:
                    self.file_handler.download_file(self.peer_skt, filename)
                    self.protocol.send_success(self.peer_skt, filename)
                except (Exception, KeyboardInterrupt, OSError):
                    self.file_handler.remove_file(filename)
                    logging.error("An error ocurred"
                                  f" while downloading {filename}.")
                self.filenames_monitor.unlock_file(filename)
            else:
                self.protocol.send_error(self.peer_skt,
                                         "The type is invalid. You must "
                                         "choose between download and upload.")
                logging.error("[{}:{}] requested {} of '{}' is invalid"
                              .format(self.peer_skt.host,
                                      self.peer_skt.port, type_encoder, msg))

            self.stop(False)
        except Exception as e:
            logging.error("An error occurred in Client Thread.")
            logging.debug(str(e))
            self.stop()

    def stop(self, forced=True):
        if (self.working):
            self.peer_skt.close(forced)
            self.working = False

    def finished(self):
        return not self.working
