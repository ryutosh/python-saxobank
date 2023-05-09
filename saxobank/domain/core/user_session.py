import aiohttp
from api_call import Dispatcher
from streaming_session import StreamingSession
from endpoint import Endpoint


class UserSession:
    def __init__(self, session_id, auth_url, rest_base_url, websocket_url, application_rate_limit):
        self.tcp_connector = aiohttp.TCPConnector()
        self.dispatcher = Dispatcher(self.tcp_connector, rest_base_url)
        self.streaming_session = StreamingSession(self.tcp_connector, self.dispatcher, websocket_url)

    async def refresh_token():
        self.streaming_session.reauth()

    def create_streaming_session(self, context_id: str):
        self.streaming_session = StreamingSession(context_id, self.dispatcher)
        return self.streaming_session

    # async def create_subscription(self, subscription_id: int, endpoint: Endpoint, args):
    #     return await self.streaming_session.create_subscription(subscription_id, endpoint, args)


class UserSessions:
    """Collection object"""

    sessions = []
