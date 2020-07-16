""" builder """
# pylint: disable=too-few-public-methods
import logging
from .const import CTYPE
from .entities import Packet
from .helpers import pack

logger = logging.getLogger(__name__)

class Builder:
    """ Packer """
    def __init__(self):
        self.sequence = 0
        self.user_id = 0
        self.device_id = 0
        self.ctype = CTYPE

    def build(self, opcode: int, schema=None) -> bytes:
        """ pack """
        # pack
        packet = Packet(
            ctype=self.ctype,
            flow=0,
            user_id=self.user_id,
            device_id=self.device_id,
            sequence=self.sequence,
            opcode=opcode,
            payload=schema.SerializeToString() if schema else None
        )
        # increment
        self.sequence += 1
        return pack(packet)
