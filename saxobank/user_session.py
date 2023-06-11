from __future__ import annotations

from collections import namedtuple
from collections.abc import Coroutine
from datetime import datetime
from functools import partial
from typing import Any, Optional, Tuple
from urllib.parse import urljoin

import aiohttp
import pydantic

from . import endpoint, exception
from .endpoint import ContentType, Dimension, HttpMethod
from .environment import RestBaseUrl
from .model.common import ErrorResponse, ODataResponse, ResponseCode, SaxobankModel
from .service_group import _Portfolio, _Reference, _Root

# from functools import partialmethod


class RateLimiter:
    async def throttle(
        self, dimension: Optional[Dimension] = None, is_order: bool = False, effectual_until: Optional[datetime] = None
    ):
        pass


class UserSession:
    # _http_responses_exceptions: Final[dict] = {
    #     401: exception.RequestUnauthorizedError,
    #     403: exception.RequestForbiddenError,
    #     404: exception.RequestNotFoundError,
    #     429: exception.TooManyRequestsError,
    #     500: exception.SaxobankServiceError,
    #     503: exception.SaxobankServiceUnavailableError,
    # }
    _OpenApiRequestResponse = namedtuple("_OpenApiRequestResponse", ["code", "model", "next_request"])

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

        self.port = _Portfolio(self)
        self.ref = _Reference(self)
        self.root = _Root(self)

    async def openapi_request(
        self,
        endpoint: endpoint.Endpoint,
        request_model: SaxobankModel | None = None,
        effectual_until: datetime | None = None,
        access_token: str | None = None,
    ) -> Tuple[ResponseCode, Optional[SaxobankModel], Optional[Coroutine]]:
        url = urljoin(self.base_url, endpoint.url(request_model.path_items() if request_model else None))
        params = request_model.dict_lower_case() if request_model and endpoint.method == HttpMethod.GET else None
        data = request_model.dict() if request_model and endpoint.method != HttpMethod.GET else None

        # req_data = request_model.dict(exclude_unset=True, by_alias=True) if request_model else None
        # params = req_data if endpoint.method == HttpMethod.GET else None
        # data = req_data if endpoint.method != HttpMethod.GET else None

        await self.limiter.throttle(endpoint.dimension, endpoint.is_order, effectual_until)

        try:
            async with self.http.request(
                endpoint.method,
                url,
                params=params,
                data=data if endpoint.content_type != ContentType.JSON else None,
                json=data if endpoint.content_type == ContentType.JSON else None,
                headers={"Authorization": f"Bearer {access_token if access_token else self.token}"},
                raise_for_status=False,
            ) as response:
                info = response.request_info
                code = ResponseCode(response.status)
                json = await response.json() if response.content_type == ContentType.JSON else None

            if error_response := self.error_response(code, json):
                return self._OpenApiRequestResponse(code, error_response, None)

            response_model = endpoint.response_model.parse_obj(json) if endpoint.response_model else None
            is_odata, next_callback = self.is_odata_response(response_model)

            return self._OpenApiRequestResponse(code, response_model.Data if is_odata else response_model, next_callback)

        except aiohttp.ClientResponseError as ex:
            raise exception.ResponseError(ex.status, ex.message)

        except aiohttp.InvalidURL as ex:
            raise exception.InternalError(f"Invalid URL: {ex.url}")

        except (aiohttp.ClientConnectionError, aiohttp.ClientPayloadError) as ex:
            raise exception.HttpClientError(str(ex))

        except pydantic.ValidationError as ex:
            print(str(info))
            raise exception.InternalError(str(ex) + f"\r\nResponce was: {json}")

    @classmethod
    def error_response(cls, code: ResponseCode, json: Optional[Any] = None) -> Optional[ErrorResponse]:
        if code != ResponseCode.BAD_REQUEST or not json:
            return None

        try:
            return ErrorResponse.parse_obj(json)
        except pydantic.ValidationError:
            return None

    def is_odata_response(self, response_model: Optional[SaxobankModel]) -> Tuple[bool, Optional[Coroutine]]:
        if not isinstance(response_model, ODataResponse):
            return False, None

        if not (next := response_model.next_request):
            return True, None

        if not (next_endpoint := endpoint.Endpoint.match(next.path)):
            raise exception.InternalError(f"Next endpoint for {next.path} not found.")

        next_request_model = next_endpoint.request_model.parse_obj(next.query)
        return True, partial(self.openapi_request, next_endpoint, next_request_model)
