from __future__ import annotations

from typing import Optional

from .common import ContextId, SaxobankModel  # , HeartbeatReason, ReferenceId,

# class StreamingwsHeartbeatSubscriptionRes(SaxobankModel):
#     OriginatingReferenceId: ReferenceId
#     Reason: HeartbeatReason


# class StreamingwsHeartbeatRes(SaxobankModel):
#     ReferenceId: Literal["_heartbeat"]
#     Heartbeats: StreamingwsHeartbeatSubscriptionRes


# class StreamingwsDisconnectRes(SaxobankModel):
#     ReferenceId: Literal["_disconnect"]


# class StreamingwsResetSubscriptionsRes(SaxobankModel):
#     ReferenceId: Literal["_resetsubscriptions"]
#     TargetReferenceIds: List[common.ReferenceId]


class ReqConnect(SaxobankModel):
    contextid: ContextId
    messageid: Optional[int]


class ReqAuthorize(SaxobankModel):
    contextid: ContextId
