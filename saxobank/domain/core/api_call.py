from endpoint import Endpoint, HttpMethod

from datetime import datetime  # , timedelta, timezone
from typing import Optional
from environment import RestBaseUrl, WsBaseUrl
import aiohttp

# import asyncio
import logging
import simplejson as json
import urllib.parse

# from multidict import CIMultiDictProxy
from authorization import Token

logger = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, connector: aiohttp.TCPConnector, rest_base_url: RestBaseUrl, ws_base_url: WsBaseUrl, token: Token):
        self.client_session = aiohttp.ClientSession(connector=connector, json_serialize=json.dumps, connector_owner=False)
        self.rest_base_url = rest_base_url
        self.ws_base_url = ws_base_url
        self.token = token

    async def request_endpoint(
        self, endpoint: Endpoint, params: Optional[dict] = None, effectual_until: Optional[datetime] = None
    ):
        pass

    async def request(
        self, url: str, method: HttpMethod, params: Optional[dict] = None, effectual_until: Optional[datetime] = None
    ):
        pass

    async def request_ws(self, url: str, params: Optional[dict] = None) -> aiohttp.ClientWebSocketResponse:
        return await self.client_session.ws_connect(urllib.parse.urljoin(self.ws_base_url, url), params=params)
