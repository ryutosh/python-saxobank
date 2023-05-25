from __future__ import annotations

from typing import Any, Optional

from .common import ContextId, ReferenceId, SaxobankModel


class RequestCreateSubscription(SaxobankModel):
    """
    #  additional querys https://www.developer.saxo/openapi/referencedocs/port/v1/orders/addactivesubscription/53353f1979518cb2b9598b88ca8410e1
    #  $inlinecount
    #  $skip
    #  skiptoken
    #  $top: Optional[int] <-- query https://www.developer.saxo/openapi/referencedocs/port/v1/closedpositions/addactivesubscription/9e39bb714999a4e0048f97a39f6bec73
    #                                https://www.developer.saxo/openapi/referencedocs/port/v1/positions/addactivesubscription/f9116eaa246df2922e5d2dde51907ed9
    """

    ContextId: str
    ReferenceId: str
    Format: str
    Arguments: Any
    """
    # None case: https://www.developer.saxo/openapi/referencedocs/root/v1/sessions/addsubscription/12fcebb834c04dfbb0ff6b6a3a87a0df
    #                            https://www.developer.saxo/openapi/referencedocs/trade/v1/messages/addsubscriptionasync/a8a42807d6bbd9b3eaf69d0048fd59be
    """
    ReplaceReferenceId: Optional[str]
    """
    # RefreshRate: int
    """


class StreamingwsConnectReq(SaxobankModel):
    contextid: ContextId
    messageid: Optional[int]


class StreamingwsAuthorizeReq(SaxobankModel):
    contextid: ContextId


class ResponseCreateSubscription(SaxobankModel):
    RefreshRate: int
    Snapshot: Any


class RequestRemoveSubscription(SaxobankModel):
    ContextId: str
    ReferenceId: str
