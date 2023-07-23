from __future__ import annotations

from collections.abc import Container
from typing import List, Literal, Optional, Sequence, Set

from .base import SaxobankModel, SaxobankRootModel
from .common import ContextId, HeartbeatReason, ReferenceId

# from dataclasses import dataclass

# @dataclass
# class Heartbeats():
class Heartbeats(SaxobankModel):
    OriginatingReferenceId: ReferenceId
    Reason: HeartbeatReason

class ListHeartbeats(SaxobankRootModel):
    root: List[Heartbeats]


class BaseData:
    pass

class SubData(BaseData):
    pass

class Base:
    cls_data: BaseData
    list_data: Sequence[BaseData]

class Sub(Base):
    cls_data: SubData
    list_data: List[SubData]


class ResHeartbeat(SaxobankModel):
    ReferenceId: Literal["_heartbeat"]
    Heartbeats: List[Heartbeats]

    def filter_reasons(self, reasons: Container[HeartbeatReason]) -> Set[Heartbeats]:
        return {h.OriginatingReferenceId for h in self.Heartbeats if h.Reason in reasons}


class ResResetSubscriptions(SaxobankModel):
    ReferenceId: Literal["_resetsubscriptions"]
    TargetReferenceIds: List[ReferenceId]


class ReqConnect(SaxobankModel):
    contextid: ContextId
    messageid: Optional[int]


class ReqAuthorize(SaxobankModel):
    contextid: ContextId
