"""
  Generated by Eclipse Cyclone DDS idlc Python Backend
  Cyclone DDS IDL version: v0.11.0
  Module: unitree_go.msg.dds_
  IDL file: MotorCmd_.idl

"""

from dataclasses import dataclass

import cyclonedds.idl as idl
import cyclonedds.idl.annotations as annotate
import cyclonedds.idl.types as types

# root module import for resolving types
# import unitree_go


@dataclass
@annotate.final
@annotate.autoid("sequential")
class MotorCmd_(idl.IdlStruct, typename="unitree_go.msg.dds_.MotorCmd_"):
    mode: types.uint8
    q: types.float32
    dq: types.float32
    tau: types.float32
    kp: types.float32
    kd: types.float32
    reserve: types.array[types.uint32, 3]
