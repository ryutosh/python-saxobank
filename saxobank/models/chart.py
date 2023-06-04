from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from typing import Optional as N
from urllib.parse import quote

from . import enums as e
from .common import (
    AccountKey,
    ClientKey,
    OrderDuration,
    SaxobankModel,
    SaxobankPagedRequestMoel,
    SaxobankPagedResponseMoel,
    SubscriptionsResModel,
)

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
