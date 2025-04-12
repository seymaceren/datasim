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

type PLOT_TYPE = Literal["scatter", "line", "bar", "pie"]

type PlotObj = Optional[Plot]


class PlotData(ABC):
    """TODO: write.

    Args:
        ABC (_type_): _description_
    """

    plot: PlotObj = None
    plot_type: PLOT_TYPE
    title: Optional[str]
    trace: Optional[Figure] = None
    dashboard: Optional[Dashboard] = None

    def __init__(self, plot_type: PLOT_TYPE, title: Optional[str]):
        """TODO: write.

        Args:
            plot_type ("scatter", "line", "bar", "pie", optional): Type or chart to plot.
            title (str, optional): Title to use over the plot.
        """
        self.plot_type = plot_type
        self.title = title

    def _update_traces(self):
        if self.dashboard is None:
            if "dashboard" in st.session_state:
                self.dashboard = cast(Dashboard, st.session_state.dashboard)


class XYPlotData(PlotData):
    """TODO: write.

    Args:
        PlotData (_type_): _description_
    """

    data_x: List[float]
    data_y: List[float]

    def __init__(self, data_x: List[float] = [], data_y: List[float] = [],
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """TODO: write.

        Args:
            data_x (List[float], optional): _description_. Defaults to [].
            data_y (List[float], optional): _description_. Defaults to [].
            plot_type (PLOT_TYPE, optional): _description_. Defaults to "line".
            title (Optional[str], optional): _description_. Defaults to None.
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
    """TODO: write.

    Args:
        PlotData (_type_): _description_
    """

    labels: List[str]
    values: List[float]

    def __init__(self, data_x: List[str] = [], data_y: List[float] = [],
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """TODO: write.

        Args:
            data_x (List[str], optional): _description_. Defaults to [].
            data_y (List[float], optional): _description_. Defaults to [].
            plot_type (PLOT_TYPE, optional): _description_. Defaults to "line".
            title (Optional[str], optional): _description_. Defaults to None.
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
    """TODO: write.

    Args:
        PlotData (_type_): _description_
    """

    data: ndarray

    def __init__(self, data: ndarray,
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """TODO: write.

        Args:
            data (ndarray): _description_
            plot_type (PLOT_TYPE, optional): _description_. Defaults to "line".
            title (Optional[str], optional): _description_. Defaults to None.
        """
        super().__init__(plot_type, title)
        self.data = data


class ResourcePlotData(PlotData):
    """TODO: write.

    Args:
        PlotData (_type_): _description_
    """

    data: Resource
    frequency: int

    def __init__(self, data: Resource, frequency: int = 1,
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """TODO: write.

        Args:
            data (Resource): _description_
            frequency (int, optional): _description_. Defaults to 1.
            plot_type (PLOT_TYPE, optional): _description_. Defaults to "line".
            title (Optional[str], optional): _description_. Defaults to None.
        """
        super().__init__(plot_type, title)
        self.data = data
        self.frequency = frequency


class QueuePlotData(PlotData):
    """TODO: write.

    Args:
        PlotData (_type_): _description_
    """

    data: Queue
    frequency: int

    def __init__(self, data: Queue, frequency: int = 1,
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """TODO: write.

        Args:
            data (Queue): _description_
            frequency (int, optional): _description_. Defaults to 1.
            plot_type (PLOT_TYPE, optional): _description_. Defaults to "line".
            title (Optional[str], optional): _description_. Defaults to None.
        """
        super().__init__(plot_type, title)
        self.data = data
        self.frequency = frequency


class StatePlotData(PlotData):
    """TODO: write.

    Args:
        PlotData (_type_): _description_
    """

    data: Entity
    frequency: int

    def __init__(self, data: Entity, frequency: int = 1,
                 plot_type: PLOT_TYPE = "line", title: Optional[str] = None):
        """TODO: write.

        Args:
            data (Entity): _description_
            frequency (int, optional): _description_. Defaults to 1.
            plot_type (PLOT_TYPE, optional): _description_. Defaults to "line".
            title (Optional[str], optional): _description_. Defaults to None.
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
