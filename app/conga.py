""" conga """
import logging
import threading
from google.protobuf.json_format import MessageToDict
from . import schema_pb2
from .evented import Evented
from .objects import Device
from .builder import Builder
from .socket import Socket
from .constants import HOST, PORT, OPCODES, OPNAMES, MODES, STATES
from .helpers import unpack, build_schema

logger = logging.getLogger(__name__)

class Conga(Evented):
    """ Conga """
    def __init__(self):
        super().__init__()
        self.session_id = None
        self.device = Device()
        self.builder = Builder()
        self.socket = Socket(HOST, PORT)
        self.socket.on('recv', self.recv)
        self.on('set_session', self.on_set_session)
        self.on('login', self.on_login)
        self.on('update', self.on_update)
        self.on('disconnect_device', self.on_disconnect_device)
        self.handlers = {
            'SMSG_USER_LOGIN': self.handle_user_login,
            'SMSG_SESSION_LOGIN': self.handle_session_login,
            'SMSG_DEVICE_STATUS': self.handle_device_status,
            'SMSG_USER_LOGOUT': self.handle_user_logout,
            'SMSG_PING': self.handle_ping,
            'SMSG_DISCONNECT': self.handle_disconnect,
            'SMSG_UPDATE_ROBOT_POSITION': self.handle_update_robot_position,
        }

    def send(self, opname, schema=None):
        """ send """
        opcode = OPCODES[opname]
        data = self.builder.build(opcode, schema)
        self.socket.send(data)
        logger.debug('[%s] %s', opname, MessageToDict(schema) if schema else '')

    def recv(self, data: bytes):
        """ recv """
        packet = unpack(data)
        schema = build_schema(packet)
        opname = OPNAMES[packet.opcode] if packet.opcode in OPNAMES else packet.opcode
        logger.debug('[%s] %s', opname, MessageToDict(schema))
        if opname in self.handlers:
            self.handlers[opname](schema)

    def set_session(self, session_id, user_id, device_id):
        """ set_session """
        self.builder.user_id = user_id
        self.builder.device_id = device_id
        self.session_id = session_id
        self.trigger('set_session')

    def login(self, email, password):
        """ login """
        data = schema_pb2.CMSG_USER_LOGIN()
        data.email = email
        data.password = password
        data.unk1 = 1003
        self.send('CMSG_USER_LOGIN', data)

    def connect_device(self):
        """ connect_device """
        self.send('CMSG_CONNECT')
        self.trigger('connect_device')

    def restore_session(self):
        """ session """
        data = schema_pb2.CMSG_SESSION_LOGIN()
        data.sessionId = self.session_id
        data.isPwd = True
        data.unk1 = 1003
        data.unk2 = 1003
        data.unk3 = 'android-3x90-1.1.3'
        self.send('CMSG_SESSION_LOGIN', data)

    def ping(self):
        """ ping """
        self.send('CMSG_PING')

    def handle_ping(self, _):
        """ handlePing """
        threading.Timer(10.0, self.ping).start()

    def handle_user_login(self, schema):
        """ handle_user_login """
        self.set_session(
            session_id=schema.body.sessionId,
            user_id=schema.body.userId,
            device_id=schema.body.deviceId
        )

    def handle_session_login(self, schema):
        """ handle_session_login """
        if schema.result != 0:
            raise Exception('session expired')
        self.trigger('login')

    def handle_device_status(self, schema):
        """ handle_device_status """
        self.device.battery_level = schema.battery
        self.device.fan_mode = MODES[schema.cleanPreference]
        self.device.state = STATES[schema.workMode]
        self.trigger('update')

    def handle_user_logout(self, schema):
        """ handle_user_logout """
        logger.info('Logout: %s', schema.reason)
        self.trigger('logout')

    def handle_disconnect(self, _):
        """ handleDisconnect """
        logger.info('Disconnected! Reconnecting...')
        self.trigger('disconnect_device')

    def handle_update_robot_position(self, schema):
        """ handleUpdateRobotPosition """
        self.device.position.x = schema.pose.x
        self.device.position.y = schema.pose.y
        self.device.position.phi = schema.pose.phi
        self.trigger('update')

    def on_set_session(self):
        """ on_set_session """
        self.restore_session()

    def on_login(self):
        """ on_login """
        self.connect_device()
        self.ping()

    def on_disconnect_device(self):
        """ on_disconnect_device """
        self.connect_device()

    def on_update(self):
        """ on_update """
        logger.info('State: %s', self.device.__dict__)
        logger.info('Position: %s', self.device.position.__dict__)
