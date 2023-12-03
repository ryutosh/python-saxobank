from __future__ import annotations

from decimal import Decimal

# from datetime import datetime
from typing import Any
from typing import Optional as N

from pydantic import conint

from ..base import ODataRequest, ODataResponse, SaxobankModel
from ..common import (
    AssetType,
    InstrumentFieldGroup,
    NonTradableReasons,
    OrderDistanceType,
    OrderDurationType,
    PlaceableOrderType,
    PriceDisplayFormatType,
    TradingStatus,
)


# ****************************************************************
# SubModels
# ****************************************************************
class ExchangeSummaryResponse(SaxobankModel):
    Name: N[str]
    CountryCode: N[str]
    ExchangeId: N[str]
    PriceSourceName: N[str]
    TimeZoneId: N[str]


class OrderDistancesResponse(SaxobankModel):
    EntryDefaultDistance: float
    EntryDefaultDistanceType: OrderDistanceType
    StopLossDefaultDistance: float
    StopLossDefaultDistanceType: OrderDistanceType


class PriceDisplayFormatResponse(SaxobankModel):
    OrderDecimals: conint(ge=0)
    Format: N[PriceDisplayFormatType]
    PriceCurrency: N[str]


class SupportedOrderTypeSettingResponse(SaxobankModel):
    DurationTypes: list[OrderDurationType]
    OrderType: PlaceableOrderType


class TickSizeSchemeElementResponse(SaxobankModel):
    HighPrice: Decimal
    TickSize: Decimal


class TickSizeSchemeResponse(SaxobankModel):
    DefaultTickSize: Decimal
    Elements: list[TickSizeSchemeElementResponse]


# ****************************************************************
# Request Main Models
# ****************************************************************
class InstrumentsDetailsRequest(SaxobankModel, ODataRequest):
    AssetTypes: N[list[AssetType]]
    Uics: N[list[int]]
    FieldGroups: N[list[InstrumentFieldGroup]]

    # class Config:
    #     use_enum_values = True


# ****************************************************************
# Response Main Models
# ****************************************************************
class InstrumentsDetails(SaxobankModel):
    # ErrorInfo
    # ErrorCode: N[str]
    # Message: N[str]
    # ModelState: N[Any]

    # Display, Format and Defaults
    AssetType: N[AssetType]
    Uic: N[int]
    Symbol: N[str]
    Description: N[str]
    Exchange: N[ExchangeSummaryResponse]
    Format: N[PriceDisplayFormatResponse]
    # Important Meta Data
    PriceCurrency: N[str]
    CurrencyCode: N[str]
    # Validation
    IsTradable: N[bool] = True
    TradableAs: N[list[AssetType]]
    TradingStatus: N[TradingStatus] = TradingStatus.Tradable
    NonTradableReason: N[NonTradableReasons]
    ShortTradeDisabled: N[bool] = False
    # OrderConditions
    AmountDecimals: N[conint(ge=0)]
    MinimumLotSize: N[float]
    OrderDistances: N[OrderDistancesResponse]
    SupportedOrderTypes: N[list[PlaceableOrderType]]
    SupportedOrderTypeSettings: N[list[SupportedOrderTypeSettingResponse]]
    # TickSize
    TickSizeScheme: N[TickSizeSchemeResponse]
    TickSize: N[Decimal]
    TickSizeLimitOrder: N[Decimal]
    TickSizeStopOrder: N[Decimal]


class InstrumentsDetailsResponse(SaxobankModel, ODataResponse):
    Data: list[InstrumentsDetails]
