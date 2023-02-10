from datetime import datetime
from typing import Optional as N
from urllib.parse import parse_qs

from pydantic import BaseModel, Field, HttpUrl

from . import enums as e


class AccountKey(str):
    pass


class ClientKey(str):
    pass


class SaxobankModel(BaseModel):
    pass


class SaxobankPagedRequestMoel(SaxobankModel):
    _Top: int = Field(None, alias="$top")
    _Skip: int = Field(None, alias="$skip")


class SaxobankPagedResponseMoel(SaxobankModel):
    # _Next: HttpUrl = Field(None, alias="__next")
    _Next: N[HttpUrl] = None

    class Config:
        fields = {"_Next": "__next"}

    def next_page(self):
        if not self._Next:
            return None

        query = parse_qs(self._Next.query)
        top = query.get("top", [None])[0]
        skip = query.get("skip", [None])[0]
        return (top, skip) if top and skip else None


class OrderDuration(SaxobankModel):
    DurationType: e.OrderDurationType
    ExpirationDateContainsTime: N[bool]
    ExpirationDateTime: N[datetime]

    class Config:
        use_enum_values = True
