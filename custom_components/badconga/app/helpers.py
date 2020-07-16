""" helpers """
import time
import struct
from google.protobuf.json_format import MessageToDict
from . import schema_pb2
from .const import OPNAMES
from .opcode_handlers import OPCODE_HANDLERS
from .entities import Packet

def message_to_dict(schema):
    """ message_to_dict """
    result = MessageToDict(schema)
    if 'mapGrid' in result:
        del result['mapGrid']
    return result

def build_schema(packet: Packet):
    """ build_schema """
    opname = OPNAMES[packet.opcode] if packet.opcode in OPNAMES else None
    schema = None
    if opname and hasattr(schema_pb2, opname):
        schema = getattr(schema_pb2, opname)()
        schema.ParseFromString(packet.payload)
    if opname and opname in OPCODE_HANDLERS:
        schema = OPCODE_HANDLERS[opname](packet.payload)
    return schema

def wait_for(callback):
    """ waitFor """
    while not callback:
        time.sleep(1)

def pack(packet: Packet) -> bytes:
    """ pack """
    # headers
    data = struct.pack('b', packet.ctype)
    data += struct.pack('b', packet.flow) # flow
    data += struct.pack('i', packet.user_id)
    data += struct.pack('i', packet.device_id)
    data += struct.pack('q', packet.sequence)
    data += struct.pack('=h', packet.opcode)
    # args
    if packet.payload:
        data += packet.payload
    # append size
    size = len(data) + 4
    data = struct.pack('i', size) + data
    # return
    return data

def unpack(data: bytes) -> Packet:
    """ unpack """
    (_, ctype, flow, user_id, device_id, sequence, opcode) = struct.unpack('=ibbiiqh', data[:24])
    payload = data[24:]
    return Packet(
        ctype,
        flow,
        user_id,
        device_id,
        sequence,
        opcode,
        payload
    )
