from abc import ABC
from typing import Any, List, Literal, Optional, cast
from numpy import ndarray
from plotly.graph_objs._figure import Figure

import plotly.express as px
import streamlit as st

from .entity import Entity
from .queue import Queue
from .resource import Resource

from .dashboard import Dashboard

type PLOT_TYPE = Literal["scatter", "line", "bar", "pie"]


class PlotData(ABC):
    """Abstract superclass of different types of data to plot."""

    plot_type: PLOT_TYPE
    title: Optional[str]
    trace: Optional[Figure] = None
    dashboard: Optional[Dashboard] = None
    plot: Optional[Any] = None

    def __init__(self, plot_type: PLOT_TYPE, title: Optional[str]):
        """Create a data source to plot from.

        Args:
            plot_type ("scatter", "line", "bar", "pie"): Type or chart to plot.
            title (str, optional): Title to use over the plot. Defaults to None.
        """
        self.plot_type = plot_type
        self.title = title

    def _update_traces(self):
        if self.dashboard is None:
            if "dashboard" in st.session_state:
                self.dashboard = cast(Dashboard, st.session_state.dashboard)


class XYPlotData(PlotData):
    """Data with x and y values as float."""

    data_x: List[float]
    data_y: List[float]

    def __init__(self, data_x: List[float] = [], data_y: List[float] = [],
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """Create a data source from x and y lists of floats.

        Args:
            data_x (List[float], optional): x values. Defaults to [] to start with an empty data set.
            data_y (List[float], optional): y values. Defaults to [] to start with an empty data set.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        super().__init__(plot_type, title)
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

    def _update_traces(self):
        super()._update_traces()

        if self.dashboard is None:
            return

        if len(self.data_x) > 0:
            if not self.trace:
                match self.plot_type:
                    case "bar":
                        pass
                    case "line":
                        self.trace = cast(
                            Figure,
                            px.line(x=self.data_x, y=self.data_y,
                                    markers=True, title=self.title))
                    case "pie":
                        pass
                    case "scatter":
                        self.trace = cast(
                            Figure,
                            px.scatter(x=self.data_x, y=self.data_y,
                                       title=self.title))
            else:
                self.trace.update_traces(x=self.data_x, y=self.data_y)

            if self.plot and self.plot.id not in self.dashboard.plots and self.trace is not None:
                self.dashboard.plots[self.plot.id] = self.trace


class CategoryPlotData(PlotData):
    """Data with named categories with float values."""

    labels: List[str]
    values: List[float]

    def __init__(self, data_x: List[str] = [], data_y: List[float] = [],
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """Create a data source from x as categories and y as float values.

        Args:
            data_x (List[str], optional): labels. Defaults to [] to start with an empty data set.
            data_y (List[float], optional): values for each label. Defaults to [] to start with an empty data set.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        super().__init__(plot_type, title)
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
    """Data with Numpy array as source."""

    data: ndarray

    def __init__(self, data: ndarray,
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """Create a data source from a Numpy array.

        Args:
            data (ndarray): Array of data points. Shape should correspond to the dimensions of the plot.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        super().__init__(plot_type, title)
        self.data = data


class ResourcePlotData(PlotData):
    """Data source from watching the amount of a :class:`Resource`."""

    data: Resource
    frequency: int

    def __init__(self, data: Resource, frequency: int = 1,
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """Create a data source from watching the amount of a :class:`Resource`.

        Args:
            data (:class:`Resource`): Source :class:`Resource`.
            frequency (int, optional): Frequency in ticks to add data points.
                Defaults to 1, meaning a point gets added every tick.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        super().__init__(plot_type, title)
        self.data = data
        self.frequency = frequency


class QueuePlotData(PlotData):
    """Data source from watching the size of a :class:`Queue`."""

    data: Queue
    frequency: int

    def __init__(self, data: Queue, frequency: int = 1,
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """Create a data source from watching the size of a :class:`Queue`.

        Args:
            data (:class:`Queue`): Source :class:`Queue`.
            frequency (int, optional): Frequency in ticks to add data points.
                Defaults to 1, meaning a point gets added every tick.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        super().__init__(plot_type, title)
        self.data = data
        self.frequency = frequency


class StatePlotData(PlotData):
    """Data source from watching the state of an :class:`Entity`."""

    data: Entity
    frequency: int

    def __init__(self, data: Entity, frequency: int = 1,
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """Create a data source from watching the state of an :class:`Entity`.

        Args:
            data (:class:`Entity`): Source :class:`Entity`.
            frequency (int, optional): Frequency in ticks to add data points.
                Defaults to 1, meaning a point gets added every tick.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        super().__init__(plot_type, title)
        self.data = data
        self.frequency = frequency


class Plot():
    """Base class for easily updating data for plots to be made on the dashboard."""

    id: str
    title: Optional[str]
    figure: Figure
    data: List[PlotData]

    def __init__(self, id: str, *args: PlotData):
        """Create a plot to add to the dashboard using `World.add_plot()`.

        Args:
            id (str): identifier, needs to be unique.
            *args (PlotData): Data to start the plot with.
        """
        self.id = id
        self.data = []
        for arg in args:
            self.add_trace(arg)

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
        data.plot = self
        self.data.append(data)
        return index

    def _update(self):
        for data in self.data:
            data._update_traces()
