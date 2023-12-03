from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, fields
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Dict, List, Literal, Optional, Set, Tuple, Type, Union

from attrs import define

from saxobank.model import common

from ..base import (
    SaxobankModel,
    SaxobankModel2,
    SaxobankRootModel2,
    _ReqCreateSubscription,
    _ReqRemoveSubscription,
    _RespCreateSubscription,
    ommit_datetime_zero,
)
from ..common import AssetType, ChartRequestMode


# ****************************************************************
# SubModels
# ****************************************************************
class ChartFieldGroupSpec(str, Enum):
    """Specify which sections of the response you would like to get returned.

    URL: https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/getchartdataasync/387cfc61d3292d9237095b9144ac4733

    Attributes:
        ChartInfo (ChartFieldGroupSpec): Add field group ChartInfo to get additional information about the OHLC samples.
        Data (ChartFieldGroupSpec): Add FieldGroup Data to include the OHLC samples. If omitted while other field groups are included then the samples are not included in the response.
        DisplayAndFormat (ChartFieldGroupSpec): Add FieldGroup DisplayAndFormat to include formatting and display information about the instrument.
    """

    ChartInfo = "ChartInfo"
    Data = "Data"
    DisplayAndFormat = "DisplayAndFormat"


# class ChartInfo(SaxobankModel):
@dataclass
class ChartInfo(SaxobankModel2):
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

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.FirstSampleTime and not isinstance(self.FirstSampleTime, datetime):
            self.FirstSampleTime = ommit_datetime_zero(self.FirstSampleTime)

    # def __post_init__(self):
    #     if not isinstance(self.FirstSampleTime, datetime):
    #         self.FirstSampleTime = AssetType(self.AssetType)


# class ChartSample(SaxobankModel):
@dataclass
class ChartSample(SaxobankModel2):
    CloseAsk: float
    CloseBid: float
    Time: Union[datetime, str]

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.Time, datetime):
            self.Time = ommit_datetime_zero(self.Time)

    # def __post_init__(self):
    #     for e in fields(self):
    #         if e.type == "Union[datetime, str]":
    #             value = getattr(self, e.name)
    #             if not isinstance(value, datetime):
    #                 setattr(self, e.name, ommit_datetime_zero(value))


# class Data(SaxobankRootModel):
@dataclass
class Data(SaxobankRootModel2):
    """Represents Data.
    Attributes:
        root (list[charts.ChartSample]): Array holding the individual OHLC samples. For Forex Instruments both Bid and Ask values are returned. For other instruments the values are the last traded values.
    """

    _root: list[ChartSample] | list[dict[str, Any]]


# ****************************************************************
# Request
# ****************************************************************
@dataclass
class ChartSubscriptionRequest(SaxobankModel2):
    """Represents bellow Saxobank OpenAPI requests.
    https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/addsubscriptionasync/dbf87ad4302f2d4289be19be8cb4a3db
    """

    AssetType: Union[AssetType, str]
    Uic: int
    Horizon: int
    Count: Optional[int] = None

    def __post_init__(self):
        super().__post_init__()

        if not isinstance(self.AssetType, AssetType):
            self.AssetType = AssetType(self.AssetType)


@dataclass
class ReqSubscriptionsPost(SaxobankModel2):
    Arguments: Union[ChartSubscriptionRequest, dict[str, Any]]


class ReqSubscriptionDelete(_ReqRemoveSubscription):
    pass


# ****************************************************************
# Response
# ****************************************************************
# class GetResp(SaxobankModel):


@dataclass
class GetResp(SaxobankModel2):
    """Represents conposit model.

    Attributes descriptions are referenced from [OpenAPI Reference]: https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/getchartdataasync/387cfc61d3292d9237095b9144ac4733/.

    Attributes:
        Data (saxobank.model.chart.charts.Data): Array holding the individual OHLC samples. For Forex Instruments both Bid and Ask values are returned. For other instruments the values are the last traded values.



    """

    # Data: list[Union[ChartSample, dict[str, Any]]]
    Data: Data | list[dict[str, Any]]
    DataVersion: int
    ChartInfo: Optional[Union[ChartInfo, Dict[str, Any]]] = None

    # _partitions: Set[int] = set()

    def apply_delta(self, delta: Any) -> Tuple[ChartResponse, bool]:
        if not isinstance(delta, SaxobankModel):
            delta = RespSubscriptionsStreaming.parse_obj(delta)

        if delta.PartitionNumber:
            self._partitions.add(delta.PartitionNumber)

        is_parted = (
            bool(len(self._partitions) == delta.TotalPartition) if delta.TotalPartition else False
        )
        return self.merge(delta.Data), is_parted


# class RespSubscriptionsStreaming(_RespPartedStreaming):
#     Data: ChartResponse


class RespSubscriptionsPost(_RespCreateSubscription):
    Snapshot: ChartResponse
