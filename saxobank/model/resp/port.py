"""Response models used port service group.


"""

from dataclasses import dataclass
from typing import Any, cast

from ... import model
from ..base import SaxobankModel2


@dataclass
class PostPortOrdersSubscriptionsStreamingResp(SaxobankModel2):
    """Streaming response model for [`saxobank.application.Client.post_port_orders_subscriptions`][]

    *See [OpenAPI Reference](https://www.developer.saxo/openapi/referencedocs/port/v1/orders/addactivesubscription/53353f1979518cb2b9598b88ca8410e1) for original info.*

    Attributes(Not completed):
        AccountKey: Unique key of the account where the order is placed
        AssetType: The instrument asset type.
        Uic: Unique Id of the instrument
    """

    AccountKey: model.common.AccountKey | str
    AssetType: model.common.AssetType | str
    Uic: int

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.AccountKey and not isinstance(self.AccountKey, model.common.AccountKey):
            self.AccountKey = model.common.AccountKey(self.AccountKey)
        if self.AssetType and not isinstance(self.AssetType, model.common.AssetType):
            self.AssetType = model.common.AssetType(self.AssetType)


from typing import ClassVar


@dataclass
class SaxobankRootModel2(SaxobankModel2):
    _root: list[SaxobankModel2] | list[dict[str, Any]]

    def __init__(self, /, model: list[SaxobankModel2] | list[dict[str, Any]]) -> None:
        self._root = model


@dataclass
class PostPortOrdersSubscriptionsStreamingRespRoot(SaxobankRootModel2):
    """Streaming response model for [`saxobank.application.Client.post_port_orders_subscriptions`][]

    *See [OpenAPI Reference](https://www.developer.saxo/openapi/referencedocs/port/v1/orders/addactivesubscription/53353f1979518cb2b9598b88ca8410e1) for original info.*

    Attributes(Not completed):
        AccountKey: Unique key of the account where the order is placed
        AssetType: The instrument asset type.
        Uic: Unique Id of the instrument
    """

    _root: list[PostPortOrdersSubscriptionsStreamingResp] | list[dict[str, Any]]

    def __init__(
        self, /, model: list[PostPortOrdersSubscriptionsStreamingResp] | list[dict[str, Any]]
    ) -> None:
        print("init")
        self._root = model
        self.__post_init__()

    def __post_init__(self) -> None:
        print("post init")
        super().__post_init__()

        if self._root and any(
            (
                not isinstance(member, PostPortOrdersSubscriptionsStreamingResp)
                for member in self._root
            )
        ):
            self._root = [
                PostPortOrdersSubscriptionsStreamingResp(**member)
                for member in cast(list[dict[str, Any]], self._root)
            ]
