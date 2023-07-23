from __future__ import annotations

import asyncio
import collections
from collections.abc import Container
from datetime import datetime, timedelta, timezone
from typing import Any, Collection, Iterator, Optional, Set, Union, cast

from .common import is_aware_datetime
from .model.common import ReferenceId, SaxobankModel

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


class Subscription:
    # delta_model: SaxobankModel = None

    def __init__(self, reference_id: Union[ReferenceId, str], tag: Optional[str] = None) -> None:
        self.reference_id = reference_id if isinstance(reference_id, ReferenceId) else ReferenceId(reference_id)
        self.tag = tag

        # Post setups
        self._preparation = asyncio.Event()
        self._snapshot: Optional[SaxobankModel] = None
        self._inactivity_timeout: Optional[timedelta] = None
        self._timeout_after: Optional[datetime] = None

    def __hash__(self) -> int:
        return hash((self.__class__, self.reference_id))

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return hash(self) == hash(o)

    def _setup(self, inactivity_timeout_secs: int, snapshot: SaxobankModel) -> None:
        assert not self._preparation.is_set()

        self._inactivity_timeout = timedelta(seconds=inactivity_timeout_secs)
        self._snapshot = snapshot
        self._preparation.set()

    async def wait_preparation(self) -> None:
        await self._preparation.wait()

    def extend_timeout(self) -> None:
        if self._inactivity_timeout:
            self._timeout_after = datetime.now(timezone.utc) + self._inactivity_timeout

    def is_timed_out(self, evaluate_at: datetime) -> bool:
        assert is_aware_datetime(evaluate_at)
        return (self._timeout_after < evaluate_at) if self._timeout_after else False

    @property
    def snapshot(self) -> SaxobankModel:
        if not self._snapshot:
            raise RuntimeError

        return self._snapshot.copy()

    def apply_delta(self, delta: Any) -> Optional[SaxobankModel]:
        assert self._snapshot is not None
        self._snapshot, is_parted = self.snapshot.apply_delta(delta)

        return cast(SaxobankModel, self._snapshot) if not is_parted else None


class Subscriptions(collections.abc.MutableSet):
    def __init__(self) -> None:
        self._subscriptions: Set[Subscription] = set()

    def __contains__(self, o: object) -> bool:
        return o in self._subscriptions

    def __iter__(self) -> Iterator[Subscription]:
        return iter(self._subscriptions)

    def __len__(self) -> int:
        return len(self._subscriptions)

    def get(self, reference_id: Union[ReferenceId, str]) -> Subscription:
        for s in self._subscriptions:
            if s.reference_id == reference_id:
                return s
        raise KeyError

    def reference_ids(self) -> Set[ReferenceId]:
        return {subscription.reference_id for subscription in self._subscriptions}

    def add(self, subscription: Subscription) -> None:
        assert isinstance(subscription, Subscription)
        self._subscriptions.add(subscription)

    def discard(self, subscription: Subscription) -> None:
        assert isinstance(subscription, Subscription)
        self._subscriptions.discard(subscription)

    def remove_items(
        self,
        subscriptions: Optional[Collection[Subscription]] = None,
        reference_ids: Optional[Collection[ReferenceId]] = None,
        tag: Optional[str] = None,
    ) -> None:
        if subscriptions:
            for s in subscriptions:
                self.discard(s)

        elif reference_ids:
            self.remove_items(subscriptions={self.get(r) for r in reference_ids})

        elif tag:
            self.remove_items(subscriptions={s for s in self._subscriptions if s.tag == tag})

    def remove_timeouts(self, evaluate_at: datetime) -> Set[ReferenceId]:
        assert is_aware_datetime(evaluate_at)

        timeouts = {s for s in self._subscriptions if s.is_timed_out(evaluate_at)}
        for subscription in timeouts:
            self.remove(subscription)
        return {s.reference_id for s in timeouts}

    def extend_timeout(self, reference_ids: Container[ReferenceId]) -> None:
        for subscription in {s for s in self._subscriptions if s.reference_id in reference_ids}:
            subscription.extend_timeout()
