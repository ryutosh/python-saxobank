from __future__ import annotations

import string
from collections import namedtuple
from datetime import datetime
from enum import Enum, auto, unique
from typing import Any, Final, List, Optional, Tuple, Type, Union
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl

from . import enum as e


class AccountKey(str):
    pass


class ClientKey(str):
    pass


class ContextId(str):
    MAX_ID_LENGTH: int = 50
    MIN_ID_LENGTH: int = 1
    ACCEPTABLE_CHARS: str = string.ascii_letters + string.digits + "-"

    def __new__(cls, v: Optional[object] = None) -> ContextId:
        id = v if v else str(uuid4())
        if not cls.validate(id):
            raise ValueError
        return super().__new__(cls, id)

    @classmethod
    def validate(cls, v: object) -> bool:
        chars = str(v)
        return all([c in cls.ACCEPTABLE_CHARS for c in chars]) and (cls.MIN_ID_LENGTH <= len(chars) <= cls.MAX_ID_LENGTH)


class ODataRequest(BaseModel):
    inlinecount: Optional[InlineCountValue] = None
    top: Optional[int] = Field(alias="$top")
    skip: Optional[int] = Field(alias="$skip")


class ODataResponse(BaseModel):
    count: Optional[int] = Field(alias="__count")
    next: HttpUrl = Field(None, alias="__next")
    NextRequest = namedtuple("NextRequest", ["path", "query"])

    @property
    def next_request(self) -> Optional[NextRequest]:
        if not self.next:
            return None

        parsed = urlparse(self.next)
        path = str(parsed.path)
        query = {str.lower(k): v[0] if len(v) == 1 else v for (k, v) in parse_qs(str(parsed.query)).items()}
        return self.NextRequest(path, query)

    # def next_request(self, request_model: ODataRequest) -> ODataRequest:
    #     if not self.next:
    #         return request_model

    #     query = parse_qs(self.next.query)
    #     next_model = request_model.copy()
    #     next_model.top = int(query["top"][0]) if "top" in query else None
    #     next_model.skip = int(query["skip"][0]) if "skip" in query else None
    #     return next_model


class ReferenceId(str):
    def __new__(cls, v: Optional[object] = None) -> ReferenceId:
        id = v if v else str(uuid4())
        return super().__new__(cls, id)


@unique
class ResponseCode(Enum):
    OK = 200
    CREATED = 201
    ACCEPTED = 202  # 202 is not documented, but returned actually.
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

    @property
    def is_successful(self) -> bool:
        return self.value < 400

    @property
    def is_error(self) -> bool:
        return 400 <= self.value


class SaxobankModel(BaseModel):
    def apply_delta(self, delta: SaxobankModel):
        d = self.dict()
        d.update(delta.dict(exclude_unset=True))
        return delta.__class__(**d)

    def path_items(self) -> dict[str, Any]:
        return {}

    def dict(self, **kwargs) -> dict:
        return super().dict(exclude_unset=True, exclude_none=True, **kwargs)

    def as_request(self, **kwargs) -> dict:
        return super().dict(exclude_unset=True, exclude_none=True, **kwargs)

    def dict_lower_case(self, **kwargs) -> dict:
        return super().dict(by_alias=True, exclude_unset=True, exclude_none=True, **kwargs)

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
        alias_generator = str.lower
        allow_population_by_field_name = True


class ErrorResponse(SaxobankModel):
    ErrorCode: str
    Message: str
    ModelState: Optional[Any]


class ListResultModel(SaxobankModel):
    count: Optional[int] = Field(alias="__count")
    next: HttpUrl = Field(alias="__next")
    MaxRows: Optional[int]
    Data: List[Type[SubscriptionSnapshotModel]]

    def apply_delta(self, delta: SubscriptionSnapshotModel):
        copy = self.Data.copy()

        try:
            idx = copy.index(delta)

        except ValueError:
            copy.append(delta)

        else:
            copy[idx] = copy[idx].apply_delta(delta)

        return copy


class SubscriptionsResModel(SaxobankModel):
    ContextId: ContextId
    Format: str
    InactivityTimeout: int
    ReferenceId: ReferenceId
    RefreshRate: int
    # Snapshot: Union[Type[SubscriptionSnapshotModel], Type[ListResultModel]]
    State: str
    Tag: str


# class SubscriptionSnapshotModel(SaxobankModel):
#     def apply_delta(self, delta: SubscriptionSnapshotModel):
#         d = self.dict()
#         d.update(delta.dict(exclude_unset=True))
#         return delta.__class__(**d)


class InlineCountValue(Enum):
    """
    Defines an enumeration for $inlinecount query option values.
    """

    ALL_PAGES = "AllPages"  # The results will contain a total count of items in the queried dataset.
    NONE = "None"  # The results will not contain an inline count.


class CreateSubscriptionRequest(SaxobankModel):
    ContextId: ContextId
    ReferenceId: ReferenceId
    ReplaceReferenceId: Optional[ReferenceId]
    Format: Optional[str]
    RefreshRate: Optional[int]
    Tag: Optional[str]


class OrderDuration(SaxobankModel):
    DurationType: e.OrderDurationType
    ExpirationDateContainsTime: Optional[bool]
    ExpirationDateTime: Optional[datetime]

    class Config:
        use_enum_values = True
