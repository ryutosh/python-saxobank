# from datetime import datetime
from __future__ import annotations

# from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from typing import Optional as N

import saxobank.models.enums as e

# from . import enums as e
from saxobank.models.common import SaxobankModel  # , SaxobankPagedRequestMoel, SaxobankPagedResponseMoel


class ReqOrderActivities(SaxobankModel):
    FromDateTime: N[datetime]
    ToDateTime: N[datetime]
    # Status: N[e.OrderType]


class ResOrderActivities(SaxobankModel):
    PositionId: str
    OrderId: str
    AssetType: e.AssetType
    Uic: int
    BuySell: e.BuySell
    ActivityTime: datetime  # Time of the activity
    Amount: Decimal  # Order amount
    ExecutionPrice: Decimal  # Execution price of this particular fill (if multiple fills)
