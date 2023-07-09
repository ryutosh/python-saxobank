from __future__ import annotations

from datetime import datetime

from .. import common as _c
from .. import enum as _e
from typing import Any, ClassVar, List, Optional, Set, Tuple, Type


# ****************************************************************
# SubModels
# ****************************************************************
class ChartInfo(_c._SaxobankModel):
    """Represents ChartInfo.
    Attributes:
        ExchangeId: Id of the Exchange. Go to the ReferenceData/Exhanges endpoint to get exchange session info.
        Horizon: Horizon in minutes.
        FirstSampleTime: The time of the first (oldest) available sample available for this instrument. Useful for the client when calculating the size of the horizontal slider.
        DelayedByMinutes: If the pricefeed is delayed, this field will be returned indicating the delay in minutes.
    """
    ExchangeId: str
    Horizon: int
    FirstSampleTime: Optional[datetime] = None
    DelayedByMinutes: Optional[int] = None


class ChartSample(_c._SaxobankModel):
    CloseAsk: float
    CloseBid: float
    Time: datetime


# ****************************************************************
# Request
# ****************************************************************
class ChartSubscriptionRequest(_c._SaxobankModel):
    """Represents bellow Saxobank OpenAPI requests.
    https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/addsubscriptionasync/dbf87ad4302f2d4289be19be8cb4a3db
    """
    AssetType: _e.AssetType
    Uic: int
    Horizon: int
    Count: Optional[int] = None


class ReqSubscriptionsPost(_c._ReqCreateSubscription):
    Arguments: ChartSubscriptionRequest


class ReqSubscriptionDelete(_c._ReqRemoveSubscription):
    pass


# ****************************************************************
# Response
# ****************************************************************
class ChartResponse(_c._SaxobankModel):
    DataVersion: int
    ChartInfo: Optional[ChartInfo] = None
    Data: List[ChartSample]

    _partitions: Set[int] = set()

    def apply_delta(self, delta: Any) -> Tuple[ChartResponse, bool]:
        if not isinstance(delta, _c._SaxobankModel):
            delta = RespSubscriptionsStreaming.parse_obj(delta)

        if delta.PartitionNumber:
            self._partitions.add(delta.PartitionNumber)

        is_parted = bool(len(self._partitions) == delta.TotalPartition) if delta.TotalPartition else False
        return self.merge(delta.Data), is_parted


class RespSubscriptionsStreaming(_c._RespPartedStreaming):
    Data: ChartResponse


class RespSubscriptionsPost(_c._RespCreateSubscription):
    Snapshot: ChartResponse
