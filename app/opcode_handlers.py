""" opcode_handlers """
# pylint: disable=no-member
import struct
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

OPCODE_HANDLERS = {
    'SMSG_UPDATE_ROBOT_POSITION': handle_update_robot_position,
}
