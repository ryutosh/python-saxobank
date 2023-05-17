from datetime import datetime
from typing import Any, Optional
from urllib.parse import parse_qs

from pydantic import BaseModel, Field, HttpUrl

from . import enums as e


class AccountKey(str):
    pass


class ClientKey(str):
    pass


class ContextId(str):
    "most 50 characters (a-z, A-Z, -, and 0-9)."
    pass


class SaxobankModel(BaseModel):
    pass


# class CreateSubscriptionRequest(SaxobankModel):
#     ContextId: str
#     ReferenceId: str
#     Format: str
#     Arguments: Any
#     ReplaceReferenceId: Optional[str]


class SaxobankPagedRequestMoel(SaxobankModel):
    _Top: int = Field(None, alias="$top")
    _Skip: int = Field(None, alias="$skip")


class SaxobankPagedResponseMoel(SaxobankModel):
    # _Next: HttpUrl = Field(None, alias="__next")
    _Next: Optional[HttpUrl] = None

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
    ExpirationDateContainsTime: Optional[bool]
    ExpirationDateTime: Optional[datetime]

    class Config:
        use_enum_values = True
