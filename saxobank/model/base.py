"""Provides base classes these are not suppose to be used generally.

You can override classes in the modules and make new data models.
But models are strongly bundled with Endpoint definitions(endpoint.py),
thus, createing models by user-side is not supposed to.
"""
from __future__ import annotations

from collections import namedtuple
from datetime import datetime
from typing import Any, Container, Final, List, Literal, Optional, Sequence, Tuple, Type, Union, cast, Iterator
from urllib.parse import parse_qs, urlparse
from pydantic import BaseModel, Field, HttpUrl
from typing import Any, Container, Final, List, Literal, Optional, Sequence, Tuple, Type, Union, cast, Iterator
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, RootModel
from .common import ContextId, ReferenceId, InlineCountValue


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


class SaxobankModel(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

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

    def merge(self, delta: SaxobankModel) -> SaxobankModel:
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