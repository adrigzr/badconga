""" conga """
# pylint: disable=too-many-public-methods
import logging
import threading
from . import schema_pb2
from .evented import Evented
from .entities import Device
from .map import Map
from .builder import Builder
from .socket import Socket
from .constants import HOST, PORT, OPCODES, OPNAMES, FAN_MODES, FanMode, REVERSE_FAN_MODES
from .helpers import unpack, build_schema, message_to_dict

logger = logging.getLogger(__name__)

class Conga(Evented):
    """ Conga """
    def __init__(self):
        super().__init__()
        self.session_id = None
        self.device = Device()
        self.builder = Builder()
        self.map = Map()
        self.socket = Socket(HOST, PORT)
        self.socket.on('connect', self.on_connect)
        self.socket.on('recv', self.on_recv)
        self.socket.on('disconnect', self.on_disconnect)
        self.on('set_session', self.on_set_session)
        self.on('login', self.on_login)
        self.on('update', self.on_update)
        self.on('disconnect_device', self.on_disconnect_device)
        self.handlers = {
            'SMSG_USER_LOGIN': self.handle_user_login,
            'SMSG_SESSION_LOGIN': self.handle_session_login,
            'SMSG_DEVICE_STATUS': self.handle_device_status,
            'SMSG_USER_KICK': self.handle_user_logout,
            'SMSG_PING': self.handle_ping,
            'SMSG_DISCONNECT_DEVICE': self.handle_disconnect_device,
            'SMSG_UPDATE_ROBOT_POSITION': self.handle_update_robot_position,
            'SMSG_MAP_INFO': self.handle_map_update,
            'SMSG_MAP_UPDATE': self.handle_map_update,
            'SMSG_DISCONNECT': self.handle_disconnect,
        }

    # private

    def send(self, opname, schema=None):
        """ send """
        opcode = OPCODES[opname]
        data = self.builder.build(opcode, schema)
        self.socket.send(data)
        logger.debug('[%s] %s', opname, message_to_dict(schema) if schema else '')

    def on_connect(self):
        """ on_connect """
        if self.session_id:
            self.restore_session()

    def on_recv(self, data: bytes):
        """ on_recv """
        packet = unpack(data)
        schema = build_schema(packet)
        opname = OPNAMES[packet.opcode] if packet.opcode in OPNAMES else packet.opcode
        logger.debug('[%s] %s', opname, message_to_dict(schema) if schema else packet.payload.hex())
        if opname in self.handlers:
            self.handlers[opname](schema)

    def on_disconnect(self):
        """ on_disconnect """
        self.device = Device()

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

    # handlers

    def handle_ping(self, _):
        """ handlePing """
        threading.Timer(10.0, self.ping).start()

    def handle_user_login(self, schema):
        """ handle_user_login """
        if schema.result != 0:
            raise Exception('user login error ({})'.format(hex(schema.result)))
        if schema.body.deviceId == 0:
            raise Exception('device not configured on this account')
        self.set_session(
            session_id=schema.body.sessionId,
            user_id=schema.body.userId,
            device_id=schema.body.deviceId
        )
        self.restore_session()

    def handle_session_login(self, schema):
        """ handle_session_login """
        if schema.result != 0:
            raise Exception('session login error ({})'.format(hex(schema.result)))
        self.trigger('login')

    def handle_device_status(self, schema):
        """ handle_device_status """
        self.device.battery_level = schema.battery
        self.device.work_mode = schema.workMode
        self.device.charge_status = schema.chargeStatus
        self.device.clean_time = schema.cleanTime
        self.device.clean_size = schema.cleanSize
        self.device.type = schema.type
        self.device.fault_code = schema.faultCode
        self.device.fan_mode = FAN_MODES[schema.cleanPreference]
        self.trigger('update_device')

    def handle_user_logout(self, schema):
        """ handle_user_logout """
        logger.info('Logout: %s', schema.reason)
        self.trigger('logout')

    def handle_disconnect_device(self, _):
        """ handleDisconnect """
        logger.info('Disconnected! Reconnecting...')
        self.trigger('disconnect_device')

    def handle_update_robot_position(self, schema):
        """ handleUpdateRobotPosition """
        self.map.robot.x = schema.pose.x
        self.map.robot.y = schema.pose.y
        self.map.robot.phi = schema.pose.phi
        self.trigger('update_position')

    def handle_map_update(self, schema):
        """ handle_map_update """
        self.map.grid = schema.mapGrid
        self.map.size_x = schema.mapHeadInfo.sizeX
        self.map.size_y = schema.mapHeadInfo.sizeY
        self.map.min_x = schema.mapHeadInfo.minX
        self.map.min_y = schema.mapHeadInfo.minY
        self.map.max_x = schema.mapHeadInfo.maxX
        self.map.max_y = schema.mapHeadInfo.maxY
        self.map.charger.x = schema.robotChargeInfo.poseX
        self.map.charger.y = schema.robotChargeInfo.poseY
        self.map.charger.phi = schema.robotChargeInfo.posePhi
        self.map.robot.x = schema.robotPoseInfo.poseX
        self.map.robot.y = schema.robotPoseInfo.poseY
        self.map.robot.phi = schema.robotPoseInfo.posePhi
        self.trigger('update_map')

    def handle_disconnect(self, _):
        """ handle_disconnect """
        self.socket.disconnect()

    # events

    def on_set_session(self):
        """ on_set_session """
        self.socket.connect()

    def on_login(self):
        """ on_login """
        self.connect_device()
        self.get_map_info()
        self.ping()

    def on_disconnect_device(self):
        """ on_disconnect_device """
        self.connect_device()

    def on_update(self):
        """ on_update """
        logger.info('State: state=%s, fan_mode=%s, clean_mode=%s, battery_level=%i',
                    self.device.state, self.device.fan_mode, self.device.clean_mode,
                    self.device.battery_level)

    # methods

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

    def locate(self):
        """ locate """
        self.send('CMSG_LOCATE_DEVICE')

    def get_map_info(self):
        """ get_map_info """
        data = schema_pb2.CMSG_MAP_INFO()
        data.mask = 0x78FF
        self.send('CMSG_MAP_INFO', data)


    def turn_on(self):
        """ turn_on """
        data = schema_pb2.CMSG_CLEAN_MODE()
        data.mode = 1
        data.unk2 = 2
        self.send('CMSG_CLEAN_MODE', data)

    def turn_off(self):
        """ turn_off """
        data = schema_pb2.CMSG_CLEAN_MODE()
        data.mode = 2
        data.unk2 = 2
        self.send('CMSG_CLEAN_MODE', data)

    def return_home(self):
        """ return_home """
        data = schema_pb2.CMSG_RETURN_HOME()
        data.unk1 = 1
        self.send('CMSG_RETURN_HOME', data)

    def set_fan_mode(self, mode: FanMode):
        """ set_clean_mode """
        data = schema_pb2.CMSG_SET_FAN_MODE()
        data.mode = REVERSE_FAN_MODES[mode]
        self.send('CMSG_SET_FAN_MODE', data)
