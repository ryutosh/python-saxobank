from datetime import datetime
from json import loads
from typing import cast

from saxobank.model.chart import charts
from saxobank.model.common import AssetType, ChartRequestMode


def test_GetReq() -> None:
    # exp = loads('{"AssetType": "CfdOnIndex", "Uic": 1924, "Horizon": 100, "Mode": "UpTo"}')
    # mdl = charts.SamplePydanticDataclass(
    # mdl = charts.SamplePydanticModel(
    # mdl = charts.SampleAttrs(
    mdl = charts.SampleStandardDataclass(
        Horizon=100,
        Mode=ChartRequestMode.UpTo,
    )
    # mdl = streaming.Heartbeats.model_validate(exp)
    assert and mdl.Horizon == 100


def test_GetResp() -> None:
    # exp = loads('{"AssetType": "CfdOnIndex", "Uic": 1924, "Horizon": 100, "Mode": "UpTo"}')
    mdl = charts.GetResp(
        # Data=charts.Data(
        #     _root=[
        #         charts.ChartSample(CloseAsk=12.0, CloseBid=12.3, Time=datetime.now()),
        #         charts.ChartSample(CloseAsk=13.1, CloseBid=13.4, Time=datetime.now()),
        #     ],
        # ),
        DataVersion=100,
        ChartInfo=charts.ChartInfo(ExchangeId="NYSE", Horizon=110),
    )
    # mdl = streaming.Heartbeats.model_validate(exp)
    assert (
        cast(charts.ChartInfo, mdl.ChartInfo).ExchangeId == "NYSE"
        and mdl.DataVersion == 100
    )
