import aiohttp
import simplejson as json
from api_call import Dispatcher
from authorization import Token
from endpoint import Endpoint
from environment import RestBaseUrl
from streaming_session import StreamingSession


class RateLimiter:
    pass


class UserSession:
    def __init__(self, rest_base_url: RestBaseUrl, token: Token, rate_limiter: RateLimiter):
        self.client_session = aiohttp.ClientSession(json_serialize=json.dumps)
        # self.dispatcher = Dispatcher(self.tcp_connector, rest_base_url)

    def create_streaming(self, context_id: str):
        self.streaming_session = StreamingSession(context_id, self.dispatcher)
        return self.streaming_session

    # async def create_subscription(self, subscription_id: int, endpoint: Endpoint, args):
    #     return await self.streaming_session.create_subscription(subscription_id, endpoint, args)


class UserSessions:
    """Collection object"""

    sessions = []
