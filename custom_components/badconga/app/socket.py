""" Socket """
import threading
import socket
import logging
import struct
import time
from .evented import Evented

logger = logging.getLogger(__name__)

class Socket(Evented):
    """ Socket """
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.is_connecting = False
        self.is_connected = False
        self.connect_thread = None
        self.recv_thread = None
        self.sock = None

    def __del__(self):
        self.disconnect()

    def start_connect(self):
        """ start_connect """
        self.is_connecting = True
        self.connect_thread = threading.Thread(target=self.connect)
        self.connect_thread.start()

    def connect(self):
        """ connect """
        while self.is_connecting and not self.is_connected:
            logger.debug('connecting to %s:%s...', self.host, self.port)
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(90.0)
                self.sock.connect((self.host, self.port))
            except socket.error as error:
                logger.debug('connect error: %s', error)
                time.sleep(60)
                continue
            self.is_connected = True
            self.is_connecting = False
            self.recv_thread = threading.Thread(target=self.handle)
            self.recv_thread.start()
            self.trigger('connect')

    def disconnect(self):
        """ disconnect """
        if self.connect_thread:
            self.is_connecting = False
            if self.connect_thread != threading.current_thread():
                try:
                    self.connect_thread.join()
                except RuntimeError:
                    pass
                self.connect_thread = None
        if self.is_connected:
            logger.debug('disconnecting...')
            self.is_connected = False
            if self.sock:
                logger.debug('closing socket...')
                try:
                    self.sock.close()
                except socket.error:
                    pass
            if self.recv_thread:
                if self.recv_thread != threading.current_thread():
                    logger.debug('waiting for thread to close...')
                    try:
                        self.recv_thread.join()
                    except RuntimeError:
                        pass
            self.sock = None
            self.recv_thread = None
            self.trigger('disconnect')

    def send(self, data: bytes):
        """ send """
        if self.is_connected:
            try:
                self.sock.send(data)
            except socket.error as error:
                logger.debug('send error: %s', error)
                self.disconnect()

    def handle(self):
        """ handle """
        while self.is_connected:
            try:
                data = self.recv()
                if data:
                    self.trigger('recv', data)
            except socket.error as error:
                logger.debug('recv error: %s', error)
                self.disconnect()

    def recv(self) -> bytes:
        """ recv """
        data = b''
        # packet length
        while 4 - len(data) > 0:
            buf = self.sock.recv(4 - len(data))
            if not buf:
                raise socket.error('connection closed while receiving header')
            data += buf
        (len_response,) = struct.unpack('i', data)
        if len_response < 4:
            logger.error('received wrong packet: length %d too small',
                         len_response)
            return None
        # packet data
        while len_response - len(data) > 0:
            buf = self.sock.recv(len_response - len(data))
            if not buf:
                raise socket.error('connection closed while receiving payload')
            data += buf
        # return
        return data
