import logging

# --
# import pydantic

# --
from winko.protos import auth_pb2

# from winko import exceptions
# from winko import saxobank_request_dispatcher
from . import saxobank_request_dispatcher

# from winko.saxobank import dispatcher

# from winko.saxobank import models


logger = logging.getLogger(__name__)


async def auth_url(winko_id, redirect_uri, state_string=None):
    return saxobank_request_dispatcher.auth_url(winko_id, redirect_uri, state_string)


async def delete_auth_info(request):
    logger.debug(f"def start.")
    saxobank_request_dispatcher.remove_authinfo(request.winko_id)
    logger.debug(f"def exit.")
    return auth_pb2.IsAuthenticatedResponse(is_authenticated=False)


async def add_authinfo(request):
    logger.debug(f"def start.")

    saxobank_request_dispatcher.add_authinfo(
        request.winko_id,
        # request.saxobank_auth_info.app_key,
        # request.saxobank_auth_info.app_secret,
        request.saxobank_auth_info.auth_code
        # request.saxobank_auth_info.redirect_uri,
        # need_refresh=request.saxobank_auth_info.need_refresh,
    )
    logger.debug(f"def exit.")
    return auth_pb2.IsAuthenticatedResponse(is_authenticated=True)
