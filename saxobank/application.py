from __future__ import annotations

import logging
from functools import partialmethod
from typing import Coroutine, Optional, Tuple, cast

import simplejson
from aiohttp import ClientSession
from attr import dataclass

import saxobank

from . import endpoint, model
from .environment import LIVE, SIM, SaxobankEnvironment, WsBaseUrl
from .model import chart, req
from .model.base import SaxobankModel
from .model.common import ContextId, ResponseCode

# from .streaming_session import StreamingSession
from .user_session import RateLimiter, UserSession, _OpenApiRequestResponse

# from environment import Environment

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Application:
    def __init__(
        self,
        saxobank_environment: SaxobankEnvironment,
        application_key,
        application_secret,
    ):
        self.saxo_env = saxobank_environment
        self.__app_key = application_key
        self.__app_secret = application_secret
        self.limiter = RateLimiter()

    @classmethod
    def LIVE(cls, application_key, application_secret):
        return cls(LIVE, application_key, application_secret)

    @classmethod
    def SIM(cls, application_key, application_secret):
        return cls(SIM, application_key, application_secret)

    def create_session(self, access_token: Optional[str] = None) -> SessionFacade:
        client_session = ClientSession(json_serialize=simplejson.dumps)
        user_session = UserSession(
            self.saxo_env.rest_base_url, client_session, self.limiter, access_token
        )
        # return SessionFacade(rest_base_url, ws_base_url, access_token)
        return Client(user_session, self.saxo_env.ws_base_url)


class Client:
    # def __init__(self, rest_base_url, ws_base_url, access_token: Optional[str] = None) -> None:
    #     client_session = ClientSession(json_serialize=simplejson.dumps)
    #     self.user_session = UserSession(self.rest_base_url, client_session, self.limiter, access_token)

    def __init__(self, user_session: UserSession, ws_base_url: WsBaseUrl) -> None:
        self._user_session = user_session
        self._ws_base_url = ws_base_url

    def _openapi_request(
        self,
        endpoint: endpoint.Endpoint,
        request_model: SaxobankModel | None = None,
        access_token: str | None = None,
    ) -> (
        _OpenApiRequestResponse
    ):  # -> Tuple[ResponseCode, Optional[SaxobankModel], Optional[Coroutine]]:
        return self._user_session.openapi_request(endpoint, request_model, access_token)

    # def create_streaming_session(
    #     self, context_id: Optional[ContextId] = None, access_token: Optional[str] = None
    # ) -> StreamingSession:
    #     return StreamingSession(
    #         self._ws_base_url,
    #         self._user_session,
    #         self._user_session.http,
    #         access_token if access_token else self._user_session.token,
    #         context_id,
    #     )

    # port_clients_me_get = partialmethod(_openapi_request, endpoint.PORT_CLIENTS_ME_GET)
    # port_closedpositions_get = partialmethod(_openapi_request, endpoint.PORT_CLOSEDPOSITIONS_GET)
    # ref_instruments_details_get = partialmethod(
    #     _openapi_request, endpoint.REF_INSTRUMENTS_DETAILS_GET
    # )
    # root_sessions_capabilities_put = partialmethod(
    #     _openapi_request, endpoint.ROOT_SESSIONS_CAPABILITIES_PUT
    # )

    # charts_get = APIs(request=partial(_openapi_request, endpoint.PORT_CLIENTS_ME_GET))
    async def get_chart_charts(
        self, request: model.req.GetChartCharts, access_token: str | None = None
    ) -> model.resp.GetChartChartsResp:
        """Get chart data.

        Returns timestamped OHLC samples for a single instrument identified by UIC and AssetType.
        The time period covered by the samples and interval size between them are controlled by the combination of parameters Horizon, Time, Mode and Count.

        *See [OpenAPI Reference](https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/getchartdataasync/387cfc61d3292d9237095b9144ac4733) for original info.*

        Args:
            request: Request to endpoint.
            access_token: Access token used for this request.

        Returns:
            Response from endpoint.

        Raises:
            RequestError: Failed to requst.
        """
        ret = await self._user_session.openapi_request2(
            endpoint.REF_INSTRUMENTS_DETAILS_GET, request, access_token
        )
        return cast(model.resp.GetChartChartsResp, ret)
