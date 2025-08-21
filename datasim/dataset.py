from abc import ABC
from typing import Final, List, Optional
from pandas import DataFrame

import numpy as np

from .entity import Entity
from .logging import log
from .output import Output
from .queue import Queue
from .resource import Resource
from .types import LogLevel, PlotOptions, PlotType


class DataSource(ABC):
    """Abstract superclass of different types of data to save and/or plot."""

    world: Final
    dataset: Optional["Dataset"] = None
    set_index: Optional[int] = 0
    options: PlotOptions
    _stopped: bool = False

    def __init__(
        self,
        world,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a data source to save or plot.

        Args:
            world: The `World` this data belongs to.
            plot_options (Optional[PlotOptions], optional): Options for a plot.
                Defaults to default PlotOptions which means nothing will be plotted.
        """
        self.world = world

        self.options = plot_options

        self._buffer_size = max(10000, self.world.end_tick)
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
        self.world.output._update_trace(self)

    def _tick(self):
        pass

    def _stop(self):
        self._tick()
        self._stopped = True


class DataFrameData(DataSource):
    """Data directly from a Pandas DataFrame."""

    data: DataFrame

    def __init__(
        self,
        world,
        data: DataFrame,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a data source directly referencing a Pandas DataFrame.

        Args:
            world: The `World` this data belongs to.
            data (:class:`pd.DataFrame`): The DataFrame.
            plot_options (Optional[PlotOptions], optional): Options for a plot.
                Defaults to default PlotOptions which means nothing will be plotted.

        Raises:
            `TypeError`: When trying to take from a capacity resource without specifying an amount.
        """
        super().__init__(world, plot_options)
        self.data = data

    @property
    def _data_frame(self):
        return self.data


class XYData(DataSource):
    """Data with x and y values as float."""

    def __init__(
        self,
        world,
        data_x: List[float] = [],
        data_y: List[float] = [],
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a data source from x and y lists of floats.

        Args:
            world: The `World` this data belongs to.
            data_x (List[float], optional): x values. Defaults to [] to start with an empty data set.
            data_y (List[float], optional): y values. Defaults to [] to start with an empty data set.
            plot_options (Optional[PlotOptions], optional): Options for a plot.
                Defaults to default PlotOptions which means nothing will be plotted.
        """
        super().__init__(world, plot_options)
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


class CategoryData(DataSource):
    """Data with named categories with float values."""

    labels: List[str]
    values: List[float]

    def __init__(
        self,
        world,
        data_x: List[str] = [],
        data_y: List[float] = [],
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a data source from x as categories and y as float values.

        Args:
            world: The `World` this data belongs to.
            data_x (List[str], optional): labels. Defaults to [] to start with an empty data set.
            data_y (List[float], optional): values for each label. Defaults to [] to start with an empty data set.
            plot_options (Optional[PlotOptions], optional): Options for a plot.
                Defaults to default PlotOptions which means nothing will be plotted.
        """
        if plot_options.legend_x == "":
            plot_options.legend_x = "category"
        if plot_options.legend_y == "":
            plot_options.legend_y = "value"
        super().__init__(world, plot_options)
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


class NPData(DataSource):
    """Data with Numpy array as source."""

    data: np.ndarray

    def __init__(
        self,
        world,
        data: np.ndarray,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a data source from a Numpy array.

        Args:
            world: The `World` this data belongs to.
            data (:class:`np.ndarray`): Array of data points. Shape should correspond to the dimensions of the plot
                (2 columns for 2D plots, 3 columns for 3D plots).
            plot_options (Optional[PlotOptions], optional): Options for a plot.
                Defaults to default PlotOptions which means nothing will be plotted.

        Raises:
            `TypeError`: When trying to take from a capacity resource without specifying an amount.
        """
        super().__init__(world, plot_options)
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


class ResourceData(DataSource):
    """Data source from watching the amount of a :class:`Resource`."""

    source: Resource
    sample_users: bool
    frequency: int

    def __init__(
        self,
        world,
        source_id: str,
        sample_users: bool = False,
        frequency: int = 1,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a data source from watching the amount of a :class:`Resource`.

        Args:
            world: The `World` this data belongs to.
            source_id (:class:`Resource`): Source :class:`Resource`.
            plot_users (bool, optional): If True, sample number of users instead of amount.
            frequency (int, optional): Frequency in ticks to add data points.
                Defaults to 1, meaning a point gets added every tick.
            plot_options (Optional[PlotOptions], optional): Options for a plot.
                Defaults to default PlotOptions which means nothing will be plotted.
        """
        if plot_options.legend_x == "":
            plot_options.legend_x = world.time_unit
        if plot_options.legend_y == "":
            plot_options.legend_y = "amount"
        super().__init__(world, plot_options)
        self.source = self.world.resource(source_id)
        self.sample_users = sample_users
        self.frequency = frequency

    def _tick(self):
        if self._stopped:
            return

        if (self.frequency == 0 and self.source.changed_tick == self.world.ticks) or (
            self.frequency > 0 and self.world.ticks % self.frequency == 0
        ):
            if len(self._x_buffer) <= self._buffer_index:
                self._x_buffer = np.append(self._x_buffer, np.zeros(self._buffer_size))
                self._y_buffer = np.append(self._y_buffer, np.zeros(self._buffer_size))
            self._x_buffer[self._buffer_index] = self.world.time
            self._y_buffer[self._buffer_index] = (
                len(self.source.users) if self.sample_users else self.source.amount
            )
            self._buffer_index += 1


class QueueData(DataSource):
    """Data source from watching the size of a :class:`Queue`."""

    source: Queue
    frequency: int

    def __init__(
        self,
        world,
        source_id: str,
        frequency: int = 1,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a data source from watching the size of a :class:`Queue`.

        Args:
            world: The `World` this data belongs to.
            source_id (:class:`Queue`): Source :class:`Queue`.
            frequency (int, optional): Frequency in ticks to add data points.
                Defaults to 1, meaning a point gets added every tick.
            plot_options (Optional[PlotOptions], optional): Options for a plot.
                Defaults to default PlotOptions which means nothing will be plotted.
        """
        if plot_options.legend_x == "":
            plot_options.legend_x = world.time_unit
        if plot_options.legend_y == "":
            plot_options.legend_y = "length"
        super().__init__(world, plot_options)
        self.source = self.world.queue(source_id)
        self.frequency = frequency

    def _tick(self):
        if self._stopped:
            return

        if (self.frequency == 0 and self.source.changed_tick == self.world.ticks) or (
            self.frequency > 0 and self.world.ticks % self.frequency == 0
        ):
            if len(self._x_buffer) <= self._buffer_index:
                self._x_buffer = np.append(self._x_buffer, np.zeros(self._buffer_size))
                self._y_buffer = np.append(self._y_buffer, np.zeros(self._buffer_size))
            self._x_buffer[self._buffer_index] = self.world.time
            self._y_buffer[self._buffer_index] = len(self.source)
            self._buffer_index += 1


class StateData(DataSource):
    """Data source from watching the state of an :class:`Entity`."""

    source: Entity
    frequency: int

    def __init__(
        self,
        world,
        source: Entity,
        frequency: int = 1,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a data source from watching the state of an :class:`Entity`.

        Args:
            world: The `World` this data belongs to.
            source (:class:`Entity`): Source :class:`Entity`.
            frequency (int, optional): Frequency in ticks to add data points.
                Defaults to 1, meaning a point gets added every tick.
            plot_options (Optional[PlotOptions], optional): Options for a plot.
                Defaults to default PlotOptions which means nothing will be plotted.
        """
        if plot_options.legend_x == "":
            plot_options.legend_x = world.time_unit
        if plot_options.legend_y == "":
            plot_options.legend_y = "state"
        super().__init__(world, plot_options)
        self.source = source
        self.source._link_output(self)
        self.frequency = frequency
        self._y_buffer = np.full(self._buffer_size, "", dtype=object)

    def _tick(self):
        if self._stopped:
            return

        if (self.frequency == 0 and self.source.ticks_in_current_state <= 1) or (
            self.frequency > 0 and self.world.ticks % self.frequency == 0
        ):
            if len(self._x_buffer) <= self._buffer_index:
                self._x_buffer = np.append(self._x_buffer, np.zeros(self._buffer_size))
                self._y_buffer = np.append(
                    self._y_buffer, np.full(self._buffer_size, "", dtype=object)
                )
            self._x_buffer[self._buffer_index] = self.world.time
            self._y_buffer[self._buffer_index] = self.source.state.type_id
            self._buffer_index += 1


class Dataset:
    """Base class for saving data and updating data for plots to be made on a dashboard."""

    world: Final
    id: Final[str]
    title: Optional[str]
    sources: List[DataSource]
    output: Output
    _gathered: bool = False

    def __init__(self, world, id: str, *args: DataSource):
        """Create a dataset to add to the output using `World.add_data()`.

        Args:
            id (str): identifier, needs to be unique.
            *args (:class:`DataSource`): Source to start the dataset with.
        """
        self.world = world
        self.id = id
        self.sources = []

        output = self.world.runner.output
        if output is None:
            return
        self.output: Output = output

        for arg in args:
            self.add_source(arg)

    def __getitem__(self, key: int) -> DataSource:
        """Get a reference to a source from this dataset.

        Args:
            key (int): Index of the source.

        Returns:
            tuple(list[float] | list[str], list[float]): Source at index.
        """
        return self.sources[key]

    def _tick(self):
        for source in self.sources:
            source._tick()

    def add_source(self, source: DataSource) -> int:
        """Add a data source to the set.

        Args:
            data (Data): Data source.

        Returns:
            int: Index of the added data source.
        """
        if source in self.sources:
            return self.sources.index(source)
        source.dataset = self
        source.set_index = len(self.sources)
        self.sources.append(source)
        return source.set_index

    def remove_source(self, source: DataSource):
        """Remove a data source from the set.

        Args:
            data (Data): Data source.
        Raises:
            ReferenceError: In case of a DataSource set or index mismatch.
        """
        index = source.set_index
        if source.dataset != self or index is None or self.sources[index] != source:
            raise ReferenceError("Integrity failure: Data source or index mismatch!")
        self.sources.remove(source)
        for new_index in range(index, len(self.sources)):
            self.sources[new_index].set_index = new_index

    def _update(self) -> bool:
        changed = False
        any_output = False
        for source in self.sources:
            if not self._gathered:
                log(f"- Updating: {source.options.name}...", LogLevel.verbose)
                source._update_trace()
                changed = True
            if source.options.plot_type != PlotType.none:
                any_output = True
            if source.options.plot_type not in (PlotType.none, PlotType.export_only):
                self.output._add_source(
                    self.world.index,
                    self.id,
                    source.options.legend_x,
                    source.options.secondary_y,
                )

        if any_output:
            self.output.dataframes[self.world.index][self.id] = DataFrame()
            if self.id not in self.output.dataframe_names[self.world.index]:
                self.output.dataframe_names[self.world.index][self.id] = (
                    f"{self.world.title} - {self.id} - {self.world.variation.replace(":", ".")}"
                    if self.world.variation and self.world.runner.split_worlds
                    else f"{self.world.title} - {self.id}"
                )

        for source in self.sources:
            if source.options.plot_type != PlotType.none and source.dataset is not None:
                self.output._update_source(source)

                dataframe = source._data_frame.copy()
                if len(dataframe.columns) == 2:
                    dataframe.columns = [self.world.time_unit, source.options.name]
                if self.output.dataframes[self.world.index][self.id].empty:
                    self.output.dataframes[self.world.index][self.id] = dataframe
                else:
                    self.output.dataframes[self.world.index][self.id] = (
                        self.output.dataframes[self.world.index][self.id].merge(
                            dataframe, on=self.world.time_unit, how="outer"
                        )
                    )

        self._gathered = True

        return changed
