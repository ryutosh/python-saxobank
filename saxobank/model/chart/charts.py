from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar, List, Optional, Set, Tuple, Type

from ..base import SaxobankModel, SaxobankRootModel
from ..common import AssetType, ChartRequestMode


# ****************************************************************
# SubModels
# ****************************************************************
class ChartInfo(SaxobankModel):
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


class ChartSample(SaxobankModel):
    CloseAsk: float
    CloseBid: float
    Time: datetime


class Data(SaxobankRootModel):
    root: List[ChartSample]


# ****************************************************************
# Request
# ****************************************************************
class GetReq(SaxobankModel):
    AssetType: AssetType
    Uic: int
    Horizon: int
    Mode: ChartRequestMode
    Count: Optional[int]

    def __init__(self, asset_type: AssetType, uic: int, horizon: int, mode: ChartRequestMode, count: Optional[int] = None):
        self.AssetType = asset_type
        self.Uic = uic
        self.Horizon = horizon
        self.Mode = mode
        self.Count = count



class ChartSubscriptionRequest(SaxobankModel):
    """Represents bellow Saxobank OpenAPI requests.
    https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/addsubscriptionasync/dbf87ad4302f2d4289be19be8cb4a3db
    """
    AssetType: AssetType
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
class GetResp(SaxobankModel):
    """Represents conposit model.

    Attributes descriptions are referenced from [OpenAPI Reference]: https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/getchartdataasync/387cfc61d3292d9237095b9144ac4733/.

    Attributes:
        Data: Array holding the individual OHLC samples. For Forex Instruments both Bid and Ask values are returned. For other instruments the values are the last traded values.



    """

    ChartInfo: Optional[ChartInfo] = None
    Data: Data
    DataVersion: int

    _partitions: Set[int] = set()

    def apply_delta(self, delta: Any) -> Tuple[ChartResponse, bool]:
        """Example function with types documented in the docstring.

        `PEP 484`_ type annotations are supported. If attribute, parameter, and
        return types are annotated according to `PEP 484`_, they do not need to be
        included in the docstring:

        Args:
            param1 (int): The first parameter.
            param2 (str): The second parameter.

        Returns:
            bool: The return value. True for success, False otherwise.

        .. _PEP 484:
            https://www.python.org/dev/peps/pep-0484/

        """
        if not isinstance(delta, SaxobankModel):
            delta = RespSubscriptionsStreaming.parse_obj(delta)

        if delta.PartitionNumber:
            self._partitions.add(delta.PartitionNumber)

        is_parted = bool(len(self._partitions) == delta.TotalPartition) if delta.TotalPartition else False
        return self.merge(delta.Data), is_parted


class RespSubscriptionsStreaming(_c._RespPartedStreaming):
    Data: ChartResponse


class RespSubscriptionsPost(_c._RespCreateSubscription):
    Snapshot: ChartResponse
