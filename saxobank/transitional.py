from logging import getLogger
from typing import List

# --
from winko import exceptions

from . import models
from . import request as saxo_req

# from winko. import dispatcher
log = getLogger(__name__)

"""
This module containing transitional functions will be removed in future releases bundling more proper way.
"""


async def position_id(winko_id, order_id) -> List[int]:
    """
    Returns position id which sourced from specified order id.
    """

    # --------------------------
    # Make positions request
    positions_req = models.PositionsMeRequest(FieldGroups=[models.PositionFieldGroup.PositionBase]).dict(exclude_unset=True)

    # Send positions request
    try:
        status, positions_res = await saxo_req.positions_me(winko_id, positions_req, effectual_until=None)
    except exceptions.RequestError:
        raise exceptions.OrderError()

    # Return found position ids
    return [x.PositionId for x in positions_res.find_order_id(order_id)]
