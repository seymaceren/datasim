from abc import ABC
from typing import Any, List, Optional
from pandas import DataFrame
from plotly.graph_objs._figure import Figure
from plotly.subplots import make_subplots
from plotly.colors import convert_colors_to_same_type, unlabel_rgb

import numpy as np
import plotly.express as px
from webcolors import name_to_rgb

from .dashboard import Dashboard
from .entity import Entity
from .queue import Queue
from .resource import Resource
from .types import PlotOptions, PlotType
import datasim.simulation as simulation


class PlotData(ABC):
    """Abstract superclass of different types of data to plot."""

    trace: Optional[Figure] = None
    plot: Optional[Any] = None
    plot_index: Optional[int] = 0
    options: PlotOptions

    def __init__(
        self,
        options: PlotOptions = PlotOptions(),
    ):
        """Create a data source to plot from.

        Args:
            plot_type ("scatter", "line", "bar", "pie"): Type of plot to render.
            title (str, optional): Title to use over the plot. Defaults to None.
        """
        if options.legend_x == "":
            options.legend_x = "x"
        if options.legend_y == "":
            options.legend_y = "y"
        if options.plot_type is None:
            options.plot_type = PlotType.line
        self.options = options

        self._buffer_size = max(10000, simulation.end_tick)
        self._buffer_index = 0
        self._x_buffer = np.zeros(self._buffer_size)
        self._y_buffer = np.zeros(self._buffer_size)

    @property
    def _data_frame(self):
        return DataFrame(
            {
                self.options.legend_x: self._x_buffer[: self._buffer_index],
                self.options.legend_y: self._y_buffer[: self._buffer_index],
            }
        )

    def _update_trace(self):
        match self.options.plot_type:
            case PlotType.bar:
                self.trace = px.bar(
                    self._data_frame,
                    title=self.options.title,
                    x=self.options.legend_x,
                    y=self.options.legend_y,
                    color=self.options.color,
                    color_continuous_scale=self.options.color_continuous_scale,
                    color_continuous_midpoint=self.options.color_continuous_midpoint,
                    color_discrete_map=self.options.color_discrete_map,
                    color_discrete_sequence=self.options.color_discrete_sequence,
                    range_color=self.options.range_color,
                    hover_name=self.options.hover_name,
                    hover_data=self.options.hover_data,
                    custom_data=self.options.custom_data,
                    text=self.options.text,
                    facet_row=self.options.facet_row,
                    facet_col=self.options.facet_col,
                    facet_row_spacing=self.options.facet_row_spacing,
                    facet_col_spacing=self.options.facet_col_spacing,
                    facet_col_wrap=self.options.facet_col_wrap,
                    error_x=self.options.error_x,
                    error_y=self.options.error_y,
                    error_x_minus=self.options.error_x_minus,
                    error_y_minus=self.options.error_y_minus,
                    category_orders=self.options.category_orders,
                    labels=(
                        self.options.labels
                        or {self.options.legend_y: self.options.name}
                    ),
                    orientation=self.options.orientation,
                    opacity=self.options.opacity,
                    log_x=self.options.log_x,
                    log_y=self.options.log_y,
                    range_x=self.options.range_x,
                    range_y=self.options.range_y,
                    pattern_shape=self.options.pattern_shape,
                    pattern_shape_map=self.options.pattern_shape_map,
                    pattern_shape_sequence=self.options.pattern_shape_sequence,
                    base=self.options.base,
                    barmode=self.options.barmode,
                    text_auto=self.options.text_auto,
                    template=self.options.template,
                    width=self.options.width,
                    height=self.options.height,
                    animation_frame=self.options.animation_frame,
                    animation_group=self.options.animation_group,
                )
                if self.options.secondary_y:
                    self.trace.update_yaxes(secondary_y=True)
                    self.trace.update_traces(yaxis="y2")
            case PlotType.line:
                self.trace = px.line(
                    self._data_frame,
                    title=self.options.title,
                    x=self.options.legend_x,
                    y=self.options.legend_y,
                    color=self.options.color,
                    color_discrete_map=self.options.color_discrete_map,
                    color_discrete_sequence=self.options.color_discrete_sequence,
                    symbol=self.options.symbol,
                    symbol_map=self.options.symbol_map,
                    symbol_sequence=self.options.symbol_sequence,
                    hover_name=self.options.hover_name,
                    hover_data=self.options.hover_data,
                    custom_data=self.options.custom_data,
                    text=self.options.text,
                    facet_row=self.options.facet_row,
                    facet_col=self.options.facet_col,
                    facet_row_spacing=self.options.facet_row_spacing,
                    facet_col_spacing=self.options.facet_col_spacing,
                    facet_col_wrap=self.options.facet_col_wrap,
                    error_x=self.options.error_x,
                    error_y=self.options.error_y,
                    error_x_minus=self.options.error_x_minus,
                    error_y_minus=self.options.error_y_minus,
                    category_orders=self.options.category_orders,
                    labels=(
                        self.options.labels
                        or {self.options.legend_y: self.options.name}
                    ),
                    orientation=self.options.orientation,
                    log_x=self.options.log_x,
                    log_y=self.options.log_y,
                    range_x=self.options.range_x,
                    range_y=self.options.range_y,
                    render_mode=self.options.render_mode,
                    template=self.options.template,
                    width=self.options.width,
                    height=self.options.height,
                    line_dash=self.options.line_dash,
                    line_dash_map=self.options.line_dash_map,
                    line_dash_sequence=self.options.line_dash_sequence,
                    line_group=self.options.line_group,
                    line_shape=self.options.line_shape,
                    markers=self.options.markers,
                    animation_frame=self.options.animation_frame,
                    animation_group=self.options.animation_group,
                )
                if self.options.secondary_y:
                    self.trace.update_yaxes(secondary_y=True)
                    self.trace.update_traces(yaxis="y2")
            case PlotType.pie:
                self.trace = px.pie(
                    self._data_frame,
                    title=self.options.title,
                    names=self.options.legend_x,
                    values=self.options.legend_y,
                    color=self.options.color,
                    color_discrete_map=self.options.color_discrete_map,
                    color_discrete_sequence=self.options.color_discrete_sequence,
                    hover_name=self.options.hover_name,
                    hover_data=self.options.hover_data,
                    custom_data=self.options.custom_data,
                    facet_row=self.options.facet_row,
                    facet_col=self.options.facet_col,
                    facet_row_spacing=self.options.facet_row_spacing,
                    facet_col_spacing=self.options.facet_col_spacing,
                    facet_col_wrap=self.options.facet_col_wrap,
                    category_orders=self.options.category_orders,
                    hole=self.options.hole,
                    labels=(
                        self.options.labels
                        or {self.options.legend_y: self.options.name}
                    ),
                    opacity=self.options.opacity,
                    template=self.options.template,
                    width=self.options.width,
                    height=self.options.height,
                )
                if self.options.secondary_y:
                    self.trace.update_yaxes(secondary_y=True)
                    self.trace.update_traces(yaxis="y2")
            case PlotType.scatter:
                self.trace = px.scatter(
                    self._data_frame,
                    x=self.options.legend_x,
                    y=self.options.legend_y,
                    title=self.options.title,
                    color=self.options.color,
                    color_continuous_scale=self.options.color_continuous_scale,
                    color_continuous_midpoint=self.options.color_continuous_midpoint,
                    color_discrete_map=self.options.color_discrete_map,
                    color_discrete_sequence=self.options.color_discrete_sequence,
                    range_color=self.options.range_color,
                    size=self.options.size,
                    size_max=self.options.size_max,
                    symbol=self.options.symbol,
                    symbol_map=self.options.symbol_map,
                    symbol_sequence=self.options.symbol_sequence,
                    hover_name=self.options.hover_name,
                    hover_data=self.options.hover_data,
                    custom_data=self.options.custom_data,
                    text=self.options.text,
                    facet_row=self.options.facet_row,
                    facet_col=self.options.facet_col,
                    facet_row_spacing=self.options.facet_row_spacing,
                    facet_col_spacing=self.options.facet_col_spacing,
                    facet_col_wrap=self.options.facet_col_wrap,
                    error_x=self.options.error_x,
                    error_y=self.options.error_y,
                    error_x_minus=self.options.error_x_minus,
                    error_y_minus=self.options.error_y_minus,
                    category_orders=self.options.category_orders,
                    labels=(
                        self.options.labels
                        or {self.options.legend_y: self.options.name}
                    ),
                    orientation=self.options.orientation,
                    opacity=self.options.opacity,
                    marginal_x=self.options.marginal_x,
                    marginal_y=self.options.marginal_y,
                    trendline=self.options.trendline,
                    trendline_options=self.options.trendline_options,
                    trendline_scope=self.options.trendline_scope,
                    trendline_color_override=self.options.trendline_color_override,
                    log_x=self.options.log_x,
                    log_y=self.options.log_y,
                    range_x=self.options.range_x,
                    range_y=self.options.range_y,
                    render_mode=self.options.render_mode,
                    template=self.options.template,
                    width=self.options.width,
                    height=self.options.height,
                    animation_frame=self.options.animation_frame,
                    animation_group=self.options.animation_group,
                )
                if self.options.secondary_y:
                    self.trace.update_yaxes(secondary_y=True)
                    self.trace.update_traces(yaxis="y2")

    def _tick(self):
        pass


class XYPlotData(PlotData):
    """Data with x and y values as float."""

    def __init__(
        self,
        data_x: List[float] = [],
        data_y: List[float] = [],
        options: PlotOptions = PlotOptions(),
    ):
        """Create a data source from x and y lists of floats.

        Args:
            data_x (List[float], optional): x values. Defaults to [] to start with an empty data set.
            data_y (List[float], optional): y values. Defaults to [] to start with an empty data set.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        super().__init__(options)
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
        options: PlotOptions = PlotOptions(),
    ):
        """Create a data source from x as categories and y as float values.

        Args:
            data_x (List[str], optional): labels. Defaults to [] to start with an empty data set.
            data_y (List[float], optional): values for each label. Defaults to [] to start with an empty data set.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        if options.legend_x == "":
            options.legend_x = "category"
        if options.legend_y == "":
            options.legend_y = "value"
        super().__init__(options)
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
        options: PlotOptions = PlotOptions(),
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
        super().__init__(options)
        if data.shape[1] != 2:  # TODO add 3 when adding 3D plots
            raise ValueError("")
        self.data = data

    @property
    def _data_frame(self):
        return DataFrame(
            {
                self.options.legend_x: self.data[0],
                self.options.legend_y: self.data[1],
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
        options: PlotOptions = PlotOptions(),
    ):
        """Create a data source from watching the amount of a :class:`Resource`.

        Args:
            data (:class:`Resource`): Source :class:`Resource`.
            frequency (int, optional): Frequency in ticks to add data points.
                Defaults to 1, meaning a point gets added every tick.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        if options.legend_x == "":
            options.legend_x = simulation.time_unit
        if options.legend_y == "":
            options.legend_y = "amount"
        super().__init__(options)
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
        options: PlotOptions = PlotOptions(),
    ):
        """Create a data source from watching the size of a :class:`Queue`.

        Args:
            data (:class:`Queue`): Source :class:`Queue`.
            frequency (int, optional): Frequency in ticks to add data points.
                Defaults to 1, meaning a point gets added every tick.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        if options.legend_x == "":
            options.legend_x = simulation.time_unit
        if options.legend_y == "":
            options.legend_y = "length"
        super().__init__(options)
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
        options: PlotOptions = PlotOptions(),
    ):
        """Create a data source from watching the state of an :class:`Entity`.

        Args:
            data (:class:`Entity`): Source :class:`Entity`.
            frequency (int, optional): Frequency in ticks to add data points.
                Defaults to 1, meaning a point gets added every tick.
            plot_type ("scatter", "line", "bar", "pie", optional): Type of plot to show. Defaults to "line".
            title (Optional[str], optional): Title to use over the plot. Defaults to None.
        """
        if options.legend_x == "":
            options.legend_x = simulation.time_unit
        if options.legend_y == "":
            options.legend_y = "state"
        if options.plot_type is None:
            options.plot_type = PlotType.scatter
        super().__init__(options)
        self.data = data
        self.frequency = frequency

        # TODO


class Plot:
    """Base class for easily updating data for plots to be made on the dashboard."""

    id: str
    title: Optional[str]
    figure: Figure
    data: List[PlotData]
    dashboard: Dashboard

    def __init__(self, id: str, *args: PlotData):
        """Create a plot to add to the dashboard using `World.add_plot()`.

        Args:
            id (str): identifier, needs to be unique.
            *args (:class:`PlotData`): Data to start the plot with.
        """
        self.id = id
        self.data = []

        dash = simulation.world().dashboard
        if dash is None:
            return
        self.dashboard: Dashboard = dash

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
        if data in self.data:
            return self.data.index(data)
        data.plot = self
        data.plot_index = len(self.data)
        self.data.append(data)
        return data.plot_index

    def _update(self):
        self.dashboard.plots.clear()

        secondary_y = any([data.options.secondary_y for data in self.data])

        for plotdata in self.data:
            plotdata._update_trace()
            if secondary_y and plotdata.plot and plotdata.trace:
                if plotdata.plot.id not in self.dashboard.plots:
                    self.dashboard.plots[plotdata.plot.id] = make_subplots(
                        specs=[[{"secondary_y": True}]]
                    )
                    self.dashboard.plots[plotdata.plot.id].layout.xaxis.title = (  # type: ignore
                        plotdata.options.legend_x
                    )

        for plotdata in self.data:
            if plotdata.plot and plotdata.trace:
                for data in plotdata.trace["data"]:
                    data["showlegend"] = True  # type: ignore
                    data["name"] = plotdata.options.name  # type: ignore
                    self.dashboard.plots[plotdata.plot.id].add_traces([data])
                    if plotdata.options.secondary_y:
                        self.dashboard.plots[plotdata.plot.id].layout.yaxis2.title = (  # type: ignore
                            plotdata.options.legend_y
                        )
                        if isinstance(plotdata.options.color_discrete_sequence, list):
                            color = plotdata.options.color_discrete_sequence[0]
                            plcolors = convert_colors_to_same_type(color, "rgb")
                            if len(plcolors[0]) == 0:
                                rgb = name_to_rgb(color)
                                r, g, b = rgb.red, rgb.green, rgb.blue
                            else:
                                (r, g, b) = unlabel_rgb(plcolors[0][0])
                            self.dashboard.plots[plotdata.plot.id].update_yaxes(
                                gridcolor=f"rgba({r},{g},{b},0.5)", secondary_y=True
                            )
                    else:
                        self.dashboard.plots[plotdata.plot.id].layout.yaxis.title = (  # type: ignore
                            plotdata.options.legend_y
                        )
