""" objects """
# pylint: disable=invalid-name,too-many-arguments,too-few-public-methods
from .constants import State, FanMode, CleanMode, STATE_DOCKED, FAN_MODE_NONE, CLEAN_MODE_AUTO

class Packet:
    """ Packet """
    def __init__(self, ctype: int, flow: int, user_id: int, device_id: int,
                 sequence: int, opcode: int, payload: bytes):
        self.ctype = ctype
        self.flow = flow
        self.user_id = user_id
        self.device_id = device_id
        self.sequence = sequence
        self.opcode = opcode
        self.payload = payload

class Position:
    """ Position """
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.phi = 0.0

class Device:
    """ Device """
    def __init__(self):
        self.battery_level = 0
        self.state: State = STATE_DOCKED
        self.fan_mode: FanMode = FAN_MODE_NONE
        self.clean_mode: CleanMode = CLEAN_MODE_AUTO
        self.position = Position()
