from abc import ABC
from typing import List, Literal, Optional, cast
from numpy import ndarray
from plotly.graph_objs._figure import Figure
import plotly.express as px
import streamlit as st

from .entity import Entity
from .queue import Queue
from .resource import Resource

from .dashboard import Dashboard

PLOT_TYPE = Literal["scatter", "line", "bar", "pie"]


class PlotData(ABC):
    def __init__(self, plot_type: PLOT_TYPE = "line"):
        self.plot_type = plot_type


class XYPlotData(PlotData):
    data_x: List[float]
    data_y: List[float]

    def __init__(self, data_x: List[float] = [], data_y: List[float] = [], plot_type: PLOT_TYPE = "line"):
        super().__init__(plot_type)
        self.data_x = data_x
        self.data_y = data_y

    def append(self, x: float, y: float):
        """Add a data point to this data set.

        Args:
            x (float): x value of the data point.
            y (float): y value of the data point.
        """
        self.data_x.append(x)
        self.data_y.append(y)


class CategoryPlotData(PlotData):
    labels: List[str]
    values: List[float]

    def __init__(self, data_x: List[str] = [], data_y: List[float] = [], plot_type: PLOT_TYPE = "line"):
        super().__init__(plot_type)
        self.data_x = data_x
        self.data_y = data_y

    def append(self, label: str, value: float):
        """Add a data point to this data set.

        Args:
            label (str): label of the data point.
            value (float): value of the data point.
        """
        self.labels.append(label)
        self.values.append(value)


class NPPlotData(PlotData):
    data: ndarray

    def __init__(self, data: ndarray, plot_type: PLOT_TYPE = "line"):
        super().__init__(plot_type)
        self.data = data


class ResourcePlotData(PlotData):
    data: Resource
    frequency: int

    def __init__(self, data: Resource, frequency: int = 1, plot_type: PLOT_TYPE = "line"):
        super().__init__(plot_type)
        self.data = data
        self.frequency = frequency


class QueuePlotData(PlotData):
    data: Queue
    frequency: int

    def __init__(self, data: Queue, frequency: int = 1, plot_type: PLOT_TYPE = "line"):
        super().__init__(plot_type)
        self.data = data
        self.frequency = frequency


class StatePlotData(PlotData):
    data: Entity
    frequency: int

    def __init__(self, data: Entity, frequency: int = 1, plot_type: PLOT_TYPE = "line"):
        super().__init__(plot_type)
        self.data = data
        self.frequency = frequency


class Plot():
    """Base class for easily updating data for plots to be made on the dashboard."""

    id: str
    title: Optional[str]
    figure: Figure
    data: List[PlotData]
    traces: List[Optional[Figure]]

    def __init__(self, id: str, title: Optional[str] = None,
                 *args: PlotData):
        """Create a plot to add to the dashboard using `World.add_plot()`.

        Args:
            id (str): identifier, needs to be unique.
            title (str, optional): Title to use over the plot. Defaults to None.
            *args (tuple(list[float] | list[str], list[float], Literal["scatter", "line", "bar", "pie"])):
                traces to start the plot with.
        """
        self.id = id
        self.title = title
        self.data = list(args)
        self.traces = [None for _ in args]

    def __getitem__(self, key: int) -> PlotData:
        """Get a reference to a data set from this plot.

        Args:
            key (int): Index of the data set.

        Returns:
            tuple(list[float] | list[str], list[float]): Data set at index.
        """
        return self.data[key]

    def add_trace(self, data: PlotData) -> int:
        """Add a data trace to the plot.

        Args:
            data (PlotData): Data set.

        Returns:
            int: Index of the added data set.
        """
        index: int = len(self.data)
        self.data.append(data)
        self.traces.append(None)
        return index

    def _update(self, dashboard: Optional[Dashboard] = None):
        if dashboard is None:
            if "dashboard" in st.session_state:
                dashboard = cast(Dashboard, st.session_state.dashboard)
            else:
                return
        i: int = 0
        for data in self.data:
            if len(data_x) > 0:
                trace = self.traces[i]
                if not trace:
                    match self.types[i]:
                        case "bar":
                            pass
                        case "line":
                            self.traces[i] = cast(
                                Figure,
                                px.line(x=data_x, y=data_y,
                                        markers=True, title=self.title))
                        case "pie":
                            pass
                        case "scatter":
                            self.traces[i] = cast(
                                Figure,
                                px.scatter(x=data_x, y=data_y,
                                           title=self.title))
                else:
                    trace.update_traces(x=data_x, y=data_y)

                trace = self.traces[i]
                if self.id not in dashboard.plots and trace is not None:
                    dashboard.plots[self.id] = trace
            i += 1
