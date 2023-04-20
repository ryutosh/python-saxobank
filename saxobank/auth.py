import asyncio
import logging

# --
from winkorpc import auth_pb2

# from winko import exceptions
# from winko import saxobank_request_dispatcher
from . import exceptions, models
from . import request as saxo_req
from . import saxobank_request_dispatcher

log = logging.getLogger(__name__)


async def auth_url(winko_id, redirect_uri, state_string=None):
    return saxobank_request_dispatcher.auth_url(winko_id, redirect_uri, state_string)


async def delete_auth_info(request):
    log.debug(f"def start.")
    saxobank_request_dispatcher.remove_authinfo(request.winko_id)
    log.debug(f"def exit.")
    return auth_pb2.IsAuthenticatedResponse(is_authenticated=False)


async def add_authinfo(request):
    log.debug(f"def start.")

    saxobank_request_dispatcher.add_authinfo(
        request.winko_id,
        # request.saxobank_auth_info.app_key,
        # request.saxobank_auth_info.app_secret,
        request.saxobank_auth_info.auth_code
        # request.saxobank_auth_info.redirect_uri,
        # need_refresh=request.saxobank_auth_info.need_refresh,
    )
    # Elevate trade level
    await asyncio.sleep(5)
    await full_trade_capability(request.winko_id)

    log.debug(f"def exit.")
    return auth_pb2.IsAuthenticatedResponse(is_authenticated=True)


async def full_trade_capability(winko_id):
    try:
        status, capabilities_res = await saxo_req.root_sessions_capabilities(winko_id)
    except exceptions.RequestError:
        raise exceptions.OrderError()

    if (curr_trade_level := capabilities_res.TradeLevel) is None:
        log.error(f"TradeLevel can not determine.")
        raise exceptions.OrderError()

    log.debug(f"Current TradeLevel: {curr_trade_level}")
    if curr_trade_level != models.TradeLevel.FullTradingAndChat:
        change_capabilities_req = models.ChangeSessionsCapabilitiesRequest(
            TradeLevel=models.TradeLevel.FullTradingAndChat,
        ).dict(exclude_unset=True)

        try:
            status, _ = await saxo_req.change_root_sessions_capabilities(winko_id, change_capabilities_req)
        except exceptions.RequestError:
            raise exceptions.OrderError()

        log.info(f"TradeLevel changed to FullTrading.")
