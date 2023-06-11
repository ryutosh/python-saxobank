from __future__ import annotations

from decimal import Decimal
from typing import Optional as N

from . import enum as e
from .common import OrderDuration, SaxobankModel, SubscriptionsResModel

# ****************************************************************
# SubModels
# ****************************************************************


class RelatedOrderInfo(SaxobankModel):
    Amount: N[Decimal]
    Duration: N[OrderDuration]
    OpenOrderType: N[e.OrderType]
    OrderId: N[str]


class ChartResponse(SaxobankModel):
    pass


class ChartsSubscriptionsRes(SubscriptionsResModel):
    Snapshot: ChartResponse
