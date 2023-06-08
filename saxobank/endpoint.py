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


@dataclass  # (frozen=True)
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

    # def url(self, path_converts: Optional[dict[str, str]] = None) -> str:
    #     return self.path.format(**path_converts) if path_converts else self.path


# Shortcuts
__D = Dimension
__M = HttpMethod
E = EndpointDefinition

# CHART_CHARTS = E("chart/v1/charts", __M.GET, __D.ChartMinute)
# CHART_CHARTS_SUBSCRIPTIONS = E("chart/v1/charts/subscriptions", __M.POST)
# CHART_CHARTS_SUBSCRIPTIONS_DELETE = E("chart/v1/charts/subscriptions/{contextId}/{ReferenceId}", __M.DELETE)
# CHART_CHARTS_SUBSCRIPTIONS_DELETE_MULTIPLE = E("chart/v1/charts/subscriptions/{contextId}", __M.DELETE)
# PORT_GET_CLIENTS_ME = E("port/v1/clients/me", __M.GET, __D.PortfolioMinute)
# PORT_GET_ORDERS = E("port/v1/orders/{ClientKey}/{OrderId}", __M.GET, __D.PortfolioMinute)
# PORT_GET_POSITIONS_POSITION_ID = E("port/v1/positions/{PositionId}", __M.GET, __D.PortfolioMinute)
# PORT_GET_POSITIONS_ME = E("port/v1/positions/me", __M.GET, __D.PortfolioMinute)
# PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION = E("port/v1/closedpositions/subscriptions/{ContextId}/{ReferenceId}", __M.DELETE)
# PORT_PATCH_CLOSEDPOSITIONS_SUBSCRIPTION = E("port/v1/closedpositions/subscriptions/{ContextId}/{ReferenceId}", __M.PATCH)
# PORT_POST_CLOSEDPOSITIONS_SUBSCRIPTION = E("port/v1/closedpositions/subscriptions", __M.POST)
# REF_INSTRUMENTS_DETAILS = E("ref/v1/instruments/details/{Uic}/{AssetType}", __M.GET, __D.RefDataInstrumentsMinute)
# ROOT_SESSIONS_CAPABILITIES = E("root/v1/sessions/capabilities", __M.GET, __D.RootMinute)
# ROOT_SESSIONS_CAPABILITIES_PATCH = E("root/v1/sessions/capabilities", __M.PATCH, __D.RootMinute)
# TRADE_INFOPRICES = E("trade/v1/infoprices", __M.GET, __D.TradeInfoPricesMinute)
# TRADE_ORDERS = E("trade/v2/orders", __M.POST, __D.TradeOrdersPostSecond)
# TRADE_ORDERS_PATCH = E("trade/v2/orders", __M.PATCH, __D.TradeOrdersPatchSecond)

XXX = EndpointDefinition("port/v1/clients/me", HttpMethod.GET, dimension=Dimension.PortfolioMinute)


# class Endpoint(__EndpointDefinition, Enum):
class Endpoint(EndpointDefinition, Enum):
    P1 = EndpointDefinition("port/v1/clients/me", HttpMethod.GET, dimension=Dimension.PortfolioMinute)
    # CHART_CHARTS = E("chart/v1/charts", __M.GET, __D.ChartMinute)
    # CHART_CHARTS_SUBSCRIPTIONS = E("chart/v1/charts/subscriptions", __M.POST)
    # CHART_CHARTS_SUBSCRIPTIONS_DELETE = E("chart/v1/charts/subscriptions/{contextId}/{ReferenceId}", __M.DELETE)
    # CHART_CHARTS_SUBSCRIPTIONS_DELETE_MULTIPLE = E("chart/v1/charts/subscriptions/{contextId}", __M.DELETE)
    # PORT_GET_CLIENTS_ME = EndpointDefinition("port/v1/clients/me", HttpMethod.GET, Dimension.PortfolioMinute)
    # PORT_GET_ORDERS = E("port/v1/orders/{ClientKey}/{OrderId}", __M.GET, __D.PortfolioMinute)
    # PORT_GET_POSITIONS_POSITION_ID = E("port/v1/positions/{PositionId}", __M.GET, __D.PortfolioMinute)
    # PORT_GET_POSITIONS_ME = E("port/v1/positions/me", __M.GET, __D.PortfolioMinute)
    # PORT_DELETE_CLOSEDPOSITIONS_SUBSCRIPTION = E("port/v1/closedpositions/subscriptions/{ContextId}/{ReferenceId}", __M.DELETE)
    # PORT_PATCH_CLOSEDPOSITIONS_SUBSCRIPTION = E("port/v1/closedpositions/subscriptions/{ContextId}/{ReferenceId}", __M.PATCH)
    # PORT_POST_CLOSEDPOSITIONS_SUBSCRIPTION = E("port/v1/closedpositions/subscriptions", __M.POST)
    # REF_INSTRUMENTS_DETAILS = E("ref/v1/instruments/details/{Uic}/{AssetType}", __M.GET, __D.RefDataInstrumentsMinute)
    # ROOT_SESSIONS_CAPABILITIES = E("root/v1/sessions/capabilities", __M.GET, __D.RootMinute)
    # ROOT_SESSIONS_CAPABILITIES_PATCH = E("root/v1/sessions/capabilities", __M.PATCH, __D.RootMinute)
    # TRADE_INFOPRICES = E("trade/v1/infoprices", __M.GET, __D.TradeInfoPricesMinute)
    # TRADE_ORDERS = E("trade/v2/orders", __M.POST, __D.TradeOrdersPostSecond)
    # TRADE_ORDERS_PATCH = E("trade/v2/orders", __M.PATCH, __D.TradeOrdersPatchSecond)
