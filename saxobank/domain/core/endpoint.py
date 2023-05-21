from dataclasses import dataclass
from enum import Enum, auto
from functools import lru_cache


class Dimension(str, Enum):
    ChartMinute = "ChartMinute"
    PortfolioMinute = "PortfolioMinute"
    RefDataInstrumentsMinute = "RefDataInstrumentsMinute"
    RootMinute = "RootMinute"
    TradeInfoPricesMinute = "TradeInfoPricesMinute"
    TradeOrdersPostSecond = "TradeOrdersPostSecond"
    TradeOrdersPatchSecond = "TradeOrdersPatchSecond"


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class ContentType(Enum):
    TEXT = auto()
    JSON = auto()


@dataclass
class EndpointDefinition:
    path: str
    method: HttpMethod
    dimension: Dimension
    content_type: ContentType = ContentType.JSON

    def path(self, path_conv: dict[str, str]) -> str:
        return self.path.format(path_conv)


# Shortcuts
D = Dimension
M = HttpMethod
E = EndpointDefinition


class Endpoint(EndpointDefinition, Enum):
    CHART_CHARTS = E("chart/v1/charts", M.GET, D.ChartMinute)
    CHART_CHARTS_SUBSCRIPTIONS = E("chart/v1/charts/subscriptions", M.POST, None)
    CHART_CHARTS_SUBSCRIPTIONS_DELETE = E("chart/v1/charts/subscriptions/{contextId}/{ReferenceId}", M.DELETE, None)
    CHART_CHARTS_SUBSCRIPTIONS_DELETE_MULTIPLE = E("chart/v1/charts/subscriptions/{contextId}", M.DELETE, None)
    PORT_CLIENTS_ME = E("port/v1/clients/me", M.GET, D.PortfolioMinute)
    PORT_ORDERS = E("port/v1/orders/{ClientKey}/{OrderId}", M.GET, D.PortfolioMinute)
    PORT_POSITIONS_POSITION_ID = E("port/v1/positions/{PositionId}", M.GET, D.PortfolioMinute)
    PORT_POSITIONS_ME = E("port/v1/positions/me", M.GET, D.PortfolioMinute)
    REF_INSTRUMENTS_DETAILS = E("ref/v1/instruments/details/{Uic}/{AssetType}", M.GET, D.RefDataInstrumentsMinute)
    ROOT_SESSIONS_CAPABILITIES = E("root/v1/sessions/capabilities", M.GET, D.RootMinute)
    ROOT_SESSIONS_CAPABILITIES_PATCH = E("root/v1/sessions/capabilities", M.PATCH, D.RootMinute)
    TRADE_INFOPRICES = E("trade/v1/infoprices", M.GET, D.TradeInfoPricesMinute)
    TRADE_ORDERS = E("trade/v2/orders", M.POST, D.TradeOrdersPostSecond)
    TRADE_ORDERS_PATCH = E("trade/v2/orders", M.PATCH, D.TradeOrdersPatchSecond)
