import asyncio
import json
from collections import UserDict
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Literal, Optional
from urllib.parse import urljoin

import aiohttp

# from api_call import Dispatcher
from . import endpoint, exception
from .enum import HeartbeatReason
from .environment import WsBaseUrl
from .model import streaming as model_streaming
from .model.common import ContextId, ReferenceId, SaxobankModel
from .subscription import Subscriptions

# from .subscription import PortClosedPositions
from .user_session import UserSession

# from subscription import BaseSubscription


@dataclass(frozen=True)
class _DataMessageLayout:
    INDEX: int
    SIZE: int


class DataMessage:
    __LAYOUT_MESSAGE_ID = _DataMessageLayout(0, 8)
    __LAYOUT_REF_ID_SIZE = _DataMessageLayout(10, 1)
    __LAYOUT_REF_ID = _DataMessageLayout(11, 0)
    __LAYOUT_PAYLOAD_FORMAT = _DataMessageLayout(11, 1)
    __LAYOUT_PAYLOAD_SIZE = _DataMessageLayout(12, 4)
    __LAYOUT_PAYLOAD = _DataMessageLayout(16, 0)

    __BYTEORDER: Literal["little", "big"] = "little"
    __DECODE_ERROR = "strict"
    __ENCODING_ASCII = "ascii"
    __ENCODING_UTF8 = "utf-8"

    __PAYLOAD_FORMAT_JSON = 0

    def __init__(self, message: bytes) -> None:
        self.message = message

    @classmethod
    @lru_cache
    def __parse_int(cls, b: bytes) -> int:
        return int.from_bytes(b, cls.__BYTEORDER)

    @classmethod
    def __parse_json(cls, b: bytes) -> Any:
        return json.loads(b.decode(cls.__ENCODING_UTF8, cls.__DECODE_ERROR))

    @classmethod
    @lru_cache
    def __parse_str(cls, b: bytes) -> str:
        return b.decode(cls.__ENCODING_ASCII, cls.__DECODE_ERROR)

    @classmethod
    def __cut(cls, bytes: bytes, index: int, size: int) -> bytes:
        return bytes[index : index + size]

    @property
    def __payload_size(self) -> int:
        return self.__parse_int(
            self.__cut(
                self.message, self.__LAYOUT_PAYLOAD_SIZE.INDEX + self.__reference_id_size, self.__LAYOUT_PAYLOAD_SIZE.SIZE
            )
        )

    @property
    def __reference_id_size(self) -> int:
        return self.__parse_int(self.__cut(self.message, self.__LAYOUT_REF_ID_SIZE.INDEX, self.__LAYOUT_REF_ID_SIZE.SIZE))

    @property
    def message_id(self) -> int:
        return self.__parse_int(self.__cut(self.message, self.__LAYOUT_MESSAGE_ID.INDEX, self.__LAYOUT_MESSAGE_ID.SIZE))

    @property
    def payload(self) -> Any:
        return (
            self.__parse_json(
                self.__cut(self.message, self.__LAYOUT_PAYLOAD.INDEX + self.__payload_size, self.__LAYOUT_PAYLOAD.SIZE)
            )
            if self.payload_fmt == self.__PAYLOAD_FORMAT_JSON
            else None  # ProtoBuf(Not supported because un-documented at Saxobank.)
        )

    @property
    def payload_fmt(self) -> int:
        return self.__parse_int(
            self.__cut(
                self.message, self.__LAYOUT_PAYLOAD_FORMAT.INDEX + self.__reference_id_size, self.__LAYOUT_PAYLOAD_FORMAT.SIZE
            )
        )

    @property
    def reference_id(self) -> str:
        return self.__parse_str(
            self.__cut(self.message, self.__LAYOUT_REF_ID.INDEX, self.__LAYOUT_REF_ID.SIZE + self.__reference_id_size)
        )


class Streaming:
    _REF_ID_HEARTBEAT = "_heartbeat"
    _REF_ID_RESETSUBSCRIPTIONS = "_resetsubscriptions"
    _REF_ID_DISCONNECT = "_disconnect"

    def __init__(
        self, ws_resp: aiohttp.ClientWebSocketResponse, subscriptions: Subscriptions, raise_if_stream_error: bool = False
    ):
        self._ws_resp = ws_resp
        self._raise_error = raise_if_stream_error
        self._subscriptions = subscriptions

    def __aiter__(self):
        return self

    def _return_or_raise_error(self, error: Exception):
        if self._raise_error:
            raise error
        return error

    @property
    def _empty(self) -> bool:
        return len(self._ws_resp._reader) == 0

    async def receive(self) -> DataMessage:
        while True:
            timestamp_of_empty = datetime.now(tz=timezone.utc)

            if self._empty:
                timeout_subscriptions = self._subscriptions.timeouts(timestamp_of_empty)
                if timeout_subscriptions:
                    return self._return_or_raise_error(
                        exception.SubscriptionTimeoutError(
                            [subscription.reference_id for subscription in timeout_subscriptions]
                        )
                    )

            message = DataMessage(await self._ws_resp.receive_bytes())
            ref_id = message.reference_id
            payload = message.payload

            if ref_id == self._REF_ID_HEARTBEAT:
                heartbeat = model_streaming.ResHeartbeat.parse_obj(payload)
                self._subscriptions.heartbeats([heartbeat.OriginatingReferenceId for heartbeat in heartbeat.Heartbeats])

                heartbeat_unavailables = heartbeat.filter_reasons([HeartbeatReason.SubscriptionPermanentlyDisabled])
                if heartbeat_unavailables:
                    unavailable_ref_ids = [heartbeat.OriginatingReferenceId for heartbeat in heartbeat_unavailables]
                    self._subscriptions.remove(unavailable_ref_ids)
                    return self._return_or_raise_error(exception.SubscriptionPermanentlyDisabledError(unavailable_ref_ids))

            elif ref_id == self._REF_ID_RESETSUBSCRIPTIONS:
                reset_subscriptions = model_streaming.ResResetSubscriptions.parse_obj(payload)
                unavailable_ref_ids = (
                    reset_subscriptions.TargetReferenceIds
                    if reset_subscriptions.TargetReferenceIds
                    else list(self._subscriptions.reference_ids())
                )
                self._subscriptions.remove(unavailable_ref_ids)
                return self._return_or_raise_error(exception.ResetSubscriptionsError(unavailable_ref_ids))

            elif ref_id == self._REF_ID_DISCONNECT:
                return self._return_or_raise_error(exception.StreamingDisconnectError())

            subscription = self._subscriptions.get(ReferenceId(ref_id), None)
            if not subscription:
                continue

            await subscription.apply_delta(subscription.delta_model.parse_obj(payload))
            subscription.heartbeats()

            return await subscription.message()

    async def __anext__(self):
        if self.ws_resp.closed:
            raise StopAsyncIteration
        return await self.receive()

    async def __aenter__(self):
        return self

    async def disconnect(self) -> bool:
        return await self._ws_resp.close()

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self.disconnect()


# class Distributor:
#     def __init__(self, streaming: Streaming, max_message_size=None):
#         self._streaming = streaming

#     def stream(self, reference_id: ReferenceId):
#         pass

#     async def distribute(self, on_error=None, on_disconnect=None):
#         while True:
#             async for message in self.streaming:
#                 pass


class StreamingSession:
    WS_AUTHORIZE_PATH: str = "authorize"
    WS_CONNECT_PATH: str = "connect"

    def __init__(
        self,
        ws_base_url: WsBaseUrl,
        user_session: UserSession,
        ws_client: aiohttp.ClientSession,
        context_id: Optional[ContextId] = None,
        access_token: Optional[str] = None,
    ) -> None:
        self.auth_url = urljoin(ws_base_url, self.WS_AUTHORIZE_PATH)
        self.connect_url = urljoin(ws_base_url, self.WS_CONNECT_PATH)
        self.user_session = user_session
        self.ws_client = ws_client
        self.context_id = context_id if context_id else ContextId()
        self.access_token = access_token
        self._subscriptions = Subscriptions()
        self._streaming: Optional[Streaming] = None

    async def connect(self, message_id: Optional[int] = None, access_token: Optional[str] = None) -> Streaming:
        params = model_streaming.ReqConnect(contextid=self.context_id, messageid=message_id).as_request()
        self._streaming = Streaming(await self.ws_client.ws_connect(self.connect_url, params=params), self._subscriptions)

        return self._streaming

    # async def reauthorize(self, access_token: str):
    #     self.access_token = access_token
    #     params = StreamingwsAuthorizeReq(contextid=self.context_id).dict()
    #     _ = await self.ws_client.put(self.WS_AUTHORIZE_URL, params=params)

    async def chart_charts_subscription_post(
        self,
        reference_id: Optional[ReferenceId],
        arguments: Optional[SaxobankModel],
        replace_reference_id: Optional[ReferenceId],
        format: Optional[str],
        refresh_rate: Optional[int],
        tag: Optional[str],
    ):
        # assert self.streaming
        reference_id = reference_id

        subscription = ChartsSubscription(reference_id)
        self._subscriptions.append(subscription)

        req = endpoint.port.closed_positions.POST_SUBSCRIPTION.request_model(
            ContextId=self.context_id, ReferenceId=reference_id, Format=format, Arguments=arguments
        )

        res = await self.user_session.chart_charts_subscription_post(req)

        if hasattr(res.response_model, "InactivityTimeout"):
            subscription.set_timeout(res.response_model.Snapshot)

        is_odata, next_callback = self.user_session.is_odata_response(res.response_model)
        if is_odata:
            subscription.set_snapshot(res.response_model.Snapshot.Data)

        else:
            subscription.set_snapshot(res.response_model.Snapshot)

        return streamer, next_callback if is_odata else None

    # async def closedpositions_remove_multiple_subscriptions(self, arguments) -> SaxobankModel:
    #     req = Endpoint.PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION_CONTEXTID, RequestModel(
    #         ContextId=self.context_id, Arguments=arguments
    #     ).dict(exclude_unset=True, exclude_none=True)

    #     return await self.session.openapi_request(
    #         self.Endpoint.PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION_CONTEXTID, req, acess_token=access_token
    #     )


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
