# from datetime import datetime
from __future__ import annotations

from ..common import (
    AccountKey,
    ClientKey,
    ClientPositionNettingMode,
    ClientPositionNettingProfile,
)
from ..base import SaxobankModel

# from urllib.parse import quote


class MeRes(SaxobankModel):
    ClientId: str
    ClientKey: ClientKey
    DefaultAccountId: str
    DefaultAccountKey: AccountKey
    PositionNettingMode: ClientPositionNettingMode
    PositionNettingProfile: ClientPositionNettingProfile
