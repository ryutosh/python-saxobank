# from datetime import datetime
from __future__ import annotations

from .. import common as _c
from .. import enum as _e

# from urllib.parse import quote


class MeRes(SaxobankModel):
    ClientId: str
    ClientKey: _c.ClientKey
    DefaultAccountId: str
    DefaultAccountKey: _c.AccountKey
    PositionNettingMode: _e.ClientPositionNettingMode
    PositionNettingProfile: _e.ClientPositionNettingProfile
