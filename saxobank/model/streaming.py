from __future__ import annotations

from collections.abc import Container
from dataclasses import dataclass
from functools import partial, partialmethod
from typing import List, Literal, Optional, Sequence, Set, TypeVar, Union, cast

# from dataclasses import dataclass
from attrs import define, field, validators

from .base import SaxobankModel, SaxobankRootModel
from .common import ContextId, HeartbeatReason, ReferenceId

# @dataclass
# class Heartbeats():

_T1 = TypeVar("Enum")


def str2reference_id(x: Union[str, ReferenceId]) -> ReferenceId:
    return ReferenceId(x)


# def str2heartbeat_reason(x: Union[str, HeartbeatReason]) -> HeartbeatReason:
#     return HeartbeatReason(x)


def str2enum(cls, x: Union[str, _T1]) -> _T1:
    return cls(x)


str2heartbeat_reason = partial(str2enum, HeartbeatReason)


@dataclass
class Heartbeats:
    OriginatingReferenceId: ReferenceId
    Reason: HeartbeatReason

    # OriginatingReferenceId: ReferenceId = field(
    #     init=True,
    #     converter=str2reference_id,
    #     validator=validators.instance_of(ReferenceId),
    # )
    # Reason: HeartbeatReason = field(
    #     converter=partial(str2enum, HeartbeatReason),
    #     init=True,
    #     validator=validators.instance_of(HeartbeatReason),
    # )


class ListHeartbeats:
    root: List[Heartbeats]


@dataclass
class Parent:
    Msg: str
    Heartbeats: Heartbeats


@dataclass
class ResHeartbeat:
    ReferenceId: Literal["_heartbeat"]
    Heartbeats: List[Heartbeats]

    # def filter_reasons(self, reasons: Container[HeartbeatReason]) -> Set[Heartbeats]:
    #     return {
    #         h.OriginatingReferenceId for h in self.Heartbeats if h.Reason in reasons
    #     }


class ResResetSubscriptions(SaxobankModel):
    ReferenceId: Literal["_resetsubscriptions"]
    TargetReferenceIds: List[ReferenceId]


class ReqConnect(SaxobankModel):
    contextid: ContextId
    messageid: Optional[int]


class ReqAuthorize(SaxobankModel):
    contextid: ContextId
