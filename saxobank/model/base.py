"""Provides base classes these are not suppose to be used generally.

You can override classes in the modules and make new data models.
But models are strongly bundled with Endpoint definitions(endpoint.py),
thus, createing models by user-side is not supposed to.
"""
from collections import namedtuple
from dataclasses import dataclass, fields
from datetime import datetime
from enum import Enum
from inspect import get_annotations
from types import GenericAlias
from typing import (
    Any,
    ClassVar,
    Container,
    Final,
    Iterator,
    Literal,
    Optional,
    Sequence,
    Type,
    cast,
    get_type_hints,
)
from urllib.parse import parse_qs, urlparse

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, RootModel
from typeguard import CollectionCheckStrategy, TypeCheckError, check_type

from .. import exception
from .common import ContextId, InlineCountValue, OrderDurationType, ReferenceId


def _checkinstance(name: str, instance: Any, cls: type) -> bool:
    print(f"check: {name} is {cls}")
    if not isinstance(instance, cls):
        raise ValueError(
            f"Field {name} expected as {cls.__name__}, but {type(instance).__name__} given."
        )
    return True


def ommit_datetime_zero(dt: str) -> datetime:
    """Less than Python 3.11 can't handle format tailing with 'Z'."""
    if 1 <= len(dt) and dt[-1] == "Z":
        return datetime.fromisoformat(dt[:-1])
    return datetime.fromisoformat(dt)


@dataclass
class SaxobankModel2:
    _url_route: ClassVar[set[str]] = set()

    def routes(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name in self._url_route}

    def __post_init__(self) -> None:
        """Called by dataclass init method, then validate data.

        Validation run by type-hints marked on fields of dataclass.

        Raises: ValueError: Value is not comply with type-hints.
        """

        schema = get_annotations(self.__class__, eval_str=True)

        for field in fields(self):
            name = field.name
            try:
                check_type(
                    getattr(self, name),
                    schema[name],
                    collection_check_strategy=CollectionCheckStrategy.ALL_ITEMS,
                )

            except TypeCheckError:
                raise ValueError(f"Invalid value of {name}. Expected {schema[name].__name__}.")

            # t = schema[field.name]
            # v = getattr(self, field.name)

            # if isinstance(t, GenericAlias) and t.__origin__ == list:
            #     for i, e in enumerate(v):
            #         _checkinstance(f"{field.name}[{i}]", e, t.__args__[0])
            # else:
            #     _checkinstance(field.name, v, t)


class ODataRequest(BaseModel):
    inlinecount: Optional[InlineCountValue] = None
    top: Optional[int] = Field(alias="$top")
    skip: Optional[int] = Field(alias="$skip")


class ODataResponse(BaseModel):
    count: Optional[int] = Field(alias="__count")
    next: HttpUrl = Field(None, alias="__next")
    NextRequest: tuple[str, str] = namedtuple("NextRequest", ["path", "query"])

    @property
    def next_request(self) -> Optional[NextRequest]:
        if not self.next:
            return None

        parsed = urlparse(self.next)
        path = str(parsed.path)
        query = {
            str.lower(k): v[0] if len(v) == 1 else v
            for (k, v) in parse_qs(str(parsed.query)).items()
        }
        return self.NextRequest(path, query)

    # def next_request(self, request_model: ODataRequest) -> ODataRequest:
    #     if not self.next:
    #         return request_model

    #     query = parse_qs(self.next.query)
    #     next_model = request_model.copy()
    #     next_model.top = int(query["top"][0]) if "top" in query else None
    #     next_model.skip = int(query["skip"][0]) if "skip" in query else None
    #     return next_model


class SaxobankModel(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True, extra="forbid")

    def __eq__(self, o: Any) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return hash(self) == hash(o)

    # config of frozen=True will automatically generates it and makes model hashable.
    # def __hash__(self) -> int:
    #     return hash(id(self))

    def as_request_body(self) -> dict[str, Any]:
        # return self.model_dump_json(exclude_unset=True, exclude_none=True)
        return self.model_dump(exclude_unset=True, exclude_none=True)

    def path_items(self) -> dict[str, Any]:
        return {}

    def as_request(self, **kwargs: Any) -> dict:
        kwargs.update({"exclude_unset": True, "exclude_none": True})
        return super().dict(**kwargs)

    def dict_lower_case(self, **kwargs: Any) -> dict:
        kwargs.update({"by_alias": True, "exclude_unset": True, "exclude_none": True})
        return super().dict(**kwargs)

    def merge(self, delta) -> "SaxobankModel":
        new = self.dict(exclude_unset=True)
        for key, value in delta.dict().items():
            # if isinstance(value, SaxobankModel):
            print(f"processing key:{key} and value:{value}")
            delta_field = getattr(delta, key)
            if isinstance(delta_field, SaxobankModel):
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
    #     if isinstance(value, SaxobankModel):
    #         cast(SaxobankModel, value)
    #         # for inner_key, inner_value in value.__fields__.items():
    #         for inner_key, inner_value in value:
    #             # if isinstance(inner_value, SaxobankModel):
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

    # class Config:
    #     arbitrary_types_allowed = True
    #     use_enum_values = True
    #     alias_generator = str.lower
    #     allow_population_by_field_name = True


# class _SaxobankRootModel(RootModel[Any]):
# class _SaxobankRootModel(RootModel):
class SaxobankRootModel(RootModel[Sequence[SaxobankModel]]):
    """Base class of all list type Saxobank request parameters, response or their composits.

    Class provides iteration for its elements.

    Attributes:
        None: No public attributes.
    """

    # root: Sequence[SaxobankModel]

    # Reporting: reportIncompatibleMethodOverride may a bug of Pydantic v2.
    def __iter__(self) -> Iterator[SaxobankModel]:
        return iter(self.root)

    def __getitem__(self, item: int) -> SaxobankModel:
        return self.root[item]


class ErrorResponse(SaxobankModel):
    ErrorCode: str
    Message: str
    ModelState: Optional[Any]


class OrderDuration(SaxobankModel):
    DurationType: OrderDurationType
    ExpirationDateContainsTime: Optional[bool]
    ExpirationDateTime: Optional[datetime]

    class Config:
        use_enum_values = True


class ListResultModel(SaxobankModel):
    count: Optional[int] = Field(alias="__count")
    next: HttpUrl = Field(alias="__next")
    MaxRows: Optional[int]
    # Data: list[Type[SubscriptionSnapshotModel]]

    # def apply_delta(self, delta: SubscriptionSnapshotModel):
    #     copy = self.Data.copy()

    #     try:
    #         idx = copy.index(delta)

    #     except ValueError:
    #         copy.append(delta)

    #     else:
    #         copy[idx] = copy[idx].apply_delta(delta)

    #     return copy


class _Snapshot(SaxobankModel):
    Snapshot: SaxobankModel

    def apply_delta(self, delta: SaxobankModel) -> SaxobankModel:
        d = self.dict()
        d.update(delta.dict(exclude_unset=True))
        return self.__class__(**d)


class _RespCreateSubscription(SaxobankModel):
    ContextId: ContextId
    ReferenceId: ReferenceId
    State: Literal["Active"]
    InactivityTimeout: int
    Format: Optional[str] = None
    RefreshRate: int
    Tag: Optional[str] = None
    Snapshot: _Snapshot
    # Snapshot: Union[Type[SubscriptionSnapshotModel], Type[ListResultModel]]


# class SubscriptionSnapshotModel(SaxobankModel):
#     def apply_delta(self, delta: SubscriptionSnapshotModel):
#         d = self.dict()
#         d.update(delta.dict(exclude_unset=True))
#         return delta.__class__(**d)


class _RespPartedStreaming(SaxobankModel):
    ReferenceId: ReferenceId
    Data: SaxobankModel
    Timestamp: datetime
    TotalPartition: Optional[int]
    PartitionNumber: Optional[int]


# class _SnapshotPartedMixin:
#     def __init__(self, *args: Any, **kwargs: Any) -> None:
#         self._parted_delta: SaxobankModel = None
#         super().__init__(*args, **kwargs)

#     def apply_delta(delta: SaxobankModel):
#         if delta.PartitionNumber is not None:
#             self._
#         self._parted_delta.apply_delta(delta)


class _ReqCreateSubscription(SaxobankModel):
    ContextId: ContextId
    ReferenceId: ReferenceId
    Tag: Optional[str] = None
    Format: Optional[str] = None
    RefreshRate: Optional[int] = None
    ReplaceReferenceId: Optional[ReferenceId] = None


class _ReqRemoveSubscription(SaxobankModel):
    ContextId: ContextId
    ReferenceId: ReferenceId
