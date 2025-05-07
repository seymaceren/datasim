from abc import ABC
from typing import Any, List, Optional, cast
from pandas import DataFrame
from plotly.graph_objs._figure import Figure

import numpy as np
import plotly.express as px
import streamlit as st

from .dashboard import Dashboard
from .entity import Entity
from .queue import Queue
from .resource import Resource
from .types import PlotType
import datasim.simulation as simulation


class PlotData(ABC):
    """Abstract superclass of different types of data to plot."""

    plot_type: PlotType
    title: Optional[str]
    trace: Optional[Figure] = None
    dashboard: Optional[Dashboard] = None
    plot: Optional[Any] = None
    legend_x: str
    legend_y: str

    def __init__(
        self,
        plot_type: PlotType,
        title: Optional[str],
        legend_x: str = "x",
        legend_y: str = "y",
    ):
        """Create a data source to plot from.

        Args:
            plot_type ("scatter", "line", "bar", "pie"): Type of plot to render.
            title (str, optional): Title to use over the plot. Defaults to None.
        """
        self.plot_type = plot_type
        self.title = title
        self.legend_x = legend_x
        self.legend_y = legend_y

        self._buffer_size = max(10000, simulation.end_tick)
        self._buffer_index = 0
        self._x_buffer = np.zeros(self._buffer_size)
        self._y_buffer = np.zeros(self._buffer_size)

    @property
    def _data_frame(self):
        return DataFrame(
            {
                self.legend_x: self._x_buffer[: self._buffer_index],
                self.legend_y: self._y_buffer[: self._buffer_index],
            }
        )

    def _update_traces(self):
        if self.dashboard is None:
            if "dashboard" in st.session_state:
                self.dashboard = cast(Dashboard, st.session_state.dashboard)

        if self.dashboard is None:
            return

        match self.plot_type:
            case PlotType.bar:
                self.trace = cast(
                    Figure,
                    px.bar(
                        self._data_frame,
                        title=self.title,
                        x=self.legend_x,
                        y=self.legend_y,
                    ),
                )
            case PlotType.line:
                self.trace = cast(
                    Figure,
                    px.line(
                        self._data_frame,
                        title=self.title,
                        x=self.legend_x,
                        y=self.legend_y,
                    ),
                )
            case PlotType.pie:
                self.trace = cast(
                    Figure,
                    px.pie(
                        self._data_frame,
                        title=self.title,
                        names=self.legend_x,
                        values=self.legend_y,
                    ),
                )
            case PlotType.scatter:
                self.trace = cast(
                    Figure,
                    px.scatter(
                        self._data_frame,
                        x=self.legend_x,
                        y=self.legend_y,
                        title=self.title,
                    ),
                )

        if (
            self.plot
            and self.plot.id not in self.dashboard.plots
            and self.trace is not None
        ):
            self.dashboard.plots[self.plot.id] = self.trace

    def _tick(self):
        pass


class XYPlotData(PlotData):
    """Data with x and y values as float."""

    def __init__(
        self,
        data_x: List[float] = [],
        data_y: List[float] = [],
        plot_type: PlotType = PlotType.line,
        title: Optional[str] = None,
        legend_x: str = "x",
        legend_y: str = "y",
    ):
        """Create a data source from x and y lists of floats.

        Args:
            data_x (List[float], optional): x values. Defaults to [] to start with an empty data set.
            data_y (List[float], optional): y values. Defaults to [] to start with an empty data set.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        super().__init__(plot_type, title, legend_x, legend_y)
        self._x_buffer[: len(data_x)] = data_x
        self._y_buffer[: len(data_y)] = data_y

    def append(self, x: float, y: float):
        """Add a data point to this data set.

        Args:
            x (float): x value of the data point.
            y (float): y value of the data point.
        """
        if len(self._x_buffer) <= self._buffer_index:
            self._x_buffer = np.append(self._x_buffer, np.zeros(self._buffer_size))
            self._y_buffer = np.append(self._y_buffer, np.zeros(self._buffer_size))
        self._x_buffer[self._buffer_index] = x
        self._y_buffer[self._buffer_index] = y
        self._buffer_index += 1


class CategoryPlotData(PlotData):
    """Data with named categories with float values."""

    labels: List[str]
    values: List[float]

    def __init__(
        self,
        data_x: List[str] = [],
        data_y: List[float] = [],
        plot_type: PlotType = PlotType.line,
        title: Optional[str] = None,
        legend_x: str = "category",
        legend_y: str = "value",
    ):
        """Create a data source from x as categories and y as float values.

        Args:
            data_x (List[str], optional): labels. Defaults to [] to start with an empty data set.
            data_y (List[float], optional): values for each label. Defaults to [] to start with an empty data set.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        super().__init__(plot_type, title, legend_x, legend_y)
        self.data_x = data_x
        self.data_y = data_y

    def append(self, label: str, value: float):
        """Add a data point to this data set.

        Args:
            label (str): label of the data point.
            value (float): value of the data point.
        """
        # self.labels.append(label)
        # self.values.append(value)
        # TODO


class NPPlotData(PlotData):
    """Data with Numpy array as source."""

    data: np.ndarray

    def __init__(
        self,
        data: np.ndarray,
        plot_type: PlotType = PlotType.line,
        title: Optional[str] = None,
        legend_x: str = "x",
        legend_y: str = "y",
    ):
        """Create a data source from a Numpy array.

        Args:
            data (:class:`np.ndarray`): Array of data points. Shape should correspond to the dimensions of the plot
                (2 columns for 2D plots, 3 columns for 3D plots).
            plot_type (:class:`PlotType`, optional): Type of plot to show. Defaults to `"line"`.
            title (`str`, optional): Title to use over the plot. Defaults to `None`.

        Raises:
            `TypeError`: When trying to take from a capacity resource without specifying an amount.
        """
        super().__init__(plot_type, title, legend_x, legend_y)
        if data.shape[1] != 2:  # TODO add 3 when adding 3D plots
            raise ValueError("")
        self.data = data

    @property
    def _data_frame(self):
        return DataFrame(
            {
                self.legend_x: self.data[0],
                self.legend_y: self.data[1],
            }
        )


class ResourcePlotData(PlotData):
    """Data source from watching the amount of a :class:`Resource`."""

    source: Resource
    plot_users: bool
    frequency: int

    def __init__(
        self,
        source_id: str,
        plot_users: bool = False,
        frequency: int = 1,
        plot_type: PlotType = PlotType.line,
        title: Optional[str] = None,
        legend_x: str = "seconds",
        legend_y: str = "amount",
    ):
        """Create a data source from watching the amount of a :class:`Resource`.

        Args:
            data (:class:`Resource`): Source :class:`Resource`.
            frequency (int, optional): Frequency in ticks to add data points.
                Defaults to 1, meaning a point gets added every tick.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        super().__init__(plot_type, title, legend_x, legend_y)
        self.source = simulation.world().resource(source_id)
        self.plot_users = plot_users
        self.frequency = frequency

    def _tick(self):
        if (self.frequency == 0 and self.source.changed_tick == simulation.ticks) or (
            simulation.ticks % self.frequency == 0
        ):
            if len(self._x_buffer) <= self._buffer_index:
                self._x_buffer = np.append(self._x_buffer, np.zeros(self._buffer_size))
                self._y_buffer = np.append(self._y_buffer, np.zeros(self._buffer_size))
            self._x_buffer[self._buffer_index] = simulation.time
            self._y_buffer[self._buffer_index] = (
                len(self.source.users) if self.plot_users else self.source.amount
            )
            self._buffer_index += 1


class QueuePlotData(PlotData):
    """Data source from watching the size of a :class:`Queue`."""

    source: Queue
    frequency: int

    def __init__(
        self,
        source_id: str,
        frequency: int = 1,
        plot_type: PlotType = PlotType.line,
        title: Optional[str] = None,
        legend_x: str = "seconds",
        legend_y: str = "length",
    ):
        """Create a data source from watching the size of a :class:`Queue`.

        Args:
            data (:class:`Queue`): Source :class:`Queue`.
            frequency (int, optional): Frequency in ticks to add data points.
                Defaults to 1, meaning a point gets added every tick.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        super().__init__(plot_type, title, legend_x, legend_y)
        self.source = simulation.world().queue(source_id)
        self.frequency = frequency

    def _tick(self):
        if (self.frequency == 0 and self.source.changed_tick == simulation.ticks) or (
            simulation.ticks % self.frequency == 0
        ):
            if len(self._x_buffer) <= self._buffer_index:
                self._x_buffer = np.append(self._x_buffer, np.zeros(self._buffer_size))
                self._y_buffer = np.append(self._y_buffer, np.zeros(self._buffer_size))
            self._x_buffer[self._buffer_index] = simulation.time
            self._y_buffer[self._buffer_index] = len(self.source)
            self._buffer_index += 1


class StatePlotData(PlotData):
    """Data source from watching the state of an :class:`Entity`."""

    data: Entity
    frequency: int

    def __init__(
        self,
        data: Entity,
        frequency: int = 1,
        plot_type: PlotType = PlotType.line,
        title: Optional[str] = None,
    ):
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

        # TODO


class Plot:
    """Base class for easily updating data for plots to be made on the dashboard."""

    id: str
    title: Optional[str]
    figure: Figure
    data: List[PlotData]

    def __init__(self, id: str, *args: PlotData):
        """Create a plot to add to the dashboard using `World.add_plot()`.

        Args:
            id (str): identifier, needs to be unique.
            *args (:class:`PlotData`): Data to start the plot with.
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

    def _tick(self):
        for data in self.data:
            data._tick()

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
