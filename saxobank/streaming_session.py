import json

# from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache, partialmethod
from types import TracebackType
from typing import Any, Coroutine, Literal, Optional, Type, Union
from urllib.parse import urljoin

import aiohttp

# from api_call import Dispatcher
from . import endpoint, exception
from .common import auth_header
from .environment import WsBaseUrl
from .model import streaming as model_streaming
from .model.common import ContextId, ReferenceId, ResponseCode, _SaxobankModel
from .model.enum import HeartbeatReason
from .subscription import Subscription, Subscriptions

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
    @lru_cache()
    def __parse_int(cls, b: bytes) -> int:
        return int.from_bytes(b, cls.__BYTEORDER)

    @classmethod
    def __parse_json(cls, b: bytes) -> Any:
        return json.loads(b.decode(cls.__ENCODING_UTF8, cls.__DECODE_ERROR))

    @classmethod
    @lru_cache()
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
        self._subscriptions = subscriptions
        self._raise_error = raise_if_stream_error

    def __aiter__(self) -> "Streaming":
        return self

    def _return_or_raise(self, error: Exception) -> Exception:
        if self._raise_error:
            raise error
        return error

    @property
    def _empty(self) -> bool:
        return len(self._ws_resp._reader) == 0

    def _handle_reset_subscriptions(self, payload: Any) -> Exception:
        reset_subscriptions = model_streaming.ResResetSubscriptions.parse_obj(payload)

        if reset_subscriptions.TargetReferenceIds:
            self._subscriptions.remove_items(reference_ids=reset_subscriptions.TargetReferenceIds)
            return self._return_or_raise(exception.ResetSubscriptionsError(reset_subscriptions.TargetReferenceIds))

        # All reference ids are required to reset if no TargetReferenceIds set.
        need_resets = self._subscriptions.reference_ids()
        self._subscriptions.clear()
        return self._return_or_raise(exception.ResetSubscriptionsError(need_resets))

    async def receive(self) -> Union[_SaxobankModel, Exception]:
        while True:
            timestamp_of_empty = datetime.now(tz=timezone.utc)

            # Without any incoming data, subscriptions that passed inactivity timeout should be considred as invalid.
            if self._empty:
                timeouts = self._subscriptions.remove_timeouts(timestamp_of_empty)
                if timeouts:
                    return self._return_or_raise(exception.SubscriptionTimeoutError(timeouts))

            message = DataMessage(await self._ws_resp.receive_bytes())
            ref_id = message.reference_id
            payload = message.payload

            if ref_id == self._REF_ID_HEARTBEAT:
                heartbeat = model_streaming.ResHeartbeat.parse_obj(payload)
                self._subscriptions.extend_timeout([h.OriginatingReferenceId for h in heartbeat.Heartbeats])

                permanently_disables = heartbeat.filter_reasons([HeartbeatReason.SubscriptionPermanentlyDisabled])
                if permanently_disables:
                    self._subscriptions.remove_items(reference_ids=permanently_disables)
                    return self._return_or_raise(exception.SubscriptionPermanentlyDisabledError(permanently_disables))

            elif ref_id == self._REF_ID_RESETSUBSCRIPTIONS:
                return self._handle_reset_subscriptions(payload)

            elif ref_id == self._REF_ID_DISCONNECT:
                return self._return_or_raise(exception.StreamingDisconnectError())

            try:
                subscription = self._subscriptions.get(ref_id)
            except KeyError:
                # trash data message of Reference ID that's not under observation
                continue

            await subscription.wait_preparation()
            snapshot = subscription.apply_delta(payload)
            subscription.extend_timeout()

            if not snapshot:
                continue

            return snapshot

    async def __anext__(self) -> Union[_SaxobankModel, Exception]:
        if self._ws_resp.closed:
            raise StopAsyncIteration
        return await self.receive()

    async def __aenter__(self) -> "Streaming":
        return self

    async def disconnect(self) -> bool:
        return await self._ws_resp.close()

    async def __aexit__(
        self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> bool:
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


@dataclass(frozen=True)
class _CreateSubscriptionResponse:
    code: ResponseCode
    reference_id: Optional[ReferenceId] = None
    snapshot: Optional[_SaxobankModel] = None
    next_request: Optional[Coroutine] = None
    inactivity_timeout: Optional[int] = None
    format: Optional[int] = None
    refresh_rate: Optional[int] = None


class StreamingSession:
    WS_AUTHORIZE_PATH: str = "authorize"
    WS_CONNECT_PATH: str = "connect"

    def __init__(
        self,
        ws_base_url: WsBaseUrl,
        user_session: UserSession,
        ws_client: aiohttp.ClientSession,
        access_token: str,
        context_id: Optional[ContextId] = None,
    ) -> None:
        self._auth_url = urljoin(ws_base_url, self.WS_AUTHORIZE_PATH)
        self._connect_url = urljoin(ws_base_url, self.WS_CONNECT_PATH)
        self._user_session = user_session
        self._ws_client = ws_client
        self._context_id = context_id if context_id else ContextId()
        self.token = access_token
        self._subscriptions = Subscriptions()
        self._streaming: Optional[Streaming] = None

    async def connect(self, message_id: Optional[int] = None) -> Streaming:
        params = model_streaming.ReqConnect(contextid=self._context_id, messageid=message_id).as_request()
        headers = auth_header(self.token)

        self._streaming = Streaming(
            await self._ws_client.ws_connect(self._connect_url, params=params, headers=headers), self._subscriptions
        )

        return self._streaming

    async def reauthorize(self, access_token: str) -> bool:
        self.token = access_token
        headers = auth_header(self.token)
        params = model_streaming.ReqAuthorize(contextid=self._context_id).as_request()

        res = await self._ws_client.put(self._auth_url, params=params, headers=headers)
        return True if res.ok else False

    async def create_subscription_request(
        self,
        request_job: Coroutine,
        reference_id: Optional[ReferenceId],
        # format: Optional[str],
        # refresh_rate: Optional[int],
        tag: Optional[str],
        # replace_reference_id: Optional[ReferenceId],
        # arguments: Optional[SaxobankModel],
    ) -> _CreateSubscriptionResponse:
        # assert self.streaming
        if not reference_id:
            reference_id = ReferenceId()

        subscription = Subscription(reference_id, tag)
        self._subscriptions.add(subscription)

        # req = endpoint.CHART_CHARTS_SUBSCRIPTIONS_POST.request_model(
        #     ContextId=self.context_id,
        #     ReferenceId=reference_id,
        #     Format=format,
        #     RefreshRate=refresh_rate,
        #     Tag=tag,
        #     ReplaceReferenceId=replace_reference_id,
        #     Arguments=arguments,
        # )

        # res = await self._user_session.chart_charts_subscription_post(req)
        res = await request_job

        if res.code.is_error:
            self._subscriptions.discard(subscription)
            return _CreateSubscriptionResponse(res.code)

        is_odata, next_callback = self._user_session.is_odata_response(res.model)
        snapshot = res.model.Snapshot.Data if is_odata else res.model.Snapshot

        subscription._setup(res.model.InactivityTimeout, snapshot)

        # return streamer, next_callback if is_odata else None
        return _CreateSubscriptionResponse(res.code, reference_id, snapshot, next_callback, res.model.InactivityTimeout)

    async def chart_charts_subscription_post(
        self,
        reference_id: Optional[ReferenceId],
        tag: Optional[str],
        format: Optional[str],
        refresh_rate: Optional[int],
        replace_reference_id: Optional[ReferenceId],
        arguments: Optional[_SaxobankModel],
    ) -> _CreateSubscriptionResponse:
        req = endpoint.CHART_CHARTS_SUBSCRIPTIONS_POST.request_model(
            ContextId=self.context_id,
            ReferenceId=reference_id,
            Tag=tag,
            Format=format,
            RefreshRate=refresh_rate,
            ReplaceReferenceId=replace_reference_id,
            Arguments=arguments,
        )
        coro = self._user_session.chart_charts_subscription_post(req)
        return await self.create_subscription_request(coro, reference_id, tag)

    async def chart_charts_subscription_delete(self, reference_id):
        req = endpoint.CHART_CHARTS_SUBSCRIPTIONS_DELETE.request_model(ContextId=self.context_id, ReferenceId=reference_id)
        return await self._user_session.chart_charts_subscription_delete(req)

    # async def closedpositions_remove_multiple_subscriptions(self, arguments) -> SaxobankModel:
    #     req = Endpoint.PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION_CONTEXTID, RequestModel(
    #         ContextId=self.context_id, Arguments=arguments
    #     ).dict(exclude_unset=True, exclude_none=True)

    #     return await self.session.openapi_request(
    #         self.Endpoint.PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION_CONTEXTID, req, acess_token=access_token
    #     )
