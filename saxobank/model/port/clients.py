# from datetime import datetime
from dataclasses import dataclass

from ..base import SaxobankModel2
from ..common import AccountKey, ClientKey, ClientPositionNettingMode, ClientPositionNettingProfile

# from urllib.parse import quote


@dataclass
class MeRes(SaxobankModel2):
    ClientId: str
    ClientKey: ClientKey
    DefaultAccountId: str
    DefaultAccountKey: AccountKey
    PositionNettingMode: ClientPositionNettingMode
    PositionNettingProfile: ClientPositionNettingProfile
