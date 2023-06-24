from __future__ import annotations

from collections.abc import Container
from typing import List, Literal, Optional, Set

from .common import ContextId, ReferenceId, _SaxobankModel
from .enum import HeartbeatReason


class Heartbeats(_SaxobankModel):
    OriginatingReferenceId: ReferenceId
    Reason: HeartbeatReason


class ResHeartbeat(_SaxobankModel):
    ReferenceId: Literal["_heartbeat"]
    Heartbeats: List[Heartbeats]

    def filter_reasons(self, reasons: Container[HeartbeatReason]) -> Set[Heartbeats]:
        return {h.OriginatingReferenceId for h in self.Heartbeats if h.Reason in reasons}


class ResResetSubscriptions(_SaxobankModel):
    ReferenceId: Literal["_resetsubscriptions"]
    TargetReferenceIds: List[ReferenceId]


class ReqConnect(_SaxobankModel):
    contextid: ContextId
    messageid: Optional[int]


class ReqAuthorize(_SaxobankModel):
    contextid: ContextId
