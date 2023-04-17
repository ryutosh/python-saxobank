# import asyncio
# from functools import lru_cache
from logging import getLogger
from typing import Any, Dict

from pydantic import ValidationError
from winko import exceptions

# from . import ServiceState, dispatcher, endpoints, models, saxobank_request_dispatcher, service_state
from . import endpoints, models, saxobank_request_dispatcher

log = getLogger(__name__)


async def request_template(request_coro, response_model=None):
    # Send request
    status, body = await request_coro

    try:
        if response_model:
            res = response_model.parse_obj(body)

    except ValidationError as ex:
        log.error(f"Response message was invalid. Error: {ex}")
        raise exceptions.InvalidResponseError(detail=str(ex))

    return status, res if response_model else None


async def clients_me(winko_id, effectual_until=None):
    # Send request
    request_coro = saxobank_request_dispatcher.request_endpoint(
        winko_id,
        endpoints.PORT_CLIENTS_ME,
        effectual_until=effectual_until,
    )
    return await request_template(request_coro, models.PortClientsMeRes)


# @lru_cache  # Can not use because parameter:dict can not hashable
async def instruments_details(winko_id, req: dict, path_conv, effectual_until=None):
    # async def cache_clear(wait):
    #     await asyncio.sleep(wait)
    #     instruments_details.cache_clear()

    # # Set cache clear timer
    # log.debug(f"Request: {req}")
    # asyncio.create_task(cache_clear(60))

    # Send request
    request_coro = saxobank_request_dispatcher.request_endpoint(
        winko_id,
        endpoints.REF_INSTRUMENTS_DETAILS,
        data=req,
        path_conv=path_conv,
        effectual_until=effectual_until,
    )
    return await request_template(request_coro, models.InstrumentsDetailsResponse)


async def infoprices(winko_id, req: Dict[str, Any], effectual_until=None):
    # Send request
    request_coro = saxobank_request_dispatcher.request_endpoint(
        winko_id,
        endpoints.TRADE_INFOPRICES,
        data=req,
        effectual_until=effectual_until,
    )
    return await request_template(request_coro, models.InfoPricesResponse)


async def orders(winko_id, req: models.OrdersRequest, is_entry=True, effectual_until=None):
    # Send request
    request_coro = saxobank_request_dispatcher.request_endpoint(
        winko_id,
        endpoints.TRADE_ORDERS if is_entry else endpoints.TRADE_ORDERS_PATCH,
        data=req,
        effectual_until=effectual_until,
    )
    return await request_template(request_coro, models.OrdersResponse)


async def port_orders(winko_id, req: dict, path_conv, effectual_until=None, page=None):
    # Send request
    log.debug(f"Request: {req}, Page: {page}")
    if page:
        req["_Top"] = page[0]
        req["_Skip"] = page[1]

    request_coro = saxobank_request_dispatcher.request_endpoint(
        winko_id,
        endpoints.PORT_ORDERS,
        data=req,
        path_conv=path_conv,
        effectual_until=effectual_until,
    )
    status, res = await request_template(request_coro, models.PortOrdersResPaged)
    next_page = res.next_page()

    if next_page:
        status, next_res = await port_orders(winko_id, req, path_conv, effectual_until, next_page)
        res.Data.extend(next_res.Data)

    return status, res


async def positions(winko_id, req: dict, path_conv, effectual_until=None):
    request_coro = saxobank_request_dispatcher.request_endpoint(
        winko_id,
        endpoints.PORT_POSITIONS,
        data=req,
        path_conv=path_conv,
        effectual_until=effectual_until,
    )
    return await request_template(request_coro, models.PositionsMeResponse)


# 同じようなことを他のリクエストでもやると思うので、毎回TOP , SKIPの処理を書かないで良いように、それようのRequestTemplateを次作るときは用意する. good to use decorator??
async def positions_me(winko_id, req: dict, effectual_until=None, page=None):
    # Send request
    log.debug(f"Request: {req}, Page: {page}")
    if page:
        req["_Top"] = page[0]
        req["_Skip"] = page[1]

    request_coro = saxobank_request_dispatcher.request_endpoint(
        winko_id,
        endpoints.PORT_POSITIONS_ME,
        data=req,
        effectual_until=effectual_until,
    )
    status, res = await request_template(request_coro, models.PositionsMeResponsePaged)
    next_page = res.next_page()

    if next_page:
        status, next_res = await positions_me(winko_id, req, effectual_until, next_page)
        res.Data.extend(next_res.Data)

    return status, res
