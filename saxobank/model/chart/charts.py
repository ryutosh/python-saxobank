from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, List, Optional, Set, Tuple, Type

from saxobank.model import common

from ..base import (
    SaxobankModel,
    SaxobankRootModel,
    _ReqCreateSubscription,
    _ReqRemoveSubscription,
    _RespCreateSubscription,
)
from ..common import AssetType, ChartRequestMode


# ****************************************************************
# SubModels
# ****************************************************************
# class ChartInfo(SaxobankModel):
@dataclass
class ChartInfo:
    """Represents ChartInfo.
    Attributes:
        ExchangeId (str): Id of the Exchange. Go to the ReferenceData/Exhanges endpoint to get exchange session info.
        Horizon (int): Horizon in minutes.
        FirstSampleTime (datetime)): The time of the first (oldest) available sample available for this instrument. Useful for the client when calculating the size of the horizontal slider.
        DelayedByMinutes (int): If the pricefeed is delayed, this field will be returned indicating the delay in minutes.
    """

    ExchangeId: str
    Horizon: int
    FirstSampleTime: Optional[datetime] = None
    DelayedByMinutes: Optional[int] = None


# class ChartSample(SaxobankModel):
@dataclass
class ChartSample:
    CloseAsk: float
    CloseBid: float
    Time: datetime


# class Data(SaxobankRootModel):
@dataclass
class Data:
    """Represents Data.
    Attributes:
        root (list[charts.ChartSample]): Array holding the individual OHLC samples. For Forex Instruments both Bid and Ask values are returned. For other instruments the values are the last traded values.
    """

    _root: List[ChartSample]


# ****************************************************************
# Request
# ****************************************************************
# class GetReq(SaxobankModel):
from pydantic.dataclasses import dataclass as pyd


class SamplePydanticModel(SaxobankModel):
    """Class short description.

    Class Description

    Attributes:
        Horizon (int): horizon in minutes.
        Mode (saxobank.model.common.ChartRequestMode): mode
        Count (int): num of returns

    """

    Horizon: int
    Mode: common.ChartRequestMode
    Count: Optional[int] = None


from attrs import define


@define
class SampleAttrs:
    """Class short description.

    Class Description

    Attributes:
        Horizon (int): horizon in minutes.
        Mode (saxobank.model.common.ChartRequestMode): mode
        Count (int): num of returns

    """

    Horizon: int
    Mode: common.ChartRequestMode
    Count: Optional[int] = None


@pyd
class SamplePydanticDataclass:
    """Class short description.

    Class Description

    Attributes:
        Horizon (int): horizon in minutes.
        Mode (saxobank.model.common.ChartRequestMode): mode
        Count (int): num of returns

    """

    Horizon: int
    Mode: common.ChartRequestMode
    Count: Optional[int] = None


@dataclass
class SampleStandardDataclass:
    """Class short description.

    Class Description

    Attributes:
        Horizon (int): horizon in minutes.
        Mode (saxobank.model.common.ChartRequestMode): mode
        Count (int): num of returns

    """

    Horizon: int
    Mode: common.ChartRequestMode
    Count: Optional[int] = None


@dataclass
class GetReq:
    """Represents service charts request.

    Attributes descriptions are referenced from [OpenAPI Reference]: https://.

    Attributes:
        AssetType (AssetType): asset.
        Uic (int): uic.
        Mode (saxobank.model.common.ChartRequestMode): mode

    """

    AssetType: AssetType
    Uic: int
    Horizon: int
    Mode: common.ChartRequestMode
    Count: Optional[int] = None

    def __post_init__(self):
        if not isinstance(self.AssetType, AssetType):
            if isinstance(self.AssetType, str):
                self.AssetType = AssetType(self.AssetType)
            else:
                raise ValueError("Invalid AssetType")
        if not isinstance(self.Mode, ChartRequestMode):
            raise ValueError("Invalid ChartRequestMode")

    # def __init__(
    #     self,
    #     asset_type: AssetType,
    #     uic: int,
    #     horizon: int,
    #     mode: common.ChartRequestMode,
    #     count: Optional[int] = None,
    # ):
    #     self.AssetType = asset_type
    #     self.Uic = uic
    #     self.Horizon = horizon
    #     self.Mode = mode
    #     self.Count = count


class ChartSubscriptionRequest(SaxobankModel):
    """Represents bellow Saxobank OpenAPI requests.
    https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/addsubscriptionasync/dbf87ad4302f2d4289be19be8cb4a3db
    """

    AssetType: AssetType
    Uic: int
    Horizon: int
    Count: Optional[int] = None


class ReqSubscriptionsPost(_ReqCreateSubscription):
    Arguments: ChartSubscriptionRequest


class ReqSubscriptionDelete(_ReqRemoveSubscription):
    pass


# ****************************************************************
# Response
# ****************************************************************
# class GetResp(SaxobankModel):


@dataclass
class GetResp:
    """Represents conposit model.

    Attributes descriptions are referenced from [OpenAPI Reference]: https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/getchartdataasync/387cfc61d3292d9237095b9144ac4733/.

    Attributes:
        Data (saxobank.model.chart.charts.Data): Array holding the individual OHLC samples. For Forex Instruments both Bid and Ask values are returned. For other instruments the values are the last traded values.



    """

    # Data: Data
    DataVersion: int
    ChartInfo: Optional[ChartInfo] = None

    # _partitions: Set[int] = set()

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

        is_parted = (
            bool(len(self._partitions) == delta.TotalPartition)
            if delta.TotalPartition
            else False
        )
        return self.merge(delta.Data), is_parted


# class RespSubscriptionsStreaming(_RespPartedStreaming):
#     Data: ChartResponse


class RespSubscriptionsPost(_RespCreateSubscription):
    Snapshot: ChartResponse
