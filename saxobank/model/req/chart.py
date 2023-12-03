"""Request models used chart/charts service.


"""

from dataclasses import KW_ONLY, dataclass
from datetime import datetime
from typing import ClassVar

from ... import model
from .. import chart, common
from ..base import SaxobankModel2, ommit_datetime_zero


@dataclass
class GetChartCharts(SaxobankModel2):
    """Request model for [`saxobank.application.Client.get_chart_charts`][]

    *See [OpenAPI Reference](https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/getchartdataasync/387cfc61d3292d9237095b9144ac4733) for original info.*

    Attributes:
        AssetType: Assettype of the instrument.
        Uic: UIC (Universal Instrument Code) of the instrument.
        Horizon: The time period that each sample covers. Values are interpreted in minutes: 1, 5, 10, 15, 30, 60, 120, 240, 360, 480, 1440, 10080, 43200.
        Mode: If Time is supplied, mode specifies if the endpoint should returns samples "UpTo" (and including) or "From" (and including) the specified time.
        Time: Specifies the time of a sample, which must either be the first (If Mode=="From") or the last (if Mode=="UpTo") in the returned data.
        Count: Specifies maximum number of samples to return. Maximum is 1200. If not specified a default of 1200 samples are returned.
        FieldGroups: Use FieldGroups to add additional information to the samples like display/formatting details or information about the price source. If FieldGroups are not specified in the request then the response defaults to only hold the bare OHLC samples and nothing else.

    """

    _: KW_ONLY
    AssetType: model.common.AssetType | str
    Uic: int
    Horizon: int
    Mode: common.ChartRequestMode | str | None = None
    Time: datetime | str | None = None
    Count: int | None = None
    FieldGroups: list[chart.charts.ChartFieldGroupSpec] | list[str] | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

        if not isinstance(self.AssetType, common.AssetType):
            self.AssetType = common.AssetType(self.AssetType)
        if self.Mode and not isinstance(self.Mode, common.ChartRequestMode):
            self.Mode = common.ChartRequestMode(self.Mode)
        if self.Time and not isinstance(self.Time, datetime):
            self.Time = ommit_datetime_zero(self.Time)

