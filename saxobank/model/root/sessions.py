# from datetime import datetime
from __future__ import annotations

from .. import common as c
from .. import enum as e

# from urllib.parse import quote


class PutCapabilities(c._SaxobankModel):
    TradeLevel: e.TradeLevel
