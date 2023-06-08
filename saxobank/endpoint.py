from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from typing import Optional

from .model.common import SaxobankModel


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


class ContentType(Enum):
    JSON = "application/json"


@dataclass(frozen=True)
class EndpointDefinition:
    path: str
    method: HttpMethod
    dimension: Optional[Dimension] = None
    is_order: bool = False
    content_type: ContentType = ContentType.JSON
    response_model: Optional[SaxobankModel] = None

    # def url(self, base_url: str, path_converts: dict[str, Any] | None = None) -> str:
    #     converted_path = self.path.format(**path_converts) if path_converts else self.path
    #     return urljoin(base_url, self.path.format(converted_path))

    def url(self, path_converts: Optional[dict[str, str]] = None) -> str:
        return self.path.format(**path_converts) if path_converts else self.path


# CHART_CHARTS = EndpointDefinition("chart/v1/charts", HttpMethod.GET,Dimension.ChartMinute)
# CHART_CHARTS_SUBSCRIPTIONS = EndpointDefinition("chart/v1/charts/subscriptions", HttpMethod.POST)
# CHART_CHARTS_SUBSCRIPTIONS_DELETE = EndpointDefinition("chart/v1/charts/subscriptions/{contextId}/{ReferenceId}", HttpMethod.DELETE)
# CHART_CHARTS_SUBSCRIPTIONS_DELETE_MULTIPLE = EndpointDefinition("chart/v1/charts/subscriptions/{contextId}", HttpMethod.DELETE)
# PORT_GET_CLIENTS_ME = EndpointDefinition("port/v1/clients/me", HttpMethod.GET,Dimension.PortfolioMinute)
# PORT_GET_ORDERS = EndpointDefinition("port/v1/orders/{ClientKey}/{OrderId}", HttpMethod.GET,Dimension.PortfolioMinute)
# PORT_GET_POSITIONS_POSITION_ID = EndpointDefinition("port/v1/positions/{PositionId}", HttpMethod.GET,Dimension.PortfolioMinute)
# PORT_GET_POSITIONS_ME = EndpointDefinition("port/v1/positions/me", HttpMethod.GET,Dimension.PortfolioMinute)
# PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION = EndpointDefinition("port/v1/closedpositions/subscriptions/{ContextId}/{ReferenceId}", HttpMethod.DELETE)
# PORT_PATCH_CLOSEDPOSITIONS_SUBSCRIPTION = EndpointDefinition("port/v1/closedpositions/subscriptions/{ContextId}/{ReferenceId}", HttpMethod.PATCH)
# PORT_POST_CLOSEDPOSITIONS_SUBSCRIPTION = EndpointDefinition("port/v1/closedpositions/subscriptions", HttpMethod.POST)
# REF_INSTRUMENTS_DETAILS = EndpointDefinition("ref/v1/instruments/details/{Uic}/{AssetType}", HttpMethod.GET,Dimension.RefDataInstrumentsMinute)
# ROOT_SESSIONS_CAPABILITIES = EndpointDefinition("root/v1/sessions/capabilities", HttpMethod.GET,Dimension.RootMinute)
# ROOT_SESSIONS_CAPABILITIES_PATCH = EndpointDefinition("root/v1/sessions/capabilities", HttpMethod.PATCH,Dimension.RootMinute)
# TRADE_INFOPRICES = EndpointDefinition("trade/v1/infoprices", HttpMethod.GET,Dimension.TradeInfoPricesMinute)
# TRADE_ORDERS = EndpointDefinition("trade/v2/orders", HttpMethod.POST,Dimension.TradeOrdersPostSecond)
# TRADE_ORDERS_PATCH = EndpointDefinition("trade/v2/orders", HttpMethod.PATCH,Dimension.TradeOrdersPatchSecond)


# class Endpoint(__EndpointDefinition, Enum):
class Endpoint(EndpointDefinition, Enum):
    CHART_CHARTS = ("chart/v1/charts", HttpMethod.GET, Dimension.ChartMinute)
    PORT_GET_CLIENTS_ME = ("port/v1/clients/me", HttpMethod.GET, Dimension.PortfolioMinute)
    # def __init__(self, value: EndpointDefinition):

    # CHART_CHARTS_SUBSCRIPTIONS = EndpointDefinition("chart/v1/charts/subscriptions", HttpMethod.POST)
    # CHART_CHARTS_SUBSCRIPTIONS_DELETE = EndpointDefinition(
    #     "chart/v1/charts/subscriptions/{contextId}/{ReferenceId}", HttpMethod.DELETE
    # )
    # CHART_CHARTS_SUBSCRIPTIONS_DELETE_MULTIPLE = EndpointDefinition(
    #     "chart/v1/charts/subscriptions/{contextId}", HttpMethod.DELETE
    # )
    # PORT_GET_ORDERS = EndpointDefinition("port/v1/orders/{ClientKey}/{OrderId}", HttpMethod.GET, Dimension.PortfolioMinute)
    # PORT_GET_POSITIONS_POSITION_ID = EndpointDefinition(
    #     "port/v1/positions/{PositionId}", HttpMethod.GET, Dimension.PortfolioMinute
    # )
    # PORT_GET_POSITIONS_ME = EndpointDefinition("port/v1/positions/me", HttpMethod.GET, Dimension.PortfolioMinute)
    # PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION = EndpointDefinition(
    #     "port/v1/closedpositions/subscriptions/{ContextId}/{ReferenceId}", HttpMethod.DELETE
    # )
    # PORT_PATCH_CLOSEDPOSITIONS_SUBSCRIPTION = EndpointDefinition(
    #     "port/v1/closedpositions/subscriptions/{ContextId}/{ReferenceId}", HttpMethod.PATCH
    # )
    # PORT_POST_CLOSEDPOSITIONS_SUBSCRIPTION = EndpointDefinition("port/v1/closedpositions/subscriptions", HttpMethod.POST)
    # REF_INSTRUMENTS_DETAILS = EndpointDefinition(
    #     "ref/v1/instruments/details/{Uic}/{AssetType}", HttpMethod.GET, Dimension.RefDataInstrumentsMinute
    # )
    # ROOT_SESSIONS_CAPABILITIES = EndpointDefinition("root/v1/sessions/capabilities", HttpMethod.GET, Dimension.RootMinute)
    # ROOT_SESSIONS_CAPABILITIES_PATCH = EndpointDefinition(
    #     "root/v1/sessions/capabilities", HttpMethod.PATCH, Dimension.RootMinute
    # )
    # TRADE_INFOPRICES = EndpointDefinition("trade/v1/infoprices", HttpMethod.GET, Dimension.TradeInfoPricesMinute)
    # TRADE_ORDERS = EndpointDefinition("trade/v2/orders", HttpMethod.POST, Dimension.TradeOrdersPostSecond)
    # TRADE_ORDERS_PATCH = EndpointDefinition("trade/v2/orders", HttpMethod.PATCH, Dimension.TradeOrdersPatchSecond)
