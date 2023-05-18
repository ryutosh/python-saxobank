from datetime import datetime
from typing import Optional

import aiohttp
import simplejson as json
from api_call import Dispatcher
from authorization import Token
from endpoint import Endpoint, EndpointDefinition
from environment import RestBaseUrl, WsBaseUrl
from streaming_session import StreamingSession

from saxobank.models import OrdersRequest, OrdersResponse, SaxobankModel
from saxobank.models.common import ContextId


class RateLimiter:
    pass


class UserSession:
    def __init__(self, rest_base_url: RestBaseUrl, token: Token, rate_limiter: RateLimiter):
        self.client_session = aiohttp.ClientSession(base_url=rest_base_url, json_serialize=json.dumps)
        self.token = token
        self.rate_limiter = rate_limiter

    async def _boiler(self, endpoint: EndpointDefinition, request_model: SaxobankModel):
        pass

    def create_streaming(self, context_id: ContextId, ws_base_url: WsBaseUrl):
        self.streaming_session = StreamingSession(context_id, ws_base_url, self.client_session.connector)
        return self.streaming_session

    async def place_new_orders(
        self, request_model: OrdersRequest, effectual_until: Optional[datetime] = None, access_token: Optional[str] = None
    ) -> OrdersResponse:
        access_token = access_token if access_token else await self.token.get_token()

        await self.rate_limiter(Endpoint.TRADE_ORDERS.dimension, Throttle(endpoint.is_order)).throttle(effectual_until)

    # async def create_subscription(self, subscription_id: int, endpoint: Endpoint, args):
    #     return await self.streaming_session.create_subscription(subscription_id, endpoint, args)
