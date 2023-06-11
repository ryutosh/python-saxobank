# from datetime import datetime
from __future__ import annotations

from typing import List
from typing import Optional as N

from pydantic import Field

from .. import common as c
from .. import enum as e

# from collections.abc import Iterable
# from decimal import Decimal


class ClosedPositionReq(c.SaxobankModel, c.ODataRequest):
    ClientKey: c.ClientKey


class ClosedPositionRes(c.SaxobankModel, c.ODataResponse):
    Data: list[ClosedPositionResponse]


# Not fully covered
class ClosedPosition(c.SaxobankModel):
    AssetType: e.AssetType


class ClosedPositionRequest(c.SaxobankModel):
    ClientKey: c.ClientKey


class PostSubscriptionReq(c.CreateSubscriptionRequest):
    top: N[int] = Field(alias="$top")
    Arguments: N[ClosedPositionRequest]


# Not fully covered
class ClosedPositionResponse(c.SaxobankModel):
    ClosedPositionUniqueId: str
    NetPositionId: N[str]
    ClosedPosition: N[ClosedPosition]

    def __eq__(self, o: object):
        assert isinstance(o, self.__class__)
        try:
            return self.ClosedPositionUniqueId == o.ClosedPositionUniqueId
        except AttributeError:
            return False


class ListResultClosedPositionResponse(c.SaxobankModel, c.ODataResponse):
    Data: List[ClosedPositionResponse]


class PostSubscriptionRes(c.SubscriptionsResModel):
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
