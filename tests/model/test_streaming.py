from json import loads

from saxobank.converter import as_request, from_response
from saxobank.model import streaming
from saxobank.model.common import HeartbeatReason, ReferenceId

exp_Heartbeats = {"OriginatingReferenceId": "IP44964", "Reason": "NoNewData"}
mdl_Heartbeats = streaming.Heartbeats(**exp_Heartbeats)


def test_Heartbeats_serialize() -> None:
    assert exp_Heartbeats == as_request(mdl_Heartbeats)


def test_Heartbeats_deserialize() -> None:
    assert from_response(exp_Heartbeats, streaming.Heartbeats) == mdl_Heartbeats
