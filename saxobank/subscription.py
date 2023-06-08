from __future__ import annotations

import abc

from . import model
from .endpoint import Endpoint
from .model.common import ContextId, ReferenceId, SaxobankModel
from .user_session import UserSession


class BaseSubscription(abc.ABC):
    def __init__(self, user_session: UserSession, context_id: ContextId, reference_id: ReferenceId) -> None:
        self.session = user_session
        self.context_id = context_id
        self.reference_id = reference_id


# Create Method
async def __create_with_top(
    self: BaseSubscription,
    arguments: SaxobankModel | None = None,
    format: str | None = None,
    refresh_rate: int | None = None,
    tag: str | None = None,
    top: int | None = None,
    access_token: str | None = None,
):
    # has argument necessary case :  https://www.developer.saxo/openapi/referencedocs/trade/v1/infoprices/addsubscriptionasync/b0ffda941b3291f3dd9319673cc88403
    #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/optionschain/addsubscriptionasync/8ff796d4153fb5ae1dbce9ebf2d48b82
    #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/prices/addsubscriptionasync/e1dbfa7d3e2ef801a7c4ade9e57f8812
    #                                https://www.developer.saxo/openapi/referencedocs/trade/v1/prices/addmultilegpricessubscriptionasync/7251ff94a91106a3b60a4d17df574694
    req = self.__endpoint_create.RequestModel(
        ContextId=self.context_id, ReferenceId=self.reference_id, Format=self.FORMAT_JSON, Arguments=arguments
    ).dict(exclude_unset=True, exclude_none=True)

    return await self.session.openapi_request(self.endpoint_create, req, acess_token=access_token)


async def __remove(self: BaseSubscription, access_token: str | None = None):
    req = self.__endpoint_remove.RequestModel(ContextId=self.context_id, ReferenceId=self.reference_id).dict(
        exclude_unset=True, exclude_none=True
    )

    return await self.session.openapi_request(self.endpoint_remove, req, acess_token=access_token)


async def remove_multiple(self: BaseSubscription):
    pass
    # has not supported case:  https://www.developer.saxo/openapi/referencedocs/root/v1/sessions/addsubscription/12fcebb834c04dfbb0ff6b6a3a87a0df
    #                          https://www.developer.saxo/openapi/referencedocs/trade/v1/optionschain


async def __aexit(self: BaseSubscription, exc_type, exc_value, traceback):
    return await self.remove()


class PortClosedPositions(BaseSubscription):
    __endpoint_create = Endpoint.PORT_POST_CLOSEDPOSITIONS_SUBSCRIPTION
    __endpoint_remove = Endpoint.PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION

    create = __create_with_top
    __aenter__ = create
    remove = __remove
    __aexit__ = __aexit

    async def change_page_size(self, new_page_size: int, access_token: str | None = None):
        req = Endpoint.PORT_PATCH_CLOSEDPOSITIONS_SUBSCRIPTION.RequestModel(
            ContextId=self.context_id, ReferenceId=self.reference_id, NewPageSize=new_page_size
        ).dict(exclude_unset=True, exclude_none=True)

        return await self.session.openapi_request(
            Endpoint.PORT_PATCH_CLOSEDPOSITIONS_SUBSCRIPTION, req, acess_token=access_token
        )
