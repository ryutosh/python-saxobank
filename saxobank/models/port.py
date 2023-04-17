# from datetime import datetime
from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from typing import Optional as N

from . import enums as e
from .common import (AccountKey, ClientKey, OrderDuration, SaxobankModel,
                     SaxobankPagedRequestMoel, SaxobankPagedResponseMoel)

# ****************************************************************
# SubModels
# ****************************************************************


class RelatedOrderInfo(SaxobankModel):
    Amount: N[Decimal]
    Duration: N[OrderDuration]
    OpenOrderType: N[e.OrderType]
    OrderId: N[str]


# Dynamic Contents for a Position. The following fields are updated as prices change or the position is updated, filled or closed.
class PositionDynamic(SaxobankModel):
    MarketState: N[e.MarketState]


# Static contents for a position. The following fields do not change when the price is updated
class PositionStatic(SaxobankModel):
    AccountKey: N[AccountKey]
    AssetType: N[e.AssetType]
    Uic: N[int]
    Amount: N[Decimal]
    # If True, the position will not automatically be netted with position in the opposite direction
    IsForceOpen: N[bool]
    # True if the instrument is currently tradable on its exchange.
    IsMarketOpen: N[bool]
    RelatedOpenOrders: N[list[RelatedOrderInfo]]
    RelatedPositionId: N[str]
    SourceOrderId: N[str]
    # The status of the position. Possible values: Open, Closed, Closing, PartiallyClosed, Locked.
    Status: N[e.PositionStatus]


# ****************************************************************
# Request Main Models
# ****************************************************************
class PortOrdersReq(SaxobankPagedRequestMoel):
    FieldGroups: N[list[e.OrderFieldGroup]]
    PriceMode: N[e.PriceMode]

    class Config:
        use_enum_values = True


class PositionsReq(SaxobankModel):
    ClientKey: ClientKey
    AccountKey: N[AccountKey]
    FieldGroups: N[list[e.PositionFieldGroup]]

    class Config:
        use_enum_values = True


class PositionsMeRequest(SaxobankPagedRequestMoel):
    FieldGroups: N[list[e.PositionFieldGroup]]
    PriceMode: N[e.PriceMode]

    class Config:
        use_enum_values = True


# ****************************************************************
# Response Main Models
# ****************************************************************
class PortOrdersRes(SaxobankModel):
    AccountId: str
    AccountKey: AccountKey
    Amount: Decimal
    AssetType: e.AssetType
    Uic: int
    BuySell: e.BuySell
    Duration: OrderDuration
    FilledAmount: N[Decimal]
    IsForceOpen: N[bool]
    IsMarketOpen: N[bool]
    MarketState: N[e.MarketState]
    OpenOrderType: e.OrderType
    OrderId: str
    ExternalReference: N[str]
    Price: N[Decimal]
    RelatedPositionId: N[str]
    Status: e.OrderStatus
    StopLimitPrice: N[Decimal]
    TrailingStopDistanceToMarket: N[Decimal]
    TrailingStopStep: N[Decimal]

    def has_order_id(self, order_id):
        return True if self.OrderId == order_id else False


class PortOrdersResPaged(SaxobankPagedResponseMoel):
    Data: list[PortOrdersRes]

    def find_by_order_id(self, order_id):
        for order in self.Data:
            if order.has_order_id(order_id):
                return order
        return None


class PortClientsMeRes(SaxobankModel):
    ClientId: str
    ClientKey: ClientKey
    DefaultAccountId: str
    DefaultAccountKey: AccountKey
    PositionNettingMode: e.ClientPositionNettingMode
    PositionNettingProfile: e.ClientPositionNettingProfile


class PositionsMeResponse(SaxobankModel):
    NetPositionId: N[str]
    PositionId: N[str]
    PositionBase: N[PositionStatic]
    PositionView: N[PositionDynamic]

    def has_order_id(self, order_id) -> bool | None:
        return None if not self.PositionBase else True if self.PositionBase.SourceOrderId == order_id else False

    def has_instrument(self, asset_type, uic) -> bool | None:
        base = self.PositionBase
        return None if not base else True if base.AssetType == asset_type and base.Uic == uic else False


# Retrive each paged response.
# Usage
#  r1 = m.PositionsMeResponsePaged.parse_obj(no1)
#  r2 = m.PositionsMeResponsePaged.parse_obj(no2)
#  r1.Data.extend(r2.Data)
class PositionsMeResponsePaged(SaxobankPagedResponseMoel):
    Data: list[PositionsMeResponse]

    def find_order_id(self, order_id) -> Iterable[PositionsMeResponse]:
        return filter(lambda x: x.has_order_id(order_id), self.Data or [])

    def filter_instrument(self, asset_type, uic) -> Iterable[PositionsMeResponse]:
        return filter(lambda x: x.has_instrument(asset_type, uic), self.Data or [])
