from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from logging import getLogger

from saxobank.models.common import SaxobankModel

# from pydantic import ValidationError
# from winko import exceptions


# from . import saxobank_request_dispatcher

# from .dispatcher import ServiceGroup as G


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
    # ------------
    request: SaxobankModel = SaxobankModel()
    response: SaxobankModel = SaxobankModel()
    # ------------


# Shortcuts
M = HttpMethod
E = RequestEndpoint

# Gateway
GATEWAY_LIVE = "https://gateway.saxobank.com/openapi/"
GATEWAY_SIM = "https://gateway.saxobank.com/sim/openapi/"

# Endpoint definitions
CS_AUDIT_ORDERACTIVITIES = E("cs/v1/audit/orderactivities", M.GET, "")
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


# async def request_template(request_coro, response_model=None):
#     # Send request
#     status, body = await request_coro

#     try:
#         if response_model:
#             res = response_model.parse_obj(body)

#     except ValidationError as ex:
#         log.error(f"Response message was invalid. Error: {ex}")
#         raise exceptions.InvalidResponseError(detail=str(ex))

#     return status, res if response_model else None


# async def request(endpoint: RequestEndpoint, winko_id=None, effectual_until=None, **params) -> SaxobankModel:

#     req = endpoint.request(**params).dict(exclude_unset=True)

#     # infoprices_req = models.InfoPricesRequest(
#     #     AssetType=orders_main.AssetType,
#     #     Uic=orders_main.Uic,
#     #     FieldGroups=[models.InfoPriceGroupSpec.Quote],
#     # ).dict(exclude_unset=True)

#     request_coro = saxobank_request_dispatcher.request_endpoint(
#         winko_id,
#         endpoint.request,
#         data=req,
#         effectual_until=effectual_until,
#     )
#     status, res = await request_template(request_coro, endpoint.response)
#     return res
