""" Module """
import struct
import sys
from custom_components.badconga.app.const import OPNAMES
from custom_components.badconga.app.entities import Packet
from custom_components.badconga.app.helpers import build_schema, message_to_dict

HEADERS_LEN = 24
IGNORED = [
    'SMSG_CLEAN_RECORDS',
    'SMSG_AREA_LIST_INFO',
    'SMSG_UNKNOWN_MAP'
]

def handle_packet(packet: Packet):
    """ handle_packet """
    opname = OPNAMES[packet.opcode] if packet.opcode in OPNAMES else None
    if opname in IGNORED:
        return 'Body ({})'.format(len(packet.payload))
    schema = build_schema(packet)
    if schema:
        return 'Schema: {}'.format(message_to_dict(schema))
    return 'Body ({}): {}'.format(len(packet.payload), packet.payload.hex())

def stringify(packet: Packet):
    """ stringify """
    opcode = packet.opcode
    return '[{}] [USER: {}] [DEVICE: {}] {}'.format(
        OPNAMES[opcode] if opcode in OPNAMES else hex(opcode),
        packet.user_id,
        packet.device_id,
        handle_packet(packet)
    )

def parse(filename):
    """ parse """
    with open(filename, 'rb') as file:
        data = {}
        headers = file.read(HEADERS_LEN)
        while headers:
            # unpack
            (length, ctype, flow, user_id, device_id, sequence, opcode) = struct.unpack('=ibbiiqh',
                                                                                        headers)
            # check integrity
            if length < HEADERS_LEN:
                raise Exception('malformed packets: length too small', headers)
            # payload
            payload = file.read(length - HEADERS_LEN)
            # store
            data[sequence] = Packet(
                ctype,
                flow,
                user_id,
                device_id,
                sequence,
                opcode,
                payload
            )
            # next
            headers = file.read(HEADERS_LEN)
        # return
        return data

def main():
    """ main """
    flows = {}
    # parse & join
    for argv in sys.argv:
        flow = parse(argv)
        for sequence, packet in flow.items():
            if sequence not in flows:
                flows[sequence] = {}
            flows[sequence][packet.flow] = packet

    # pretty print
    for sequence in sorted(flows):
        packets = flows[sequence]
        hex_seq = struct.pack('q', sequence).hex()
        print('[{}]'.format(hex_seq))
        for flow in sorted(packets):
            packet = packets[flow]
            print('[{}] {}'.format(flow, stringify(packet)))
        print()

main()
