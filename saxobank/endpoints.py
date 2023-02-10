from dataclasses import dataclass
from enum import Enum
from logging import getLogger

# from .dispatcher import ServiceGroup as G

# from winko. import dispatcher
log = getLogger(__name__)


class HttpMethod(str, Enum):
    NONE = "NONE"  # for auth, token
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class ContentType(Enum):
    TEXT = 1
    JSON = 2


@dataclass
class RequestEndpoint:
    url: str
    method: HttpMethod
    # group: G
    ratelimit_dimension: str
    req_content: ContentType = ContentType.JSON
    token_auth: bool = True
    is_order: bool = False


# Shortcuts
M = HttpMethod
E = RequestEndpoint

# Gateway
GATEWAY_LIVE = "https://gateway.saxobank.com/openapi/"
GATEWAY_SIM = "https://gateway.saxobank.com/sim/openapi/"

# Endpoint definitions
CHART_CHARTS = E("chart/v1/charts", M.GET, "ChartMinute")
PORT_CLIENTS_ME = E("port/v1/clients/me", M.GET, "PortfolioMinute")
PORT_ORDERS = E("port/v1/orders/{ClientKey}/{OrderId}", M.GET, "PortfolioMinute")
PORT_POSITIONS = E("port/v1/positions/{PositionId}", M.GET, "PortfolioMinute")
PORT_POSITIONS_ME = E("port/v1/positions/me", M.GET, "PortfolioMinute")
REF_INSTRUMENTS_DETAILS = E("ref/v1/instruments/details/{Uic}/{AssetType}", M.GET, "RefDataInstrumentsMinute")
# ROOT_SESSIONS_CAPABILITIES = E("sessions/capabilities", M.PUT, G.ROOT)
# STREAMINGWS_CONNECT = E("streamingws/connect", M.NONE, G.NONE)
TRADE_INFOPRICES = E("trade/v1/infoprices", M.GET, "TradeInfoPricesMinute")
# TRADE_INFOPRICES_SUBSCRIPTIONS = E("trade/v1/infoprices/subscriptions", M.POST, G.TRADE)
TRADE_ORDERS = E("trade/v2/orders", M.POST, "TradeOrdersPostSecond", is_order=True)
TRADE_ORDERS_PATCH = E("trade/v2/orders", M.PATCH, "TradeOrdersPatchSecond", is_order=True)
