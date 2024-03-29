# from datetime import datetime
from __future__ import annotations

# from collections.abc import Iterable
from decimal import Decimal

# from typing import List
from typing import Optional as N

from ..base import ODataRequest, ODataResponse, SaxobankModel
from ..common import (
    AccountKey,
    AssetType,
    ClientKey,
    MarketState,
    OrderDurationType,
    OrderType,
    PositionFieldGroup,
    PositionStatus,
    PriceMode,
)

# from urllib.parse import quote


# ****************************************************************
# SubModels
# ****************************************************************


class RelatedOrderInfo(SaxobankModel):
    Amount: N[Decimal]
    Duration: N[OrderDurationType]
    OpenOrderType: N[OrderType]
    OrderId: N[str]


# Dynamic Contents for a Position. The following fields are updated as prices change or the position is updated, filled or closed.
class PositionDynamic(SaxobankModel):
    MarketState: N[MarketState]


# Static contents for a position. The following fields do not change when the price is updated
class PositionStatic(SaxobankModel):
    AccountKey: N[AccountKey]
    AssetType: N[AssetType]
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
    Status: N[PositionStatus]


# ****************************************************************
# Request Main Models
# ****************************************************************
class PositionsReq(SaxobankModel):
    ClientKey: ClientKey
    AccountKey: N[AccountKey]
    FieldGroups: N[list[PositionFieldGroup]]

    class Config:
        use_enum_values = True


class PositionsPositionIdReq(SaxobankModel):
    ClientKey: ClientKey
    PositionId: str
    # AccountKey: N[AccountKey]
    # FieldGroups: N[list[PositionFieldGroup]]

    def path_items(self) -> dict[str, str]:
        return {"PositionId": self.PositionId}

    class Config:
        fields = {"PositionId": {"exclude": True}}
        use_enum_values = True


class MeReq(SaxobankModel, ODataRequest):
    FieldGroups: N[list[PositionFieldGroup]]
    PriceMode: N[PriceMode]


# ****************************************************************
# Response Main Models
# ****************************************************************
class PositionsRes(SaxobankModel):
    NetPositionId: N[str]
    PositionId: N[str]
    PositionBase: N[PositionStatic]
    PositionView: N[PositionDynamic]


class MeRes(SaxobankModel, ODataResponse):
    Data: list[PositionsRes]

    # def has_order_id(self, order_id) -> bool | None:
    #     return None if not self.PositionBase else True if self.PositionBase.SourceOrderId == order_id else False

    # def has_instrument(self, asset_type, uic) -> bool | None:
    #     base = self.PositionBase
    #     return None if not base else True if base.AssetType == asset_type and base.Uic == uic else False


# Retrive each paged response.
# Usage
#  r1 = m.PositionsMeResponsePaged.parse_obj(no1)
#  r2 = m.PositionsMeResponsePaged.parse_obj(no2)
#  r1.Data.extend(r2.Data)
# class PositionsMeResponsePaged(c.SaxobankPagedResponseMoel):
#     Data: list[PositionsMeResponse]

#     def find_order_id(self, order_id) -> Iterable[PositionsMeResponse]:
#         return filter(lambda x: x.has_order_id(order_id), self.Data or [])

#     def filter_instrument(self, asset_type, uic) -> Iterable[PositionsMeResponse]:
#         return filter(lambda x: x.has_instrument(asset_type, uic), self.Data or [])
