from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from urllib.parse import urljoin

import aiohttp
import portfolio
import simplejson as json
from api_call import Dispatcher
from authorization import OAuth2Authorization
from endpoint import Endpoint, EndpointDefinition, HttpMethod
from environment import RestBaseUrl, WsBaseUrl
from streaming_session import StreamingSession

from saxobank.models import OrdersRequest, OrdersResponse, SaxobankModel
from saxobank.models.common import ContextId

log = getLogger(__name__)


class RateLimiter:
    pass


class UserSession:
    def __init__(
        self,
        rest_base_url: RestBaseUrl,
        http_client: aiohttp.ClientSession,
        rate_limiter: RateLimiter,
        access_token: str | None = None,
    ):
        self.base_url = rest_base_url
        self.http = http_client
        self.limiter = rate_limiter
        self.token = access_token

        # namespace includes
        self.port = portfolio

    async def _auth_header(self, access_token: str | None = None):
        return {"Authorization": f"Bearer {access_token if access_token else self.token}"}

    async def _boiler(self, request_task: Callable, ep: EndpointDefinition, effectual_until: datetime | None = None):
        await self.rate_limiter.throttle(ep.dimension, ep.is_order, effectual_until)

        try:
            log.debug(f"HTTP: Requesting to URL: {ep.url}")
            response = await request_task

        except aiohttp.ClientResponseError as ex:
            log.error(f"HTTP: Request failed with ClientError: {ex}")
            raise exceptions.ResponseError(ex.request_info, ex.status, ex.headers)

        except aiohttp.ClientError as ex:
            log.error(f"HTTP: Request failed with ClientError: {ex}")
            raise exceptions.RequestError()

        else:
            async with response:
                status = response.status
                headers = response.headers
                body = await response.json() if response.content_type == CONTENT_TYPE_JSON else None
                request_info = response.request_info

            log.debug(f"HTTP: Response returned with status:{status}.")

        if 401 <= status:
            log.error(f"HTTP: Req info: {request_info}")
            log.error(f"HTTP: Res body: {body}")
            raise exceptions.ResponseError(request_info, status, headers)

        return status, headers, body
