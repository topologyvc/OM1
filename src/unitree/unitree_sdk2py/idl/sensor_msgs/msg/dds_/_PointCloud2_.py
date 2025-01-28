"""
  Generated by Eclipse Cyclone DDS idlc Python Backend
  Cyclone DDS IDL version: v0.11.0
  Module: sensor_msgs.msg.dds_
  IDL file: PointCloud2_.idl

"""

from dataclasses import dataclass

import cyclonedds.idl as idl
import cyclonedds.idl.annotations as annotate
import cyclonedds.idl.types as types

# root module import for resolving types
# import sensor_msgs

# if TYPE_CHECKING:
#     import std_msgs.msg.dds_


@dataclass
@annotate.final
@annotate.autoid("sequential")
class PointCloud2_(idl.IdlStruct, typename="sensor_msgs.msg.dds_.PointCloud2_"):
    header: "unitree_sdk2py.idl.std_msgs.msg.dds_.Header_"
    height: types.uint32
    width: types.uint32
    fields: types.sequence["unitree_sdk2py.idl.sensor_msgs.msg.dds_.PointField_"]
    is_bigendian: bool
    point_step: types.uint32
    row_step: types.uint32
    data: types.sequence[types.uint8]
    is_dense: bool
