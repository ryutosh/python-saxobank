from __future__ import annotations

from datetime import datetime

from aiohttp import ClientSession
from endpoint import Endpoint
from user_session import UserSession

from saxobank.models import SaxobankModel, SaxobankPagedRequestMoel
from saxobank.models import enums as e
import saxobank
from saxobank.models import port


session: UserSession


class OrdersReq(SaxobankPagedRequestMoel):
    FieldGroups: list[e.OrderFieldGroup] | None
    PriceMode: e.PriceMode | None

    class Config:
        use_enum_values = True


class PositionsReq(SaxobankModel):
    PositionId: str


class PositionsRes(SaxobankModel):
    PositionId: str


async def positions_positionid(
    request_model: port.PositionsPositionIdReq, effectual_until: datetime | None = None, access_token: str | None = None
) -> port.PositionsRes:
    # Send request
    task = session.http.get(
        session._full_url(Endpoint.PORT_POSITIONS.url),
        data=request_model.dict(exclude_unset=True),
        headers=session._auth_header(access_token),
    )

    await session._boiler(task, Endpoint.PORT_POSITIONS, effectual_until)

    request_coro = saxobank_request_dispatcher.request_endpoint(
        winko_id,
        endpoints.PORT_POSITIONS,
        data=req,
        path_conv=path_conv,
        effectual_until=effectual_until,
    )
    return await request_template(request_coro, models.PositionsMeResponse)
