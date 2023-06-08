from __future__ import annotations

import logging
from typing import Optional

import simplejson
from aiohttp import ClientSession

from .environment import SaxobankEnvironment
from .model.common import ContextId
from .streaming_session import StreamingSession
from .user_session import RateLimiter, UserSession

# from environment import Environment

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Application:
    def __init__(self, saxobank_environment: SaxobankEnvironment, application_key, application_secret):
        self.saxo_env = saxobank_environment
        self.app_key = application_key
        self.app_secret = application_secret
        self.limiter = RateLimiter()

    def create_session(self, access_token: Optional[str] = None) -> SessionFacade:
        client_session = ClientSession(json_serialize=simplejson.dumps)
        user_session = UserSession(self.saxo_env.rest_base_url, client_session, self.limiter, access_token)
        # return SessionFacade(rest_base_url, ws_base_url, access_token)
        return SessionFacade(user_session)


class SessionFacade:
    # def __init__(self, rest_base_url, ws_base_url, access_token: Optional[str] = None) -> None:
    #     client_session = ClientSession(json_serialize=simplejson.dumps)
    #     self.user_session = UserSession(self.rest_base_url, client_session, self.limiter, access_token)

    def __init__(self, user_session: UserSession) -> None:
        self.__user_session = user_session
        self.port = self.__Portfolio(
            self.__user_session.base_url, self.__user_session.http, self.__user_session.limiter, self.__user_session.token
        )

    def create_streaming(self, context_id: Optional[ContextId] = None) -> StreamingSession:
        streaming_session = StreamingSession(self.__user_session, self.__user_session.http, context_id)
        return streaming_session

    class __Portfolio:
        __init__ = UserSession.__init__
        get_positions_positionid = UserSession.port_get_positions_positionid
        post_closedpositions_subscription = UserSession.port_post_closedpositions_subscription
        patch_closedpositions_subscription = UserSession.port_patch_closedpositions_subscription
        delete_closedpositions_subscription = UserSession.port_delete_closedpositions_subscription
