import abc
import json

# from abc import ABC
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import aiohttp
from api_call import Dispatcher
from endpoint import Endpoint
from environment import WsBaseUrl

from saxobank.models.common import ContextId, ReferenceId
from saxobank.models.core import StreamingwsAuthorizeReq, StreamingwsConnectReq

from ..saxobank import models

# from subscription import BaseSubscription


@dataclass(frozen=True)
class DataMessageLayout:
    INDEX: int
    SIZE: int


class DataMessage:
    MESSAGE_ID = DataMessageLayout(0, 8)
    REF_ID_SIZE = DataMessageLayout(10, 1)
    REF_ID = DataMessageLayout(11, 0)
    PAYLOAD_FORMAT = DataMessageLayout(11, 1)
    PAYLOAD_SIZE = DataMessageLayout(12, 4)
    PAYLOAD = DataMessageLayout(16, 0)

    def __init__(self, message: bytes) -> None:
        self.message_id, self.reference_id, self.payload = self.parse_message(message)
        self.is_control = bool(self.reference_id[0] == "_")

    @staticmethod
    def _parse_int(bytes: bytes, index: int, size: int) -> int:
        return int.from_bytes(bytes[index : index + size], "little")

    @staticmethod
    def _parse_json(bytes: bytes, index: int, size: int) -> Any:
        return json.loads(bytes[index : index + size].decode("utf-8", "strict"))

    @staticmethod
    def _parse_str(bytes: bytes, index: int, size: int) -> str:
        return bytes[index : index + size].decode("ascii", "strict")

    @classmethod
    def parse_message(cls, message: bytes):
        # Message ID
        message_id = cls._parse_int(message, cls.MESSAGE_ID.INDEX, cls.MESSAGE_ID.SIZE)

        # Reference id size
        ref_id_size = cls._parse_int(message, cls.REF_ID_SIZE.INDEX, cls.REF_ID_SIZE.SIZE)

        # Reference id
        # reference_id = data[11:11+ref_id_size].decode("ascii", "strict")
        reference_id = cls._parse_str(message, cls.REF_ID.INDEX, cls.REF_ID.SIZE + ref_id_size)

        # Payload Format
        # payload_fmt = int.from_bytes(data[11+ref_id_size:12+ref_id_size], "little")
        payload_fmt = cls._parse_int(message, cls.PAYLOAD_FORMAT.INDEX + ref_id_size, cls.PAYLOAD_FORMAT.SIZE)

        # Payload Size
        payload_size = cls._parse_int(message, cls.PAYLOAD_SIZE.INDEX + ref_id_size, cls.PAYLOAD_SIZE.SIZE)

        # Payload
        # TODO: else(Binary Proto Bufer Message) is not implemented
        payload = cls._parse_json(message, cls.PAYLOAD.INDEX + payload_size, cls.PAYLOAD.SIZE) if payload_fmt == 0 else None

        return message_id, ReferenceId(reference_id), payload


class Streaming:
    def __init__(self, ws_resp: aiohttp.ClientWebSocketResponse):
        self.ws_resp = ws_resp

    # NEED ITERETOR

    async def receive(self) -> DataMessage:
        return DataMessage(await self.ws_resp.receive_bytes())


class StreamingSession:
    WS_AUTHORIZE_URL: str = "authorize"
    WS_CONNECT_URL: str = "connect"

    # def __init__(self, ws_client: aiohttp.ClientSession, context_id: ContextId) -> None:
    #     self.ws_client = ws_client
    #     self.context_id = context_id
    #     self.ws_stream = None

    # async def connect(self, access_token: str | None = None, message_id: int | None = None):
    #     params = StreamingwsConnectReq(contextid=self.context_id, messageid=message_id).dict()
    #     self.ws_stream = await self.ws_client.ws_connect(self.WS_CONNECT_URL, params=params)
    #     return self.ws_stream

    def __init__(
        self,
        ws_client: aiohttp.ClientSession,
        context_id: ContextId,
        access_token: str | None = None,
        message_id: int | None = None,
    ) -> None:
        self.ws_client = ws_client
        self.context_id = context_id
        self.access_token = access_token
        self.message_id = message_id
        self.ws_stream = None

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.disconnect(self)

    async def connect(self) -> Streaming:
        params = StreamingwsConnectReq(contextid=self.context_id, messageid=self.message_id).dict()
        return Streaming(await self.ws_client.ws_connect(self.WS_CONNECT_URL, params=params))

    __aenter__ = connect

    async def disconnect(self) -> bool:
        assert self.ws_stream
        return self.ws_stream.close()

    async def reauthorize(self, access_token: str):
        params = StreamingwsAuthorizeReq(contextid=self.context_id).dict()
        _ = await self.ws_client.put(self.WS_AUTHORIZE_URL, params=params)


class ContextManager:
    def __init__(self, context_manager: ContextManager) -> None:
        self.ctxt = context_manager
        self.subscripions = []

    async def chart_subscription(self, arguments) -> Subscription:
        subscription = Subscription(self, entry_url, exit_url, arguments)
        self.subscriptions.append(subscription)
        if not run:
            loop.run(self.run())
        return subscription

    async def run(self):
        async with self.streaming_session as streaming:
            async for data_message in streaming:
                if data_message.is_control():
                    if instanceof(data_message, DisconnectMessage):
                        self.streaming_session = StreamingSession(self.ws_client, self.context_id)
                        streaming = await self.streaming_session.connect(last_message_id)

                    if instanceof(data_message, ResetSubscriptionMessage):
                        self.subscripions(data_message.old_ref_id).reset_subscription(new_ref_id)

                else:
                    await subscriptions[data_message.reference_id].put(data_message.payload)
                    self.last_message_id = data_message.message_id


class Subscription:
    def __init__(self, queue: Queue, http_client: aiohttp.ClientSession, context_id: str, reference_id: str):
        self.queue = queue
        self.ctxt_id = context_id
        self.ref_id = reference_id

    async def __enter__(self):
        self.create()
        yield await self.queue.pop()

    async def __exit__(self):
        self.remove()

    async def create(self):
        self.http_client.request(self.entry_url)

    async def reset(self, reference_id):
        self.http_client.request(self.entry_url, self.referece_id, reference_id)
        self.reference_id = reference_id

    async def remove(self):
        self.http_client.request(self.exit_url)
