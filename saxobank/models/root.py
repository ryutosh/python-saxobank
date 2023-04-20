# from datetime import datetime
from __future__ import annotations

from typing import Optional as N

from . import enums as e
from .common import SaxobankModel


# ****************************************************************
# Request
# ****************************************************************
class ChangeSessionsCapabilitiesRequest(SaxobankModel):
    TradeLevel: N[e.TradeLevel]


# ****************************************************************
# Response
# ****************************************************************
class SessionsCapabilitiesResponse(SaxobankModel):
    AuthenticationLevel: N[e.AuthenticationLevel]
    TradeLevel: N[e.TradeLevel]
