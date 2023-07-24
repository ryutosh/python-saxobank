from json import loads

from saxobank.model.chart import charts
from saxobank.model.common import AssetType, ChartRequestMode


def test_GetReq() -> None:
    # exp = loads('{"AssetType": "CfdOnIndex", "Uic": 1924, "Horizon": 100, "Mode": "UpTo"}')
    mdl = charts.GetReq(
        asset_type=AssetType.CfdOnIndex,
        uic=1924,
        horizon=100,
        mode=ChartRequestMode.UpTo,
    )
    # mdl = streaming.Heartbeats.model_validate(exp)
    assert mdl.AssetType == "CfdOnIndex" and mdl.Horizon == 100
