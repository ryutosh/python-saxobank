from __future__ import annotations

import abc
import asyncio
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any, List, Optional, Set

from . import endpoint, model
from .model.common import ContextId, ReferenceId, SaxobankModel
from .user_session import UserSession

# class BaseSubscription(abc.ABC):
#     def __init__(self, user_session: UserSession, context_id: ContextId, reference_id: ReferenceId) -> None:
#         self.session = user_session
#         self.context_id = context_id
#         self.reference_id = reference_id


# # Create Method
# async def __create_with_top(
#     self: BaseSubscription,
#     arguments: SaxobankModel | None = None,
#     format: str | None = None,
#     refresh_rate: int | None = None,
#     tag: str | None = None,
#     top: int | None = None,
#     access_token: str | None = None,
# ):
#     # has argument necessary case :  https://www.developer.saxo/openapi/referencedocs/trade/v1/infoprices/addsubscriptionasync/b0ffda941b3291f3dd9319673cc88403
#     #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/optionschain/addsubscriptionasync/8ff796d4153fb5ae1dbce9ebf2d48b82
#     #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/prices/addsubscriptionasync/e1dbfa7d3e2ef801a7c4ade9e57f8812
#     #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/prices/addmultilegpricessubscriptionasync/7251ff94a91106a3b60a4d17df574694
#     req = self.__endpoint_create.RequestModel(
#         ContextId=self.context_id, ReferenceId=self.reference_id, Format=self.FORMAT_JSON, Arguments=arguments
#     ).dict(exclude_unset=True, exclude_none=True)

#     return await self.session.openapi_request(self.endpoint_create, req, acess_token=access_token)


# async def __remove(self: BaseSubscription, access_token: str | None = None):
#     req = self.__endpoint_remove.RequestModel(ContextId=self.context_id, ReferenceId=self.reference_id).dict(
#         exclude_unset=True, exclude_none=True
#     )

#     return await self.session.openapi_request(self.endpoint_remove, req, acess_token=access_token)


# async def remove_multiple(self: BaseSubscription):
#     pass
#     # has not supported case:  https://www.developer.saxo/openapi/referencedocs/root/v1/sessions/addsubscription/12fcebb834c04dfbb0ff6b6a3a87a0df
#     #                          https://www.developer.saxo/openapi/referencedocs/trade/v1/optionschain


# async def __aexit(self: BaseSubscription, exc_type, exc_value, traceback):
#     return await self.remove()


# class PortClosedPositions(BaseSubscription):
#     __endpoint_create = endpoint.port.closed_positions.POST_SUBSCRIPTION
#     __endpoint_remove = endpoint.port.closed_positions.DELETE_SUBSCRIPTION

#     global __create_with_top, __remove
#     create = __create_with_top
#     __aenter__ = create
#     remove = __remove
#     __aexit__ = __aexit

#     async def change_page_size(self, new_page_size: int, access_token: str | None = None):
#         req = endpoint.port.closed_positions.PATCH_SUBSCRIPTION.request_model(
#             ContextId=self.context_id, ReferenceId=self.reference_id, NewPageSize=new_page_size
#         ).dict(exclude_unset=True, exclude_none=True)

#         return await self.session.openapi_request(
#             endpoint.port.closed_positions.PATCH_SUBSCRIPTION, req, access_token=access_token
#         )


@lru_cache
def is_aware_datetime(target: datetime):
    return target.tzinfo and target.tzinfo.utcoffset(target)


class Subscription:
    delta_model: SaxobankModel = None

    def __init__(self, reference_id: ReferenceId):
        self.reference_id = reference_id
        self._deltas = asyncio.Queue()

        # Post setups
        self._setup_done = asyncio.Event()
        self.snapshot: Optional[SaxobankModel] = None
        self.timeout: Optional[timedelta] = None
        self.active_until: Optional[datetime] = None

    def heartbeats(self):
        if self.timeout:
            self.active_until = datetime.now(timezone.utc) + self.timeout

    def setup(self, inactivity_timeout_secs: int, snapshot: SaxobankModel):
        self.timeout = timedelta(seconds=inactivity_timeout_secs)
        self.snapshot = snapshot
        self._setup_done.set()

    async def apply_delta(self, delta: SaxobankModel):
        await self._deltas.put(delta)

    def inactive_before(self, dt: datetime) -> bool:
        assert is_aware_datetime(dt)
        return (self.active_until < dt) if self.active_until else False

    async def message(self):
        await self._setup_done.wait()

        delta = await self._deltas.get()
        self.snapshot = self.snapshot.apply_delta(delta)
        return self.snapshot, delta


class Subscriptions:
    def __init__(self):
        self._subscriptions: Set[Subscription] = set()

    def heartbeats(self, reference_ids: List[ReferenceId]) -> None:
        for subscription in self._subscriptions:
            if subscription.reference_id in reference_ids:
                subscription.heartbeats()

    def timeouts(self, inactive_before: datetime) -> Set[Subscription]:
        assert is_aware_datetime(inactive_before)

        def inactives(subscription):
            return subscription.inactive_before(inactive_before)

        timeout_subscriptions = set(filter(inactives, self._subscriptions))
        for subscription in timeout_subscriptions:
            self._subscriptions.remove(subscription)

        return timeout_subscriptions

    def remove(self, reference_ids: List[ReferenceId]) -> None:
        copy = self._subscriptions.copy()

        for subscription in copy:
            if subscription.reference_id in reference_ids:
                self._subscriptions.remove(subscription)

    def reference_ids(self) -> Set[ReferenceId]:
        return {subscription.reference_id for subscription in self._subscriptions}

    def get(self, reference_id: ReferenceId, default: Any) -> Any:
        for subscription in self._subscriptions:
            if subscription.reference_id == reference_id:
                return subscription
        return default
