import aiohttp
from api_call import Dispatcher
from endpoint import Endpoint
# from abc import ABC
import uuid
from ..saxobank import models
import abc

class BaseSubscription(abc.ABC):
    create_subscription_endpoint: Endpoint
    remove_subscription_endpoint: Endpoint

    def __init__(self, context_id: str, reference_id: str, dispatcher: Dispatcher) -> None:
        self.context_id = context_id
        self.reference_id = reference_id
        self.dispatcher = dispatcher
    
    async def create(self, arguments: Optional[dict] = None):
        # has argument necessary case :  https://www.developer.saxo/openapi/referencedocs/trade/v1/infoprices/addsubscriptionasync/b0ffda941b3291f3dd9319673cc88403
        #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/optionschain/addsubscriptionasync/8ff796d4153fb5ae1dbce9ebf2d48b82
        #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/prices/addsubscriptionasync/e1dbfa7d3e2ef801a7c4ade9e57f8812
        #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/prices/addmultilegpricessubscriptionasync/7251ff94a91106a3b60a4d17df574694
        params = models.CreateSubscriptionRequest(
            ContextId = self.context_id,
            ReferenceId = self.reference_id,
            Format = 'application/json',
            Arguments = arguments
        ).dict(exclude_unset=True, exclude_none=True)

        return await self.dispatcher.request_endpoint(create_subscription_endpoint, params)

    async def remove(self):
        params = models.RemoveSubscriptionRequest(
            ContextId = self.context_id,
            ReferenceId = self.reference_id
        ).dict()

        return await self.dispatcher.request_endpoint(remove_subscription_endpoint, params)

    async def remove_multiple(self):
        pass
        # has not supported case:  https://www.developer.saxo/openapi/referencedocs/root/v1/sessions/addsubscription/12fcebb834c04dfbb0ff6b6a3a87a0df
        #                          https://www.developer.saxo/openapi/referencedocs/trade/v1/optionschain


    # async def put(self, data_message):
    #     await self.queue.put(data_message)

    # async def get(self):
    #     return await self.queue.get()


class Subscriptions:

    def __call__(self, *reference_id=None):
        if reference_id is not None:
            return first(self.subscriptions, key=reference_id, value=reference_id)



class DataMessage:
    message_layout = [
        (0, _parse_int),  # Message ID
        (8, None),        # Reserved
        (10, _parse_int), # Reference ID Size
        (11, _parse_str), # Reference ID
        (11, _parse_int), # Payload Format
        (12, _parse_int), # Payload Size
        (16, _parse_json) # Payload
    ]

    def __init__(self, data):
        self.data = data



    
    @staticmethod
    def parse_message(data):


        parseMessages = []
        idx = 0
        nxt = 0
        data_len = len(data)
        logger.debug(f'data_len: {data_len}')

        # Message ID
        idx = nxt
        nxt = idx + 8
        self.message_id = int.from_bytes(data[idx:nxt], 'little')

        # Reserved field: Not used now
        idx = nxt
        nxt = idx + 2

        # Reference id size
        idx = nxt
        nxt = idx + 1
        ref_id_size = int.from_bytes(data[idx:nxt], 'little')

        # Reference id
        idx = nxt
        nxt = idx + ref_id_size
        self.reference_id = data[idx:nxt].decode('ascii', 'strict')

        # Payload Format
        idx = nxt
        nxt = idx + 1
        payload_fmt = int.from_bytes(data[idx:nxt], 'little')

        # Payload Size
        idx = nxt
        nxt = idx + 4
        payload_size = int.from_bytes(data[idx:nxt], 'little')

        # Payload
        idx = nxt
        nxt = idx + payload_size

        # payload
        # TODO: else(Binary Proto Bufer Message) is not implemented
        payload = json.loads(data[idx:nxt].decode('utf-8', 'strict')) if payload_fmt == 0 else None
        logger.debug(f'payload: {payload}')

        parseMessages.append({
            'message_id': message_id,
            'reference_id': ref_id,
            'payload': payload,
        })

    def _parse_int(cls, begin: int, end: int):
        int.from_bytes(bytes, byteorder)



    

class StreamingSession:
    WS_CONNECT_URL: str = 'connect'

    def __init__(self, context_id: str, dispatcher: Dispatcher) -> None:
        self.context_id = context_id
        self.dispatcher = dispatcher

        self.subscriptions = Subscriptions()

    def _create_websocket_connect_request(self) -> dict:
        return models.CreateWebSocketConnectRequest(
            ContextId = self.context_id
        ).dict()

    async def create_subscription(self, subscription_class: BaseSubscription, reference_id: str, arguments: Optional[dict] = None) -> Subscription:
        subscription = subscription_class(self.context_id, reference_id, self.dispatcher)

        try:
            response = await self.subscription.create(arguments)
        else:
            subscription.set_snapshot(response.Snapshot)
            self.subscriptions.append(subscription)
            return subscription

    async def connect(self):
        params = self._create_websocket_connect_request()
        async with self.dispatcher.request_ws(self.WS_CONNECT_URL, params=params) as response:
            while True:
                data_message = DataMessage(await response.read())
                if data_message.is_control():
                    if instanceof (data_message, ResetSubscriptionMessage):
                        pass

                else
                    subscriptions.put(data_message)
                    self.last_message_id = data_message.message_id

    async def remove_subscription(self, subscription_class: BaseSubscription, reference_id: str):
        pass    


