""" Socket """
import threading
import socket
import logging
import struct
from .evented import Evented

logger = logging.getLogger(__name__)

class Socket(Evented):
    """ Socket """
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()
        self.thread = threading.Thread(target=self.handle)
        self.thread.start()

    def __del__(self):
        self.sock.close()

    def connect(self):
        """ connect """
        logger.debug('connecting to %s:%s...', self.host, self.port)
        self.sock.connect((self.host, self.port))

    def send(self, data: bytes):
        """ send """
        try:
            self.sock.send(data)
        except socket.error as error:
            logger.debug('send error: %s', error)
            self.connect()
            self.send(data)

    def recv(self) -> bytes:
        """ recv """
        data = b''
        # packet length
        while 4 - len(data) > 0:
            data += self.sock.recv(4 - len(data))
        (len_response,) = struct.unpack('i', data)
        if len_response < 4:
            raise Exception('received wrong packet: length too small', len_response)
        # packet data
        while len_response - len(data) > 0:
            data += self.sock.recv(len_response - len(data))
        # return
        return data

    def handle(self):
        """ handle """
        while True:
            try:
                data = self.recv()
                self.trigger('recv', data)
            except socket.error as error:
                logger.debug('recv error: %s', error)
                self.connect()
