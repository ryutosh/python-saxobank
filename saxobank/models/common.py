from __future__ import annotations

import string
from datetime import datetime
from enum import Enum, auto
from typing import Any, Optional, Type
from urllib.parse import parse_qs
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl

from . import enums as e


class AccountKey:
    def __init__(self, value: str):
        self.__value = str(value)

    def __repr__(self):
        return repr(self.__value)


class ClientKey:
    def __init__(self, value: str):
        self.__value = str(value)

    def __repr__(self):
        return repr(self.__value)


class ContextId:
    MAX_ID_LENGTH: int = 50
    MIN_ID_LENGTH: int = 1
    ACCEPTABLE_CHARS: str = string.ascii_letters + string.digits + "-"

    def __init__(self, id: int | str | None = None):
        id = id if id else str(uuid4()).replace("-", "")
        assert self.validate(id)
        self.__id = str(id)

    def __eq__(self, o: object):
        return self.__id == str(o)

    def __str__(self):
        return str(self.__id)

    def __repr__(self):
        return repr(self.__id)

    @classmethod
    def validate(cls, id: int | str) -> bool:
        chars = str(id)
        return (chars == "".join([c for c in chars if c in cls.ACCEPTABLE_CHARS])) and (
            cls.MIN_ID_LENGTH <= len(chars) <= cls.MAX_ID_LENGTH
        )


class HeartbeatReason(Enum):
    NoNewData = auto()
    SubscriptionTemporarilyDisabled = auto()
    SubscriptionPermanentlyDisabled = auto()


class ODataModel(BaseModel):
    inlinecount: InlineCountValue
    top: Optional[int] = Field(alias="$top")
    skip: Optional[int] = Field(alias="$skip")


class ReferenceId:
    def __init__(self, id: int | str | None = None):
        id = id if id else str(uuid4())
        assert self.validate(id)
        self.__id = str(id)

    def __eq__(self, o: object):
        return self.__id == str(o)

    def __str__(self):
        return str(self.__id)

    def __repr__(self):
        return repr(self.__id)

    @classmethod
    def validate(cls, id: int | str) -> bool:
        return True


class SaxobankModel(BaseModel):
    def path_items(self) -> dict[str, Any]:
        return {}

    class Config:
        arbitrary_types_allowed = True


class SubscriptionsResModel(SaxobankModel):
    ContextId: ContextId
    Format: str
    InactivityTimeout: int
    ReferenceId: ReferenceId
    RefreshRate: int
    Snapshot: Type[SaxobankModel]
    State: str
    Tag: str


class InlineCountValue(Enum):
    """
    Defines an enumeration for $inlinecount query option values.
    """

    ALL_PAGES = "AllPages"  # The results will contain a total count of items in the queried dataset.
    NONE = "None"  # The results will not contain an inline count.


# class CreateSubscriptionRequest(SaxobankModel):
#     ContextId: str
#     ReferenceId: str
#     Format: str
#     Arguments: Any
#     ReplaceReferenceId: Optional[str]


class SaxobankPagedRequestMoel(SaxobankModel):
    top: int = Field(None, alias="$top")
    skip: int = Field(None, alias="$skip")


class SaxobankPagedResponseMoel(SaxobankModel):
    next: HttpUrl = Field(None, alias="__next")
    # next: HttpUrl | None = None

    # class Config:
    #     fields = {"_Next": "__next"}

    def next_page(self):
        if not self.next:
            return None

        query = parse_qs(self.next.query)
        top = query.get("top", [None])[0]
        skip = query.get("skip", [None])[0]
        return (top, skip) if top and skip else None


class OrderDuration(SaxobankModel):
    DurationType: e.OrderDurationType
    ExpirationDateContainsTime: Optional[bool]
    ExpirationDateTime: Optional[datetime]

    class Config:
        use_enum_values = True
