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


class _Portfolio_Clients(_ServiceGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    get_me = partialmethod(_ServiceGroup._openapi_request, endpoint.port.clients.GET_ME)


class _Portfolio_Positions(_ServiceGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    get_me = partialmethod(_ServiceGroup._openapi_request, endpoint.port.positions.GET_ME)
    get_positionid = partialmethod(_ServiceGroup._openapi_request, endpoint.port.positions.GET_POSITION_ID)


class _Portfolio_ClosedPositions(_ServiceGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    get = partialmethod(_ServiceGroup._openapi_request, endpoint.port.closed_positions.GET)
    post_subscription = partialmethod(_ServiceGroup._openapi_request, endpoint.port.closed_positions.POST_SUBSCRIPTION)
    patch_subscription = partialmethod(_ServiceGroup._openapi_request, endpoint.port.closed_positions.PATCH_SUBSCRIPTION)
    delete_subscription = partialmethod(_ServiceGroup._openapi_request, endpoint.port.closed_positions.DELETE_SUBSCRIPTION)


class _Portfolio(_ServiceGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clients = _Portfolio_Clients(self._user_session)
        self.positions = _Portfolio_Positions(self._user_session)
        self.closed_positions = _Portfolio_ClosedPositions(self._user_session)


class _Reference_Instruments(_ServiceGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    details = partialmethod(_ServiceGroup._openapi_request, endpoint.ref.instruments.GET_DETAILS)


class _Reference(_ServiceGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instruments = _Reference_Instruments(self._user_session)


class _Root_Sessions(_ServiceGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    put_capabilities = partialmethod(_ServiceGroup._openapi_request, endpoint.root.sessions.PUT_CAPABILITIES)


class _Root(_ServiceGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sessions = _Root_Sessions(self._user_session)
