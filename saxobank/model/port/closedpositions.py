# from datetime import datetime
from __future__ import annotations

from typing import List
from typing import Optional as N

from pydantic import Field

from ..base import (
    ODataRequest,
    ODataResponse,
    SaxobankModel,
    _ReqCreateSubscription,
    _RespCreateSubscription,
)
from ..common import AssetType, ClientKey

# from collections.abc import Iterable
# from decimal import Decimal


class ClosedPositionReq(SaxobankModel, ODataRequest):
    ClientKey: ClientKey


class ClosedPositionRes(SaxobankModel, ODataResponse):
    Data: list[ClosedPositionResponse]


# Not fully covered
class ClosedPosition(SaxobankModel):
    AssetType: AssetType


class ClosedPositionRequest(SaxobankModel):
    ClientKey: ClientKey


class PostSubscriptionReq(_ReqCreateSubscription):
    top: N[int] = Field(alias="$top")
    Arguments: N[ClosedPositionRequest]


# Not fully covered
class ClosedPositionResponse(SaxobankModel):
    ClosedPositionUniqueId: str
    NetPositionId: N[str]
    ClosedPosition: N[ClosedPosition]

    def __eq__(self, o: object):
        assert isinstance(o, self.__class__)
        try:
            return self.ClosedPositionUniqueId == o.ClosedPositionUniqueId
        except AttributeError:
            return False


class ListResultClosedPositionResponse(SaxobankModel, ODataResponse):
    Data: List[ClosedPositionResponse]


class PostSubscriptionRes(_RespCreateSubscription):
    Snapshot: ListResultClosedPositionResponse


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
