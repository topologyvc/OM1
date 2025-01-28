"""
  Generated by Eclipse Cyclone DDS idlc Python Backend
  Cyclone DDS IDL version: v0.11.0
  Module: unitree_go.msg.dds_
  IDL file: BmsCmd_.idl

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
class BmsCmd_(idl.IdlStruct, typename="unitree_go.msg.dds_.BmsCmd_"):
    off: types.uint8
    reserve: types.array[types.uint8, 3]
