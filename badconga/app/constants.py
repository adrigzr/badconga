""" constants """
from typing import Union

OPCODES = {
    'SMSG_ERROR': 0x0001,
    'SMSG_DISCONNECT': 0x0002,
    'CMSG_USER_LOGIN': 0x0BB9,
    'SMSG_USER_LOGIN': 0x0BBA,
    'CMSG_SESSION_LOGIN': 0x07D1,
    'SMSG_SESSION_LOGIN': 0x07D2,
    'CMSG_SERVER_CHECK': 0x07D5,
    'SMSG_SERVER_CHECK': 0x07D6,
    'CMSG_DEVICE_LIST': 0x0BCB,
    'SMSG_DEVICE_LIST': 0x0BCC,
    'SMSG_USER_LOGOUT': 0x0C12,
    'CMSG_DEVICE_TIME': 0x1011,
    'SMSG_DEVICE_TIME': 0x1012,
    'CMSG_PING': 0x1079,
    'SMSG_PING': 0x107A,
    'SMSG_DISCONNECT_DEVICE': 0x107C,
    'CMSG_TASK_DATA': 0x10CD,
    'SMSG_TASK_DATA': 0x10CE,
    'CMSG_CONNECT': 0x1009,
    'SMSG_DEVICE_STATUS': 0x10FE,
    'CMSG_LOCATE_DEVICE': 0X10EB,
    'SMSG_LOCATE_DEVICE': 0X10EC,
    'CMSG_CTRL_TYPE': 0x110b,
    'SMSG_CTRL_TYPE': 0x110c,
    'CMSG_SET_CLEAN_MODE': 0x1121,
    'CMSG_MAP_INFO': 0x1162,
    'SMSG_MAP_INFO': 0x1163,
    'SMSG_UPDATE_ROBOT_POSITION': 0x1166,
    'SMSG_UPDATE_CHARGE_POSITION': 0x1168,
    'SMSG_DEVICE_BUSY': 0x1169,
    'SMSG_AREA_LIST_INFO': 0x116A,
    'CMSG_CLEAN_RECORDS': 0x1389,
    'SMSG_CLEAN_RECORDS': 0x138a,
    'CMSG_DEVICE_INFO': 0x1463,
    'SMSG_DEVICE_INFO': 0x1464,
    'CMSG_DEVICE_POWER': 0x1471,
    'SMSG_DEVICE_POWER': 0x1472,
    'CMSG_RETURN_HOME': 0x1069,
    'SMSG_RETURN_HOME': 0x106A,
    'CMSG_CLEAN_MODE': 0x106D,
    'SMSG_CLEAN_MODE': 0x106E,
    'SMSG_MAP_UPDATE': 0x1164,
    'CMSG_SET_FAN_MODE': 0x10D9,
    'SMSG_SET_FAN_MODE': 0x10DA,
    'CMSG_UNK_1': 0x111f,
    'SMSG_UNK_1': 0x1120,
    'SMSG_UNKNOWN_MAP': 0x7473,
}

OPNAMES = {
    value: key for key, value in OPCODES.items()
}

APP_NAME = 'android-3x90-1.1.3'
HOST = 'cecotec.fas.3irobotix.net'
PORT = 4020
CTYPE = 2

FAN_MODE_UNKNOWN = 'unknown'
FAN_MODE_NONE = 'none'
FAN_MODE_ECO = 'eco'
FAN_MODE_NORMAL = 'normal'
FAN_MODE_TURBO = 'turbo'

FanMode = Union[
    FAN_MODE_UNKNOWN,
    FAN_MODE_NONE,
    FAN_MODE_ECO,
    FAN_MODE_NORMAL,
    FAN_MODE_TURBO
]

FAN_MODES = {
    0: FAN_MODE_NONE,
    1: FAN_MODE_ECO,
    2: FAN_MODE_NORMAL,
    3: FAN_MODE_TURBO,
}

REVERSE_FAN_MODES = {
    value: key for key, value in FAN_MODES.items()
}

CLEAN_MODE_UNKNOWN = 'unknown'
CLEAN_MODE_AUTO = 'auto'
CLEAN_MODE_MANUAL = 'manual'
CLEAN_MODE_SPOT = 'spot'
CLEAN_MODE_SPIRAL = 'spiral'
CLEAN_MODE_EDGES = 'edges'
CLEAN_MODE_ZONE = 'zone'
CLEAN_MODE_SCRUB = 'scrub'

CleanMode = Union[
    CLEAN_MODE_UNKNOWN,
    CLEAN_MODE_AUTO,
    CLEAN_MODE_MANUAL,
    CLEAN_MODE_SPOT,
    CLEAN_MODE_SPIRAL,
    CLEAN_MODE_EDGES,
    CLEAN_MODE_ZONE,
    CLEAN_MODE_SCRUB,
]

STATE_CLEANING = 'cleaning'
STATE_DOCKED = 'docked'
STATE_RETURNING = 'returning'
STATE_ERROR = 'error'
STATE_IDLE = 'idle'
STATE_UNKNOWN = 'unknown'

State = Union[
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_RETURNING,
    STATE_ERROR,
    STATE_IDLE,
    STATE_UNKNOWN
]
