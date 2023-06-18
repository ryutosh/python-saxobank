from __future__ import annotations

from collections.abc import Container
from typing import List, Literal, Optional, Set

from .common import ContextId, ReferenceId, SaxobankModel
from .enum import HeartbeatReason


class Heartbeats(SaxobankModel):
    OriginatingReferenceId: ReferenceId
    Reason: HeartbeatReason


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
