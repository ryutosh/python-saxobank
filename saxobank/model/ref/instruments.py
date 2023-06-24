from __future__ import annotations

from decimal import Decimal

# from datetime import datetime
from typing import Any
from typing import Optional as N

from pydantic import conint

from .. import enum as e
from ..common import ODataRequest, ODataResponse, _SaxobankModel


# ****************************************************************
# SubModels
# ****************************************************************
class ExchangeSummaryResponse(_SaxobankModel):
    Name: N[str]
    CountryCode: N[str]
    ExchangeId: N[str]
    PriceSourceName: N[str]
    TimeZoneId: N[str]


class OrderDistancesResponse(_SaxobankModel):
    EntryDefaultDistance: float
    EntryDefaultDistanceType: e.OrderDistanceType
    StopLossDefaultDistance: float
    StopLossDefaultDistanceType: e.OrderDistanceType


class PriceDisplayFormatResponse(_SaxobankModel):
    OrderDecimals: conint(ge=0)
    Format: N[e.PriceDisplayFormatType]
    PriceCurrency: N[str]


class SupportedOrderTypeSettingResponse(_SaxobankModel):
    DurationTypes: list[e.OrderDurationType]
    OrderType: e.PlaceableOrderType


class TickSizeSchemeElementResponse(_SaxobankModel):
    HighPrice: Decimal
    TickSize: Decimal


class TickSizeSchemeResponse(_SaxobankModel):
    DefaultTickSize: Decimal
    Elements: list[TickSizeSchemeElementResponse]


# ****************************************************************
# Request Main Models
# ****************************************************************
class InstrumentsDetailsRequest(_SaxobankModel, ODataRequest):
    AssetTypes: N[list[e.AssetType]]
    Uics: N[list[int]]
    FieldGroups: N[list[e.InstrumentFieldGroup]]

    # class Config:
    #     use_enum_values = True


# ****************************************************************
# Response Main Models
# ****************************************************************
class InstrumentsDetails(_SaxobankModel):
    # ErrorInfo
    # ErrorCode: N[str]
    # Message: N[str]
    # ModelState: N[Any]

    # Display, Format and Defaults
    AssetType: N[e.AssetType]
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
    TradableAs: N[list[e.AssetType]]
    TradingStatus: N[e.TradingStatus] = e.TradingStatus.Tradable
    NonTradableReason: N[e.NonTradableReasons]
    ShortTradeDisabled: N[bool] = False
    # OrderConditions
    AmountDecimals: N[conint(ge=0)]
    MinimumLotSize: N[float]
    OrderDistances: N[OrderDistancesResponse]
    SupportedOrderTypes: N[list[e.PlaceableOrderType]]
    SupportedOrderTypeSettings: N[list[SupportedOrderTypeSettingResponse]]
    # TickSize
    TickSizeScheme: N[TickSizeSchemeResponse]
    TickSize: N[Decimal]
    TickSizeLimitOrder: N[Decimal]
    TickSizeStopOrder: N[Decimal]


class InstrumentsDetailsResponse(_SaxobankModel, ODataResponse):
    Data: list[InstrumentsDetails]
