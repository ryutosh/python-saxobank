from __future__ import annotations

import abc

from api_call import Dispatcher
from endpoint import Endpoint
from streaming_session import StreamingSession
from user_session import UserSession

# from abc import ABC
from saxobank import models


class BaseSubscription(abc.ABC):
    FORMAT_JSON: str = "application/json"
    endpoint_create: Endpoint
    endpoint_remove: Endpoint
    endpoint_remove_multiple: Endpoint

    def __init__(self, reference_id: str, streaming_session: StreamingSession, dispatcher: Dispatcher) -> None:
        self.reference_id = reference_id
        self.streaming_session = streaming_session
        self.dispatcher = dispatcher

    async def create(self, arguments: dict | None = None):
        # has argument necessary case :  https://www.developer.saxo/openapi/referencedocs/trade/v1/infoprices/addsubscriptionasync/b0ffda941b3291f3dd9319673cc88403
        #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/optionschain/addsubscriptionasync/8ff796d4153fb5ae1dbce9ebf2d48b82
        #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/prices/addsubscriptionasync/e1dbfa7d3e2ef801a7c4ade9e57f8812
        #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/prices/addmultilegpricessubscriptionasync/7251ff94a91106a3b60a4d17df574694
        params = models.RequestCreateSubscription(
            ContextId=self.streaming_session.context_id,
            ReferenceId=self.reference_id,
            Format=self.FORMAT_JSON,
            Arguments=arguments,
        ).dict(exclude_unset=True, exclude_none=True)

        return await self.dispatcher.request_endpoint(self.endpoint_create, params)

    async def remove(self):
        params = models.RequestRemoveSubscription(
            ContextId=self.streaming_session.context_id, ReferenceId=self.reference_id
        ).dict()

        return await self.dispatcher.request_endpoint(self.endpoint_remove, params)

    async def remove_multiple(self):
        pass
        # has not supported case:  https://www.developer.saxo/openapi/referencedocs/root/v1/sessions/addsubscription/12fcebb834c04dfbb0ff6b6a3a87a0df
        #                          https://www.developer.saxo/openapi/referencedocs/trade/v1/optionschain

    # async def put(self, data_message):
    #     await self.queue.put(data_message)

    # async def get(self):
    #     return await self.queue.get()


class ChartSubscription(BaseSubscription):
    endpoint_create: Endpoint = Endpoint.CHART_CHARTS_SUBSCRIPTIONS
    endpoint_remove: Endpoint = Endpoint.CHART_CHARTS_SUBSCRIPTIONS_DELETE


# class Subscriptions:

#     def __call__(self, *reference_id=None):
#         if reference_id is not None:
#             return first(self.subscriptions, key=reference_id, value=reference_id)


class SubscriptionService:
    def __init__(self, user_session: UserSession):
        self.user_session = user_session
        self.streaming_session = None

    async def subscribe(self, subscription_cls: BaseSubscription, reference_id: str, arguments: Optional[dict] = None):
        self.subscription = await subscription_cls(reference_id, self.streaming_session, self.user_session.dispatcher)
        self.subscription.create(arguments)

    async def connect(self, context_id: str):
        self.streaming_session = StreamingSession(context_id, self.user_session.dispatcher)

    async def reconnect(self, context_id: str, last_message_id: int):
        pass
