from __future__ import annotations

import string
from collections import namedtuple
from datetime import datetime
from enum import Enum, auto, unique
from typing import Any, Container, Final, List, Literal, Optional, Tuple, Type, Union, cast
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
    NextRequest: Tuple[str, str] = namedtuple("NextRequest", ["path", "query"])

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


class _SaxobankModel(BaseModel):
    def __hash__(self) -> int:
        return hash(id(self))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return hash(self) == hash(o)

    def path_items(self) -> dict[str, Any]:
        return {}

    def as_request(self, **kwargs: Any) -> dict:
        kwargs.update({"exclude_unset": True, "exclude_none": True})
        return super().dict(**kwargs)

    def dict_lower_case(self, **kwargs: Any) -> dict:
        kwargs.update({"by_alias": True, "exclude_unset": True, "exclude_none": True})
        return super().dict(**kwargs)

    def merge(self, delta: _SaxobankModel) -> _SaxobankModel:
        new = self.dict(exclude_unset=True)
        for key, value in delta.dict().items():
            # if isinstance(value, _SaxobankModel):
            print(f"processing key:{key} and value:{value}")
            delta_field = getattr(delta, key)
            if isinstance(delta_field, _SaxobankModel):
                if hasattr(self, key):
                    new[key] = getattr(self, key).merge(delta_field)
                else:
                    new[key] = delta_field
            elif isinstance(delta_field, list):
                if hasattr(self, key):
                    new[key] = list(set(getattr(self, key)) | set(delta_field))
                else:
                    new[key] = delta_field
                # if hasattr(self, key):
                #     base_field = getattr(self, key)
                #     for inner in delta_field:
                #         if inner in base_field:
            elif value is not None:
                new[key] = value

        return self.__class__(**new)

    # def update(self, value: Any, key: Optional[str] = None) -> None:
    #     if isinstance(value, _SaxobankModel):
    #         cast(_SaxobankModel, value)
    #         # for inner_key, inner_value in value.__fields__.items():
    #         for inner_key, inner_value in value:
    #             # if isinstance(inner_value, _SaxobankModel):
    #             #     d[inner_key] = self.merge(inner_value)
    #             # else:
    #             #     d[inner_key] = inner_value
    #             self.update(inner_value, inner_key)
    #     elif key:
    #         try:
    #             print(f"processing on key:{key} and value:{value}")
    #             # self.__fields__[key] = value

    #             # self.__setattr__(key, value)
    #             setattr(self, key, value)

    #         except Exception as ex:
    #             print(ex)
    #             print(f"error at key:{key} and value:{value}")

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
        alias_generator = str.lower
        allow_population_by_field_name = True


class ErrorResponse(_SaxobankModel):
    ErrorCode: str
    Message: str
    ModelState: Optional[Any]


class ListResultModel(_SaxobankModel):
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


class _Snapshot(_SaxobankModel):
    Snapshot: _SaxobankModel

    def apply_delta(self, delta: _SaxobankModel) -> _SaxobankModel:
        d = self.dict()
        d.update(delta.dict(exclude_unset=True))
        return self.__class__(**d)


class _RespCreateSubscription(_SaxobankModel):
    ContextId: ContextId
    ReferenceId: ReferenceId
    State: Literal["Active"]
    InactivityTimeout: int
    Format: Optional[str] = None
    RefreshRate: int
    Tag: Optional[str] = None
    Snapshot: _Snapshot
    # Snapshot: Union[Type[SubscriptionSnapshotModel], Type[ListResultModel]]


# class SubscriptionSnapshotModel(_SaxobankModel):
#     def apply_delta(self, delta: SubscriptionSnapshotModel):
#         d = self.dict()
#         d.update(delta.dict(exclude_unset=True))
#         return delta.__class__(**d)


class _RespPartedStreaming(_SaxobankModel):
    ReferenceId: ReferenceId
    Data: _SaxobankModel
    Timestamp: datetime
    TotalPartition: Optional[int]
    PartitionNumber: Optional[int]


# class _SnapshotPartedMixin:
#     def __init__(self, *args: Any, **kwargs: Any) -> None:
#         self._parted_delta: SaxobankModel = None
#         super().__init__(*args, **kwargs)

#     def apply_delta(delta: _SaxobankModel):
#         if delta.PartitionNumber is not None:
#             self._
#         self._parted_delta.apply_delta(delta)


class InlineCountValue(Enum):
    """
    Defines an enumeration for $inlinecount query option values.
    """

    ALL_PAGES = "AllPages"  # The results will contain a total count of items in the queried dataset.
    NONE = "None"  # The results will not contain an inline count.


class _ReqCreateSubscription(_SaxobankModel):
    ContextId: ContextId
    ReferenceId: ReferenceId
    Tag: Optional[str] = None
    Format: Optional[str] = None
    RefreshRate: Optional[int] = None
    ReplaceReferenceId: Optional[ReferenceId] = None


class _ReqRemoveSubscription(_SaxobankModel):
    ContextId: ContextId
    ReferenceId: ReferenceId


class OrderDuration(_SaxobankModel):
    DurationType: e.OrderDurationType
    ExpirationDateContainsTime: Optional[bool]
    ExpirationDateTime: Optional[datetime]

    class Config:
        use_enum_values = True
