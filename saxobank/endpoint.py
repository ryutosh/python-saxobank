from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Optional, Type

from .model import chart, common, port, ref, root


class Dimension(str, Enum):
    ChartMinute = "ChartMinute"
    PortfolioMinute = "PortfolioMinute"
    RefDataInstrumentsMinute = "RefDataInstrumentsMinute"
    RootMinute = "RootMinute"
    TradeInfoPricesMinute = "TradeInfoPricesMinute"
    TradeOrdersPostSecond = "TradeOrdersPostSecond"
    TradeOrdersPatchSecond = "TradeOrdersPatchSecond"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class ContentType(str, Enum):
    JSON = "application/json"


@dataclass(frozen=True)
class Endpoint:
    __instances: ClassVar[set] = set()
    path: str
    method: HttpMethod
    dimension: Optional[Dimension] = None
    is_order: bool = False
    content_type: ContentType = ContentType.JSON
    request_model: Optional[Type[common.SaxobankModel]] = None
    response_model: Optional[Type[common.SaxobankModel]] = None

    # def url(self, base_url: str, path_converts: dict[str, Any] | None = None) -> str:
    #     converted_path = self.path.format(**path_converts) if path_converts else self.path
    #     return urljoin(base_url, self.path.format(converted_path))

    def __post_init__(self) -> None:
        self.__instances.add(self)

    @classmethod
    def match(cls, path: str) -> Optional[Endpoint]:
        # Need wildcard match for fstring segments
        _match = [instance for instance in cls.__instances if instance.path in path]
        return _match[0] if _match else None

    def url(self, path_converts: Optional[dict[str, str]] = None) -> str:
        return self.path.format(**path_converts) if path_converts else self.path


CHART_CHARTS_GET = Endpoint("chart/v1/charts", HttpMethod.GET, Dimension.ChartMinute)
CHART_CHARTS_SUBSCRIPTIONS_DELETE = Endpoint(
    "chart/v1/charts/subscriptions", HttpMethod.DELETE, Dimension.ChartMinute, request_model=chart.charts.ReqSubscriptionDelete
)
CHART_CHARTS_SUBSCRIPTIONS_POST = Endpoint(
    "chart/v1/charts/subscriptions",
    HttpMethod.POST,
    Dimension.ChartMinute,
    request_model=chart.charts.ReqSubscriptionsPost,
    response_model=chart.charts.RespSubscriptionsPost,
)
PORT_CLIENTS_ME_GET = Endpoint(
    "port/v1/clients/me", HttpMethod.GET, Dimension.PortfolioMinute, response_model=port.clients.MeRes
)
PORT_CLOSEDPOSITIONS_GET = Endpoint(
    "port/v1/closedpositions", HttpMethod.GET, response_model=port.closedpositions.ClosedPositionRes
)
PORT_CLOSEDPOSITIONS_SUBSCRIPTION_DELETE = Endpoint(
    "port/v1/closedpositions/subscriptions/{ContextId}/{ReferenceId}", HttpMethod.DELETE
)
PORT_CLOSEDPOSITIONS_SUBSCRIPTION_PATCH = Endpoint(
    "port/v1/closedpositions/subscriptions/{ContextId}/{ReferenceId}", HttpMethod.PATCH
)
PORT_CLOSEDPOSITIONS_SUBSCRIPTION_POST = Endpoint(
    "port/v1/closedpositions/subscriptions",
    HttpMethod.POST,
    request_model=port.closedpositions.PostSubscriptionReq,
    response_model=port.closedpositions.PostSubscriptionRes,
)
PORT_POSITIONS_ME_GET = Endpoint(
    "port/v1/positions/me", HttpMethod.GET, Dimension.PortfolioMinute, response_model=port.positions.MeRes
)
PORT_POSITIONS_POSITIONID_GET = Endpoint("port/v1/positions/{PositionId}", HttpMethod.GET, Dimension.PortfolioMinute)

REF_INSTRUMENTS_DETAILS_GET = Endpoint(
    "ref/v1/instruments/details",
    HttpMethod.GET,
    Dimension.RefDataInstrumentsMinute,
    request_model=ref.instruments.InstrumentsDetailsRequest,
    response_model=ref.instruments.InstrumentsDetailsResponse,
)

ROOT_SESSIONS_CAPABILITIES_GET = Endpoint("root/v1/sessions/capabilities", HttpMethod.GET, Dimension.RootMinute)
ROOT_SESSIONS_CAPABILITIES_PATCH = Endpoint(
    "root/v1/sessions/capabilities",
    HttpMethod.PATCH,
    Dimension.RootMinute,
    request_model=root.sessions.PutCapabilities,
)
ROOT_SESSIONS_CAPABILITIES_PUT = Endpoint(
    "root/v1/sessions/capabilities", HttpMethod.PUT, Dimension.RootMinute, request_model=root.sessions.PutCapabilities
)
