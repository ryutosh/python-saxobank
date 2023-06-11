# from datetime import datetime
from __future__ import annotations

from .. import common as c
from .. import enum as e

# from urllib.parse import quote


class MeRes(c.SaxobankModel):
    ClientId: str
    ClientKey: c.ClientKey
    DefaultAccountId: str
    DefaultAccountKey: c.AccountKey
    PositionNettingMode: e.ClientPositionNettingMode
    PositionNettingProfile: e.ClientPositionNettingProfile
