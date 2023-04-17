from __future__ import annotations

from decimal import Decimal
from typing import Any
from typing import Optional as N

from pydantic import ValidationError, validator

from . import enums as e
from . import port
from .common import AccountKey, OrderDuration, SaxobankModel

# ****************************************************************
# SubModels
# ****************************************************************


class CommissionsResponse(SaxobankModel):
    CostBuy: Decimal
    CostSell: Decimal


class DisplayAndFormatResponse(SaxobankModel):
    Currency: str
    Decimals: int
    Description: str
    Format: e.PriceDisplayFormatType
    OrderDecimals: int
    Symbol: str


class ErrorInfo(SaxobankModel):
    ErrorCode: str
    Message: str
    ModelState: N[Any]


class InstrumentPriceDetailsResponse(SaxobankModel):
    IsMarketOpen: bool
    ShortTradeDisabled: bool


class PriceInfoResponse(SaxobankModel):
    High: N[Decimal]
    Low: N[Decimal]


class PriceInfoDetailsResponse(SaxobankModel):
    Open: N[Decimal]
    LastTraded: N[Decimal]
    LastTradedSize: N[Decimal]
    LastClose: N[Decimal]
    Volume: N[Decimal]


class QuoteResponse(SaxobankModel):
    Ask: N[Decimal]
    Bid: N[Decimal]
    Mid: N[Decimal]
    # If set, it defines the number of minutes by which the price is delayed.
    DelayedByMinutes: N[int]
    MarketState: N[e.MarketState]
    # Suggested price based on best available price information.
    ReferencePrice: N[Decimal]


# ****************************************************************
# Request Main Models
# ****************************************************************
class InfoPricesRequest(SaxobankModel):
    AccountKey: N[AccountKey]
    AssetType: e.AssetType
    Uic: int
    FieldGroups: list[e.InfoPriceGroupSpec]

    class Config:
        use_enum_values = True


# TODO: Not full covered
# https://www.developer.saxo/openapi/referencedocs/trade/v2/orders/placeorder/b60736b842c31bacab7ae7097512654b
class OrdersRequest(SaxobankModel):
    AccountKey: N[AccountKey]
    PositionId: N[str]
    OrderId: N[str]
    ExternalReference: N[str]
    AssetType: N[e.AssetType]
    Uic: N[int]
    BuySell: N[e.BuySell]
    Amount: N[Decimal]
    OrderType: N[e.PlaceableOrderType]
    OrderDuration: N[OrderDuration]
    OrderPrice: N[Decimal]
    StopLimitPrice: N[Decimal]
    TrailingStopDistanceToMarket: N[Decimal]
    TrailingStopStep: N[Decimal]
    ManualOrder: N[bool]
    Orders: N[list["OrdersRequest"]]

    @validator("Amount")
    def is_positive(cls, v):
        if v <= Decimal(0):
            raise ValidationError("Can't be negative value")
        return v

    @classmethod
    def copy_from(cls, orig: port.PortOrdersRes):
        order = cls(
            AccountKey=orig.AccountKey,
            OrderId=orig.OrderId,
            ExternalReference=orig.ExternalReference,
            AssetType=orig.AssetType,
            Uic=orig.Uic,
            Amount=orig.Amount,
            BuySell=orig.BuySell,
            OrderType=orig.OpenOrderType,
            OrderDuration=orig.Duration,
            ManualOrder=False,
        )
        if order.OrderType != e.PlaceableOrderType.Market:
            order.OrderPrice = orig.Price
        elif order.OrderType == e.PlaceableOrderType.StopLimit:
            order.StopLimitPrice = orig.StopLimitPrice
        elif order.OrderType in [
            e.PlaceableOrderType.TrailingStop,
            # e.PlaceableOrderType.TrailingStopIfBid,
            # e.PlaceableOrderType.TrailingStopIfOffered,
            e.PlaceableOrderType.TrailingStopIfTraded,
        ]:
            order.TrailingStopDistanceToMarket = orig.TrailingStopDistanceToMarket
            order.TrailingStopStep = orig.TrailingStopStep

        return order

    class Config:
        use_enum_values = True


# ****************************************************************
# Response Main Models
# ****************************************************************
class ErrorResponse(SaxobankModel):
    ErrorInfo: ErrorInfo


class InfoPricesErrorResponse(SaxobankModel):
    ErrorCode: str
    Message: str
    ModelState: N[Any]


class InfoPricesResponse(SaxobankModel):
    AssetType: N[e.AssetType]
    Uic: N[int]
    ErrorInfo: N[ErrorInfo]
    ErrorMessage: N[str]
    PriceSource: N[str]
    Commissions: N[CommissionsResponse]
    DisplayAndFormat: N[DisplayAndFormatResponse]
    PriceInfo: N[PriceInfoResponse]
    PriceInfoDetails: N[PriceInfoDetailsResponse]
    InstrumentPriceDetails: N[InstrumentPriceDetailsResponse]
    Quote: N[QuoteResponse]


class OrdersResponse(SaxobankModel):
    ErrorInfo: N[ErrorInfo]
    ExternalReference: N[str]
    OrderId: N[str]
    Orders: N[list["OrdersResponse"]]
