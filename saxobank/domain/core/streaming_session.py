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

    # async def create_subscription(self, subscription_class: BaseSubscription, reference_id: str, arguments: Optional[dict] = None) -> Subscription:
    #     subscription = subscription_class(self.context_id, reference_id, self.dispatcher)

    #     try:
    #         response = await self.subscription.create(arguments)
    #     else:
    #         subscription.set_snapshot(response.Snapshot)
    #         self.subscriptions.append(subscription)
    #         return subscription

    async def connect(self):
        params = self._create_websocket_connect_request()
        async with self.dispatcher.request_ws(self.WS_CONNECT_URL, params=params) as response:
            while True:
                data_message = DataMessage(await response.read())
                if data_message.is_control():
                    if instanceof(data_message, ResetSubscriptionMessage):
                        pass

                else:
                    subscriptions.put(data_message)
                    self.last_message_id = data_message.message_id

    # async def remove_subscription(self, subscription_class: BaseSubscription, reference_id: str):
    #     pass
