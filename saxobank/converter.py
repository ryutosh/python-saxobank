from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from .model.base import SaxobankModel2
from .model.resp.port import SaxobankRootModel2


def _as_request_factory(items: list[tuple[str, Any]]) -> dict[str, Any]:
    adict: dict[str, Any] = {}
    for key, value in items:
        if value is None:
            continue
        if isinstance(value, Enum):
            value = value.value
        elif isinstance(value, datetime):
            value = value.isoformat()
        adict[key] = value

    return adict


def as_request(model: SaxobankModel2) -> dict[str, Any]:
    # return asdict(model, dict_factory=_as_request_factory)
    if isinstance(model, SaxobankRootModel2):
        return [as_request(member) for member in model._root]

    if isinstance(model, list):
        return [asdict(e, dict_factory=_as_request_factory) for e in model]
    else:
        return asdict(model, dict_factory=_as_request_factory)


def from_response(obj: dict | list, model: dataclass) -> dataclass:
    # return model(**obj)
    if isinstance(obj, list):
        return [model(**e) for e in obj]
    else:
        return model(**obj)
