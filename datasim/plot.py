from typing import List, Literal, Optional, Tuple, TypeGuard, cast
from plotly.graph_objs._figure import Figure
import plotly.express as px
import streamlit as st

from .dashboard import Dashboard

PLOT_TYPE = Literal["scatter", "line", "bar", "pie"]


class Plot:
    """Data class for easily updating data for plots to be made on the dashboard."""

    id: str
    title: Optional[str]
    figure: Figure
    data: List[Tuple[List[float] | List[str], List[float]]]
    types: List[PLOT_TYPE]
    traces: List[Optional[Figure]]

    def __init__(self, id: str, title: Optional[str] = None,
                 *args: Tuple[List[float] | List[str], List[float], PLOT_TYPE]):
        """Create a plot to add to the dashboard using `World.add_plot()`.

        Args:
            id (str): identifier, needs to be unique.
            title (str, optional): Title to use over the plot. Defaults to None.
            *args (tuple(list[float] | list[str], list[float], Literal["scatter", "line", "bar", "pie"])):
                traces to start the plot with.
        """
        self.id = id
        self.title = title
        self.data = [(x, y) for (x, y, _) in args]
        self.types = [t for (_, _, t) in args]
        self.traces = [None for _ in args]

    def __getitem__(self, key: int) -> Tuple[List[float] | List[str], List[float]]:
        """Get a reference to a data set from this plot.

        Args:
            key (int): Index of the data set.

        Returns:
            tuple(list[float] | list[str], list[float]): Data set at index.
        """
        return self.data[key]

    def _data_float(self, val: List[float] | List[str]) -> TypeGuard[List[float]]:
        return len(val) == 0 or isinstance(val[0], float)

    def _data_str(self, val: List[float] | List[str]) -> TypeGuard[List[str]]:
        return len(val) == 0 or isinstance(val[0], str)

    def add_trace(self, data: Tuple[List[float] | List[str], List[float]] = ([], []),
                  plotType: PLOT_TYPE = "line") -> int:
        """Add a data trace to the plot.

        Args:
            data (tuple(list[float] | list[str], list[float]), optional): Data set (x, y).
                Defaults to ([], []) to start with an empty data set.
            plotType ("scatter", "line", "bar" or "pie", optional): Type of trace to plot. Defaults to "line".

        Returns:
            int: Index of the added data set.
        """
        index: int = len(self.data)
        self.data.append(data)
        self.types.append(plotType)
        self.traces.append(None)
        return index

    def append(self, index: int, x: float | str, y: float):
        """Add a data point to a data set in this plot.

        Args:
            index (int): Index of the data set.
            x (float | str): x value or label of the data point.
            y (float): y value of the data point.

        Raises:
            IndexError: If no data trace at index exists.
        """
        if len(self.data) <= index:
            raise IndexError(f"Data trace {index} out of range, only {len(self.data)} traces registered")
        xs = self.data[index][0]
        if self._data_float(xs) and isinstance(x, float):
            xs.append(x)
        elif self._data_str(xs) and isinstance(x, str):
            xs.append(x)
        self.data[index][1].append(y)

    def _update(self, dashboard: Optional[Dashboard] = None):
        if dashboard is None:
            if "dashboard" in st.session_state:
                dashboard = cast(Dashboard, st.session_state.dashboard)
            else:
                return
        i: int = 0
        for (data_x, data_y) in self.data:
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
