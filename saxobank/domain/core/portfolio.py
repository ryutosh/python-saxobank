from __future__ import annotations

from datetime import datetime

from aiohttp import ClientSession
from endpoint import Endpoint
from user_session import UserSession

import saxobank
from saxobank.models import SaxobankModel, SaxobankPagedRequestMoel
from saxobank.models import enums as e
from saxobank.models import port

session: UserSession


async def positions_positionid(
    request_model: port.PositionsPositionIdReq, effectual_until: datetime | None = None, access_token: str | None = None
) -> port.PositionsRes:
    # Send request

    request_task = session.http.get(
        Endpoint.PORT_POSITIONS_POSITION_ID.url(session.base_url, request_model.path_items()),
        data=request_model.dict(exclude_unset=True),
        headers=session._auth_header(access_token),
    )

    await session._boiler(request_task, Endpoint.PORT_POSITIONS, effectual_until)

    return await request_template(request_coro, models.PositionsMeResponse)
