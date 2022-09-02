from ..common.FileHandler import FileHandler
from ..common.AppProtocol import AppProtocol, Encoder
from ..ProtocolRDT.client.CommunicationSocketClient import (
                                        CommunicationSocketClient)
import logging


class Client:
    def __init__(self, host, port):
        self.peer_skt = CommunicationSocketClient(host, port)
        self.protocol = AppProtocol()
        self.file_handler = FileHandler(self.protocol)

    def upload(self, filename_of_client, filename_in_server):
        try:
            self.peer_skt.connect()
            self.protocol.send_upload_request(self.peer_skt,
                                              filename_in_server)
            self.file_handler.upload_file(self.peer_skt, filename_of_client)
            type_filename, filename = self.protocol.recv_success(self.peer_skt)
            if (type_filename != Encoder.SUCCESS_OPERATION):
                logging.error(f"An invalid type was received: {type_filename}")
            else:
                logging.info(f"Filename uploaded {filename}")
        
            self.peer_skt.close(False)
        except (OSError, Exception, KeyboardInterrupt) as o:
            logging.error(f"An error occurred in client upload.{str(o)}")
            self.peer_skt.close(True)

        

    def download(self, filename_of_server, filename_in_client):
        try:
            self.peer_skt.connect()
            self.protocol.send_download_request(self.peer_skt,
                                                filename_of_server)
            logging.debug("Download request sent.")
            filename_in_client = (self.file_handler
                                  .filename_available(filename_in_client))
            self.file_handler.download_file(self.peer_skt, filename_in_client)

            self.peer_skt.close(False)
        except (KeyboardInterrupt, EOFError):
            logging.info("SERVER exited by SIGNAL.")
            self.file_handler.remove_file(filename_in_client)
            logging.error(f"File {filename_in_client} was removed.")
            self.peer_skt.close(True)
        except (OSError, Exception) as e:
            logging.error(f"An error occurred in client download. {str(e)}")
            self.file_handler.remove_file(filename_in_client)
            logging.debug(f"File {filename_in_client} was removed: {str(e)}")
            self.peer_skt.close(True)

    def __del__(self):
        self.peer_skt.close(False)
