# from datetime import datetime
from __future__ import annotations

from ..base import SaxobankModel
from ..common import TradeLevel

# from urllib.parse import quote


class PutCapabilities(SaxobankModel):
    TradeLevel: TradeLevel
