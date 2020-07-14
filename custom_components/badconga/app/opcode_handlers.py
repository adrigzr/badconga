""" opcode_handlers """
# pylint: disable=no-member,line-too-long,too-many-branches
import struct
import zlib
from io import BytesIO
from google.protobuf.json_format import ParseDict
from . import schema_pb2

def handle_update_robot_position(payload):
    """ handle_update_robot_position """
    (map_head_id, pose_id, update, pose_x, pose_y, pose_phi) = struct.unpack('=iibfff', payload)
    robot_position = schema_pb2.RobotPosition()
    robot_position.mapHeadId = map_head_id
    robot_position.update = update
    robot_position.pose.id = pose_id
    robot_position.pose.x = pose_x
    robot_position.pose.y = pose_y
    robot_position.pose.phi = pose_phi
    return robot_position

def handle_update_charge_position(payload):
    """ handle_update_charge_position """
    (pose_id, pose_x, pose_y, pose_phi) = struct.unpack('=ifff', payload)
    robot_pose = schema_pb2.RobotPose()
    robot_pose.id = pose_id
    robot_pose.x = pose_x
    robot_pose.y = pose_y
    robot_pose.phi = pose_phi
    return robot_pose

def dict_to_message(message, values):
    """ dict_to_message """
    keys = message.DESCRIPTOR.fields_by_name.keys()
    return ParseDict(dict(zip(keys, values)), message)

def read_string(data):
    """ read_string """
    (str_len,) = struct.unpack('=b', data.read(1))
    if str_len:
        (string,) = struct.unpack('{}s'.format(str_len), data.read(str_len))
        return string.decode('utf-8')
    return ''

def read_map_info_list(parent, data):
    """ read_map_info_list """
    (clean_map_number,) = struct.unpack('=b', data.read(1))
    for _ in range(0, clean_map_number):
        (map_head_id,) = struct.unpack('i', data.read(4))
        map_name = read_string(data)
        (current_clean_plan_id,) = struct.unpack('i', data.read(4))
        message = parent.add()
        message.CopyFrom(dict_to_message(schema_pb2.MapInfo(), (map_head_id, map_name, current_clean_plan_id)))

def read_clean_room_list(parent, data):
    """ read_clean_room_list """
    (clean_room_number,) = struct.unpack('i', data.read(4))
    for _ in range(0, clean_room_number):
        (room_id,) = struct.unpack('=b', data.read(1))
        room_name = read_string(data)
        (room_state, room_x, room_y) = struct.unpack('=bff', data.read(9))
        message = parent.add()
        message.CopyFrom(dict_to_message(schema_pb2.CleanRoom(), (room_id, room_name, room_state, room_x, room_y)))

def read_area_info_list(parent, data):
    """ read_area_info_list """
    (number,) = struct.unpack('i', data.read(4))
    for _ in range(0, number):
        (area_id, area_type, points) = struct.unpack('3i', data.read(12))
        message = parent.add()
        message.CopyFrom(dict_to_message(schema_pb2.AreaInfo(), (area_id, area_type)))
        if points:
            message.x.extend(struct.unpack('{}f'.format(points), data.read(points * 4)))
            message.y.extend(struct.unpack('{}f'.format(points), data.read(points * 4)))
            data.read(points * 3 * 4) # dump values

def read_clean_room_info_list(parent, data):
    """ read_clean_room_info_list """
    (number,) = struct.unpack('i', data.read(4))
    for _ in range(0, number):
        (info_id, info_type) = struct.unpack('=2b', data.read(2))
        message = parent.add()
        message.CopyFrom(dict_to_message(schema_pb2.CleanRoomInfo(), (info_id, info_type)))

def read_clean_plan_list(parent, data):
    """ read_clean_plan_list """
    (number,) = struct.unpack('=b', data.read(1))
    for _ in range(0, number):
        (plan_id,) = struct.unpack('i', data.read(4))
        plan_name = read_string(data)
        (map_head_id, _) = struct.unpack('2i', data.read(8))
        message = parent.add()
        message.CopyFrom(dict_to_message(schema_pb2.CleanPlan(), (plan_id, plan_name, map_head_id)))
        read_area_info_list(message.areaInfoList, data)
        read_clean_room_info_list(message.cleanRoomInfoList, data)

def handle_map(payload):
    """ handle_map """
    data = BytesIO(zlib.decompress(payload))
    (mask,) = struct.unpack('i', data.read(4))
    map_update = schema_pb2.MapUpdate()
    map_update.mask = mask
    if mask & 0x1:
        map_update.statusInfo.CopyFrom(dict_to_message(schema_pb2.StatusInfo(), struct.unpack('11i', data.read(44))))
    if mask & 0x2:
        map_update.mapHeadInfo.CopyFrom(dict_to_message(schema_pb2.MapHeadInfo(), struct.unpack('5i5f', data.read(40))))
        map_update.mapGrid = data.read(map_update.mapHeadInfo.sizeX * map_update.mapHeadInfo.sizeY)
    if mask & 0x4:
        map_update.historyHeadInfo.CopyFrom(dict_to_message(schema_pb2.HistoryHeadInfo(), struct.unpack('3i', data.read(12))))
        data.read(map_update.historyHeadInfo.pointNumber * 9)
    if mask & 0x8:
        map_update.robotChargeInfo.CopyFrom(dict_to_message(schema_pb2.RobotChargeInfo(), struct.unpack('i3f', data.read(16))))
    if mask & 0x10:
        map_update.wallListInfo.CopyFrom(dict_to_message(schema_pb2.ListInfo(), struct.unpack('3i', data.read(12))))
    if mask & 0x20:
        map_update.areaListInfo.CopyFrom(dict_to_message(schema_pb2.ListInfo(), struct.unpack('3i', data.read(12))))
    if mask & 0x40:
        map_update.spotInfo.CopyFrom(dict_to_message(schema_pb2.SpotInfo(), struct.unpack('2i3f', data.read(5 * 4))))
    if mask & 0x80:
        map_update.robotPoseInfo.CopyFrom(dict_to_message(schema_pb2.RobotPoseInfo(), struct.unpack('=2ib3f', data.read(21))))
    if mask & 0x100:
        raise Exception('handle_map: unhandled mask 0x100')
    if mask & 0x200:
        raise Exception('handle_map: unhandled mask 0x200')
    if mask & 0x400:
        raise Exception('handle_map: unhandled mask 0x400')
    if mask & 0x800:
        map_update.cleanPlanInfo.CopyFrom(dict_to_message(schema_pb2.CleanPlanInfo(), struct.unpack('=ihb', data.read(7))))
    if mask & 0x1000:
        read_map_info_list(map_update.mapInfoList, data)
    if mask & 0x2000:
        read_clean_room_list(map_update.cleanRoomList, data)
        read_clean_plan_list(map_update.cleanPlanList, data)
        total_rooms = len(map_update.cleanRoomList)
        data.read(total_rooms * total_rooms)
        map_update.roomEnableInfo.CopyFrom(dict_to_message(schema_pb2.RoomEnableInfo(), struct.unpack('=ib', data.read(5))))
        if map_update.roomEnableInfo.size:
            raise Exception('handle_map: unhandled room enable info')
    # if mask & 0x4000:
        # raise Exception('handle_map: unhandled mask 0x4000')
    return map_update

OPCODE_HANDLERS = {
    'SMSG_UPDATE_ROBOT_POSITION': handle_update_robot_position,
    'SMSG_UPDATE_CHARGE_POSITION': handle_update_charge_position,
    'SMSG_MAP_UPDATE': handle_map,
    'SMSG_MAP_INFO': handle_map,
}
