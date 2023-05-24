import abc

# from abc import ABC
import uuid

import aiohttp
from api_call import Dispatcher
from endpoint import Endpoint
from environment import WsBaseUrl

from saxobank.models.common import ContextId

from ..saxobank import models

# from subscription import BaseSubscription


class DataMessage:
    message_layout = [
        (0, _parse_int),  # Message ID
        (8, None),  # Reserved
        (10, _parse_int),  # Reference ID Size
        (11, _parse_str),  # Reference ID
        (11, _parse_int),  # Payload Format
        (12, _parse_int),  # Payload Size
        (16, _parse_json),  # Payload
    ]

    def __init__(self, data):
        self.data = data

    @staticmethod
    def parse_message(data):
        parseMessages = []
        idx = 0
        nxt = 0
        data_len = len(data)
        logger.debug(f"data_len: {data_len}")

        # Message ID
        idx = nxt
        nxt = idx + 8
        self.message_id = int.from_bytes(data[idx:nxt], "little")

        # Reserved field: Not used now
        idx = nxt
        nxt = idx + 2

        # Reference id size
        idx = nxt
        nxt = idx + 1
        ref_id_size = int.from_bytes(data[idx:nxt], "little")

        # Reference id
        idx = nxt
        nxt = idx + ref_id_size
        self.reference_id = data[idx:nxt].decode("ascii", "strict")

        # Payload Format
        idx = nxt
        nxt = idx + 1
        payload_fmt = int.from_bytes(data[idx:nxt], "little")

        # Payload Size
        idx = nxt
        nxt = idx + 4
        payload_size = int.from_bytes(data[idx:nxt], "little")

        # Payload
        idx = nxt
        nxt = idx + payload_size

        # payload
        # TODO: else(Binary Proto Bufer Message) is not implemented
        payload = json.loads(data[idx:nxt].decode("utf-8", "strict")) if payload_fmt == 0 else None
        logger.debug(f"payload: {payload}")

        parseMessages.append(
            {
                "message_id": message_id,
                "reference_id": ref_id,
                "payload": payload,
            }
        )

    def _parse_int(cls, begin: int, end: int):
        int.from_bytes(bytes, byteorder)


class StreamingSession:
    WS_CONNECT_URL: str = "connect"

    def __init__(self, ws_client: aiohttp.ClientSession, context_id: ContextId) -> None:
        self.ws_client = ws_client
        self.context_id = context_id

    def _create_websocket_connect_request(self) -> dict:
        return models.RequestCreateWebSocketConnection(ContextId=self.context_id).dict()

    async def connect(self, access_token: str) -> ContextManager:
        params = self._create_websocket_connect_request()
        return await self.ws_client.ws_connect(self.WS_CONNECT_URL)

    async def disconnect(self):
        pass

    async def reauthorize(self, access_token: str):
        pass

    async def reconnect(self, access_token: str | None = None, last_message_id: int | None = None):
        pass



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

    def run(self):
        while True:
            data_message = DataMessage(await response.read())
            if data_message.is_control():
                if instanceof(data_message, ResetSubscriptionMessage):
                    self.subscripions(data_message.old_ref_id).reset_subscription(new_ref_id)

            else:
                subscriptions.put(data_message)
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

