from __future__ import annotations

from datetime import datetime
from functools import partialmethod

import aiohttp
import simplejson as json
from endpoint import ContentType, Endpoint, EndpointDefinition, HttpMethod
from environment import RestBaseUrl, WsBaseUrl
from model.common import SaxobankModel
from streaming_session import StreamingSession

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

    async def openapi_request(
        self,
        endpoint: EndpointDefinition,
        request_model: SaxobankModel | None = None,
        effectual_until: datetime | None = None,
        access_token: str | None = None,
    ):
        url = endpoint.url(self.base_url, request_model.path_items())
        req_data = request_model.dict(exclude_unset=True) if request_model else None
        params = req_data if endpoint.method == HttpMethod.GET else None
        data = req_data if endpoint.method != HttpMethod.GET else None

        await self.limiter.throttle(endpoint.dimension, endpoint.is_order, effectual_until)

        try:
            headers = {"Authorization": f"Bearer {access_token if access_token else self.token}"}
            response = await self.http.request(
                endpoint.method,
                url,
                params=params,
                data=data if endpoint.content_type != ContentType.JSON else None,
                json=data if endpoint.content_type == ContentType.JSON else None,
                headers=headers,
            )

        except aiohttp.ClientResponseError as ex:
            raise exceptions.ResponseError(ex.request_info, ex.status, ex.headers)

        except aiohttp.ClientError as ex:
            raise exceptions.RequestError()

        else:
            async with response:
                status = response.status
                headers = response.headers
                body = await response.json() if response.content_type == ContentType.JSON else None
                request_info = response.request_info

        if 401 <= status:
            raise exceptions.ResponseError(request_info, status, headers)

        return status, headers, body

    # Porfolio Service Group
    port_get_positions_positionid = partialmethod(openapi_request, Endpoint.PORT_POSITIONS)
    port_post_closedpositions_subscription = partialmethod(openapi_request, Endpoint.PORT_POST_CLOSEDPOSITIONS_SUBSCRIPTION)
    port_patch_closedpositions_subscription = partialmethod(openapi_request, Endpoint.PORT_PATCH_CLOSEDPOSITIONS_SUBSCRIPTION)
    port_delete_closedpositions_subscription = partialmethod(openapi_request, Endpoint.PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION)


sx = UserSession(None, None, None)
