""" objects """
# pylint: disable=invalid-name,too-many-arguments,too-few-public-methods,too-many-instance-attributes
from numbers import Number
from .const import (
    CLEAN_MODE_AUTO,
    CLEAN_MODE_EDGES,
    CLEAN_MODE_SPIRAL,
    CLEAN_MODE_SPOT,
    CLEAN_MODE_UNKNOWN,
    CleanMode,
    FAN_MODE_UNKNOWN,
    FanMode,
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_IDLE,
    STATE_RETURNING,
    STATE_UNKNOWN,
    State,
)

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
        self.x = None
        self.y = None
        self.phi = None

    def isvalid(self):
        """ True if x, y and phi are valid numbers """
        return (isinstance(self.x, Number) and
                isinstance(self.y, Number) and
                isinstance(self.phi, Number))

class Device:
    """ Device """
    def __init__(self):
        self.battery_level = 0
        self.work_mode = None
        self.charge_status = False
        self.clean_time = None
        self.clean_size = None
        self.type = 0
        self.fault_code = None
        self.fan_mode: FanMode = FAN_MODE_UNKNOWN
        self.serial_number = None
        self.utc_registered = None
        self.alias = None
        self.model = None
        self.firmware_version = None
        self.controller_version = None

    @property
    def state(self) -> State:
        """ state """
        if self.type not in [0, 3]:
            return STATE_ERROR
        if self.charge_status:
            return STATE_DOCKED
        if self.work_mode in [5, 10]:
            return STATE_RETURNING
        if self.work_mode in [1, 25, 20]:
            return STATE_CLEANING
        if self.work_mode in [0, 4, 23, 29]:
            return STATE_IDLE
        return STATE_UNKNOWN

    @property
    def clean_mode(self) -> CleanMode:
        """ clean_mode """
        if self.work_mode in [0, 1, 4, 5, 10, 11]:
            return CLEAN_MODE_AUTO
        if self.work_mode in [20, 21, 23]:
            return CLEAN_MODE_SPIRAL
        if self.work_mode in [25, 26, 27, 29]:
            return CLEAN_MODE_EDGES
        if self.work_mode in [7, 9, 14, 22]:
            return CLEAN_MODE_SPOT
        if self.work_mode in [36, 37, 38, 39, 40]:
            return CLEAN_MODE_SPOT
        return CLEAN_MODE_UNKNOWN
