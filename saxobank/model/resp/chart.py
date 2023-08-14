"""Response models used chart/charts service.


"""

from dataclasses import dataclass
from typing import Any, cast

from ... import model
from ..base import SaxobankModel2


@dataclass
class GetChartChartsResp(SaxobankModel2):
    """Response model for [`saxobank.application.Client.get_chart_charts`][]

    *See [OpenAPI Reference](https://www.developer.saxo/openapi/referencedocs/chart/v1/charts/getchartdataasync/387cfc61d3292d9237095b9144ac4733) for original info.*

    Attributes:
        ChartInfo: Object holding information about the OHLC samples such as the exchange id of the price source, when the first sample begins, the horizon in minutes and how long the samples are delayed by.
        Data: Array holding the individual OHLC samples. For Forex Instruments both Bid and Ask values are returned. For other instruments the values are the last traded values.
        DataVersion: This field holds a version number of the data.
        DisplayAndFormat: Object holding information relevant to displaying the instrument and formatting the samples for charting it. Currently holds the symbol of the instrument, how many decimals samples have, a description of the instrument and what currency it is traded in.
    """

    ChartInfo: model.chart.charts.ChartInfo | dict[str, Any]
    Data: list[model.chart.charts.ChartSample] | list[dict[str, Any]]
    DataVersion: int
    # DisplayAndFormat: model.common.Dis | str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.ChartInfo and not isinstance(self.ChartInfo, model.chart.charts.ChartInfo):
            self.ChartInfo = model.chart.charts.ChartInfo(**self.ChartInfo)
        if self.Data and any(
            (not isinstance(member, model.chart.charts.ChartSample) for member in self.Data)
        ):
            self.Data = [
                model.chart.charts.ChartSample(**member)
                for member in cast(list[dict[str, Any]], self.Data)
            ]
