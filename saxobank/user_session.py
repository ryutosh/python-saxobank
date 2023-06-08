from __future__ import annotations

from datetime import datetime
from functools import partialmethod
from typing import Optional
from urllib.parse import urljoin

import aiohttp

from . import exception
from .endpoint import ContentType, Dimension, Endpoint, EndpointDefinition, HttpMethod
from .environment import RestBaseUrl
from .model.common import SaxobankModel


class RateLimiter:
    async def throttle(
        self, dimension: Optional[Dimension] = None, is_order: bool = False, effectual_until: Optional[datetime] = None
    ):
        pass


# p = Endpoint.P1
print(dir(Endpoint))


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
        endpoint: Endpoint,
        request_model: SaxobankModel | None = None,
        effectual_until: datetime | None = None,
        access_token: str | None = None,
    ):
        url = urljoin(self.base_url, endpoint.url(request_model.path_items() if request_model else None))
        req_data = request_model.dict(exclude_unset=True) if request_model else None
        params = req_data if endpoint.method == HttpMethod.GET else None
        data = req_data if endpoint.method != HttpMethod.GET else None

        await self.limiter.throttle(endpoint.dimension, endpoint.is_order, effectual_until)

        try:
            response = await self.http.request(
                endpoint.method,
                url,
                params=params,
                data=data if endpoint.content_type != ContentType.JSON else None,
                json=data if endpoint.content_type == ContentType.JSON else None,
                headers={"Authorization": f"Bearer {access_token if access_token else self.token}"},
            )

        except aiohttp.ClientResponseError as ex:
            raise exception.ResponseError(ex.request_info, ex.status, ex.headers)

        except aiohttp.ClientError as ex:
            raise exception.RequestError(ex)

        else:
            async with response:
                status = response.status
                headers = response.headers
                body = await response.json() if response.content_type == ContentType.JSON else None
                request_info = response.request_info

        if 401 <= status:
            raise exception.ResponseError(request_info, status, headers)

        return status, headers, body

    # Porfolio Service Group
    port_get_clients_me = partialmethod(openapi_request, Endpoint.P1)
    port_get_positions_positionid = partialmethod(openapi_request, Endpoint.PORT_GET_POSITIONS_POSITION_ID)
    port_post_closedpositions_subscription = partialmethod(openapi_request, Endpoint.PORT_POST_CLOSEDPOSITIONS_SUBSCRIPTION)
    port_patch_closedpositions_subscription = partialmethod(openapi_request, Endpoint.PORT_PATCH_CLOSEDPOSITIONS_SUBSCRIPTION)
    port_delete_closedpositions_subscription = partialmethod(openapi_request, Endpoint.PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION)
