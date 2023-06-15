from __future__ import annotations

from typing import List, Literal, Optional

from .common import ContextId, ReferenceId, SaxobankModel
from .enum import HeartbeatReason


class Heartbeats(SaxobankModel):
    OriginatingReferenceId: ReferenceId
    Reason: HeartbeatReason


class ResHeartbeat(SaxobankModel):
    ReferenceId: Literal["_heartbeat"]
    Heartbeats: List[Heartbeats]

    def filter_reasons(self, reasons: List[HeartbeatReason]) -> List[Heartbeats]:
        def check(heartbeats: Heartbeats) -> bool:
            return heartbeats.Reason in reasons

        return list(filter(check, self.Heartbeats))


class ResResetSubscriptions(SaxobankModel):
    ReferenceId: Literal["_resetsubscriptions"]
    TargetReferenceIds: List[ReferenceId]


class ReqConnect(SaxobankModel):
    contextid: ContextId
    messageid: Optional[int]


class ReqAuthorize(SaxobankModel):
    contextid: ContextId
