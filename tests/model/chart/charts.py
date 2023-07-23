from json import loads

from saxobank.model.chart import charts


def test_GetReq() -> None:
    # exp = loads('{"OriginatingReferenceId": "IP44964", "Reason": "NoNewData"}')
    mdl = charts.GetReq()
    # mdl = streaming.Heartbeats.model_validate(exp)
    # assert mdl.OriginatingReferenceId == 'IP44964' and mdl.Reason == 'NoNewData'
