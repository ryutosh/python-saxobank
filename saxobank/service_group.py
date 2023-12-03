from __future__ import annotations

from collections.abc import Coroutine
from datetime import datetime
from functools import partialmethod
from typing import Optional, Tuple

from . import endpoint
from .model.common import SaxobankModel

# from .user_session import UserSession


class _ServiceGroup:
    def __init__(self, user_session: UserSession):
        self._user_session = user_session

    def _openapi_request(
        self,
        endpoint: endpoint.Endpoint,
        request_model: SaxobankModel | None = None,
        effectual_until: datetime | None = None,
        access_token: str | None = None,
    ) -> Tuple[ResponseCode, Optional[SaxobankModel], Optional[Coroutine]]:
        return self._user_session.openapi_request(endpoint, request_model, effectual_until, access_token)
