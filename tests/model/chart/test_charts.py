from datetime import datetime
from json import loads
from typing import cast

from saxobank.converter import as_request, from_response
from saxobank.model.chart import charts
from saxobank.model.common import AssetType, ChartRequestMode


def test_GetReq() -> None:
    exp = loads(
        '{"AssetType": "CfdOnIndex", "Uic": 1924, "Horizon": 100, "Mode": "UpTo"}'
    )

    mdl = charts.GetReq(**exp)
    assert mdl.Horizon == 100


now = datetime.now()
mdl = charts.GetResp(
    DataVersion=100,
    ChartInfo={
        "DelayedByMinutes": 15,
        "ExchangeId": "NYSE",
        "FirstSampleTime": now,
        "Horizon": 100,
    },
)
mdl2 = charts.GetResp(
    DataVersion=100,
    ChartInfo=charts.ChartInfo(
        DelayedByMinutes=15,
        ExchangeId="NYSE",
        FirstSampleTime=now,
        Horizon=100,
    ),
)

exp = {
    "DataVersion": 100,
    "ChartInfo": {
        "DelayedByMinutes": 15,
        "ExchangeId": "NYSE",
        "FirstSampleTime": now.isoformat(),
        "Horizon": 100,
    },
}


def test_GetResp_serialize() -> None:
    assert exp == as_request(mdl) == as_request(mdl2)


def test_GetResp_deserialize() -> None:
    assert from_response(exp, charts.GetResp) == mdl == mdl2


def test_ChartSample_serialize() -> None:
    pass
