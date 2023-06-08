import abc
import asyncio
import json
import uuid
from collections import UserDict
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Literal, Optional

import aiohttp

from . import exception

# from api_call import Dispatcher
from .endpoint import Endpoint
from .environment import WsBaseUrl
from .model.common import ContextId, ReferenceId, SaxobankModel
from .model.core import (
    # DefinedReferenceId,
    StreamingwsAuthorizeReq,
    StreamingwsConnectReq,
    StreamingwsDisconnectRes,
    StreamingwsHeartbeatRes,
    StreamingwsResetSubscriptionsRes,
)
from .subscription import PortClosedPositions
from .user_session import UserSession

# from subscription import BaseSubscription


@dataclass(frozen=True)
class DataMessageLayout:
    INDEX: int
    SIZE: int


class DataMessage:
    __LAYOUT_MESSAGE_ID = DataMessageLayout(0, 8)
    __LAYOUT_REF_ID_SIZE = DataMessageLayout(10, 1)
    __LAYOUT_REF_ID = DataMessageLayout(11, 0)
    __LAYOUT_PAYLOAD_FORMAT = DataMessageLayout(11, 1)
    __LAYOUT_PAYLOAD_SIZE = DataMessageLayout(12, 4)
    __LAYOUT_PAYLOAD = DataMessageLayout(16, 0)

    __BYTEORDER: Literal["little", "big"] = "little"
    __DECODE_ERROR = "strict"
    __ENCODING_ASCII = "ascii"
    __ENCODING_UTF8 = "utf-8"

    def __init__(self, message: bytes) -> None:
        self.message = message
        # self.is_control = bool(self.reference_id[0] == "_")

    @classmethod
    def __parse_int(cls, bytes: bytes, index: int, size: int) -> int:
        return int.from_bytes(bytes[index : index + size], cls.__BYTEORDER)

    @classmethod
    def __parse_json(cls, bytes: bytes, index: int, size: int) -> Any:
        return json.loads(bytes[index : index + size].decode(cls.__ENCODING_UTF8, cls.__DECODE_ERROR))

    @classmethod
    def __parse_str(cls, bytes: bytes, index: int, size: int) -> str:
        return bytes[index : index + size].decode(cls.__ENCODING_ASCII, cls.__DECODE_ERROR)

    @lru_cache
    @property
    def __payload_size(self):
        return self.__parse_int(
            self.message, self.__LAYOUT_PAYLOAD_SIZE.INDEX + self.__reference_id_size, self.__LAYOUT_PAYLOAD_SIZE.SIZE
        )

    @lru_cache
    @property
    def __reference_id_size(self):
        return self.__parse_int(self.message, self.__LAYOUT_REF_ID_SIZE.INDEX, self.__LAYOUT_REF_ID_SIZE.SIZE)

    @lru_cache
    @property
    def is_control(self):
        return bool(self.reference_id[0] == "_")

    @lru_cache
    @property
    def message_id(self):
        return self.__parse_int(self.message, self.__LAYOUT_MESSAGE_ID.INDEX, self.__LAYOUT_MESSAGE_ID.SIZE)

    @lru_cache
    @property
    def payload(self):
        return (
            self.__parse_json(self.message, self.__LAYOUT_PAYLOAD.INDEX + self.__payload_size, self.__LAYOUT_PAYLOAD.SIZE)
            if self.payload_fmt == 0
            else None
        )

    @lru_cache
    @property
    def payload_fmt(self):
        return self.__parse_int(
            self.message, self.__LAYOUT_PAYLOAD_FORMAT.INDEX + self.__reference_id_size, self.__LAYOUT_PAYLOAD_FORMAT.SIZE
        )

    @lru_cache
    @property
    def reference_id(self):
        return self.__parse_str(self.message, self.__LAYOUT_REF_ID.INDEX, self.__LAYOUT_REF_ID.SIZE + self.__reference_id_size)


# class SubscriptionStreaming:
#     def __init__(self, queue: Queue, subscription: Subscription):
#         self.queue = queue
#         self.subscription = subscription

#     def __iter__(self):
#         yield await self.receive()

#     async def close(self):
#         await self.subscription.remove()

#     async def receive(self) -> DataMessage:
#         return await self.queue.get()


class Streaming:
    def __init__(self, ws_resp: aiohttp.ClientWebSocketResponse, streamers: Streamers):
        self.ws_resp = ws_resp

    async def __aiter__(self):
        yield await self.receive()

    async def close(self) -> bool:
        return await self.ws_resp.close()

    async def receive(self) -> DataMessage:
        return DataMessage(await self.ws_resp.receive_bytes())


class StreamingSession:
    WS_AUTHORIZE_URL: str = "authorize"
    WS_CONNECT_URL: str = "connect"

    def __init__(
        self,
        user_session: UserSession,
        ws_client: aiohttp.ClientSession,
        context_id: ContextId,
        access_token: Optional[str] = None,
        message_id: Optional[int] = None,
    ) -> None:
        self.user_session = user_session
        self.ws_client = ws_client
        self.context_id = context_id
        self.access_token = access_token
        self.message_id = message_id
        self.streamers = Streamers(self.context_id)
        self.streaming: Optional[Streaming] = None

    async def connect(self, access_token: Optional[str] = None) -> Streaming:
        params = StreamingwsConnectReq(contextid=self.context_id, messageid=self.message_id).dict()
        ws_stream = await self.ws_client.ws_connect(self.WS_CONNECT_URL, params=params)
        return Streaming(ws_stream, self.streamers)

    # __aenter__ = connect

    async def disconnect(self) -> bool:
        assert self.streaming
        return await self.streaming.close()

    # async def __aexit__(self, exc_type, exc_value, traceback):
    #     self.disconnect(self)

    async def service(self) -> None:
        try:
            self.streaming = await self.connect(access_token)
            async for data_message in self.streaming:
                if data_message.is_control:
                    pass
                else:
                    self.message_id = data_message.message_id
                    self.streamers[data_message.reference_id].put(data_message)

        except asyncio.CancelledError:
            pass

        finally:
            await self.disconnect()

    async def reauthorize(self, access_token: str):
        self.access_token = access_token
        params = StreamingwsAuthorizeReq(contextid=self.context_id).dict()
        _ = await self.ws_client.put(self.WS_AUTHORIZE_URL, params=params)

    # async def __create_subscription(self, reference_id: ReferenceId, arguments: SaxobankModel)
    async def closedpositions_subscription(self, reference_id: ReferenceId, arguments, format, refresh_rate) -> SaxobankModel:
        assert self.streaming
        req = Endpoint.PORT_POST_CLOSEDPOSITIONS_SUBSCRIPTION.RequestModel(
            ContextId=self.context_id, ReferenceId=reference_id, Format=format, Arguments=arguments
        ).dict(exclude_unset=True, exclude_none=True)

        res = await self.session.openapi_request(
            self.Endpoint.PORT_POST_CLOSEDPOSITIONS_SUBSCRIPTION, req, acess_token=access_token
        )

        # template add snapshot and timeout
        if hasattr(res, "Snapshot"):
            self.streamers[reference_id].set_snapshot(res.Snapshot)

    async def closedpositions_remove_multiple_subscriptions(self, arguments) -> SaxobankModel:
        req = Endpoint.PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION_CONTEXTID, RequestModel(
            ContextId=self.context_id, Arguments=arguments
        ).dict(exclude_unset=True, exclude_none=True)

        return await self.session.openapi_request(
            self.Endpoint.PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION_CONTEXTID, req, acess_token=access_token
        )

    def streamer(self, reference_id: ReferenceId, snapshot: SaxobankModel, timeout: int):
        streamer = self.streamers[reference_id]
        streamer.set_snapshot(snapshot)
        streamer.timeout = timeout
        return streamer

    # @asynccontextmanager
    # async def closedpositions_subscription(self, arguments):
    #     reference_id = ReferenceId()
    #     subscription = PortClosedPositions(self.user_session, self.context_id, reference_id)
    #     streamer = Streamer(self.context_id, reference_id, models.port.PositionResponse)
    #     self.streamers.append(streamer)

    #     try:
    #         ret = await subscription.create(arguments)
    #         await streamer.set_snapshot(ret.Snapshot)
    #         streamer.set_timeout(ret.InactivityTimeout)
    #         yield subscription, streamer

    #     finally:
    #         _ = await subscription.remove()
    #         self.streamers.remove(streamer)

    #     if not run:
    #         loop.run(self.connect())


class Streamers(UserDict):
    def __init__(self, context_id: ContextId):
        self.context_id = context_id
        super().__init__()

    def __missing__(self, key: ReferenceId):
        self[key] = streamer = Streamer(self.context_id, key)
        return streamer


class Streamer:
    def __init__(self, context_id: ContextId, reference_id: ReferenceId, minimum_inactivity_timeout: int = 2):
        self.context_id = context_id
        self.reference_id = reference_id
        self.minimum_timeout = minimum_inactivity_timeout

        self.data_messages = asyncio.Queue()
        self.snapshot: Union[SubscriptionSnapshotModel, ListResultModel] | None = None
        self.__timeout: int | None = None

    def __eq__(self, o: object) -> bool:
        assert isinstance(o, self.__class__)
        try:
            return (self.context_id == o.context_id) and (self.reference_id == o.reference_id)
        except AttributeError:
            return False

    async def put(self, data_message: DataMessage):
        await self.data_messages.put(data_message.payload)

    async def get(self) -> SaxobankModel:
        assert self.snapshot
        try:
            payload = await asyncio.wait_for(self.data_messages.get(), timeout=self.timeout)

        except TimeoutError:
            raise exception.TimeoutError()

        else:
            self.snapshot = self.snapshot.apply_delta(payload)
            self.data_messages.task_done()

            if not self.snapshot.message_complete():
                return await self.get()

            return self.snapshot

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, value):
        self.__timeout = max(value, self.minimum_timeout)


# class ContextManager:
#     def __init__(self, user_session: UserSession,  context_id: ContextId) -> None:
#         self.user_session = user_session
#         self.context_id = context_id
#         self.ctxt = context_manager
#         self.last_message_id
#         self.streaming_session: = None

#     def _handle_disconnect(self, control_message: StreamingwsDisconnectRes):
#         self.last_message_id = data_message.message_id

#     def _handle_heartbeat(self, control_message: StreamingwsHeartbeatRes):
#         self.last_message_id = data_message.message_id

#         if control_message.Heartbeats.Reason == SubscriptionPermanentlyDisabled:
#             pass

#     def _handle_reset_subscription(self, control_message: StreamingwsResetSubscriptionsRes):
#         for reference_id in control_message.TargetReferenceIds:
#             await self.subscripions[reference_id].remove()

#     async def run(self):
#         async with self.streaming_session as streaming:
#             async for data_message in streaming:
#                 if data_message.reference_id == DefinedReferenceId.Heartbeat:
#                     self._handle_heartbeat(StreamingwsHeartbeatRes.parse_obj(data_message.payload))

#                 elif data_message.reference_id == DefinedReferenceId.ResetSubscription:
#                     self._handle_reset_subscription(StreamingwsResetSubscriptionsRes.parse_obj(data_message.payload))

#                 elif data_message.reference_id == DefinedReferenceId.Disconnect:
#                     self.streaming_session = StreamingSession(self.ws_client, self.context_id)
#                     streaming = await self.streaming_session.connect(last_message_id)

#                 else:
#                     await subscriptions[data_message.reference_id].put(data_message.payload)
#                     self.last_message_id = data_message.message_id


# class Subscription:
#     def __init__(self, queue: Queue, http_client: aiohttp.ClientSession, context_id: str, reference_id: str):
#         self.queue = queue
#         self.ctxt_id = context_id
#         self.ref_id = reference_id

#     async def __enter__(self):
#         self.create()
#         yield await self.queue.pop()

#     async def __exit__(self):
#         self.remove()

#     async def create(self):
#         self.http_client.request(self.entry_url)

#     async def reset(self, reference_id):
#         self.http_client.request(self.entry_url, self.referece_id, reference_id)
#         self.reference_id = reference_id

#     async def remove(self):
#         self.http_client.request(self.exit_url)
