from saxobank.model import streaming
from json import loads

def test_Heartbeats() -> None:
    exp = loads('{"OriginatingReferenceId": "IP44964", "Reason": "NoNewData"}')
    mdl = streaming.Heartbeats.model_validate(exp)
    assert mdl.OriginatingReferenceId == 'IP44964' and mdl.Reason == 'NoNewData'
