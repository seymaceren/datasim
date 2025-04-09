from typing import List, Literal, Optional, Tuple, TypeGuard, cast
from plotly.graph_objs._figure import Figure
import plotly.express as px
import streamlit as st

from .dashboard import Dashboard

PLOT_TYPE = Literal["scatter", "line", "bar", "pie"]


class Plot:
    id: str
    title: Optional[str]
    figure: Figure
    data: List[Tuple[List[float] | List[str], List[float]]]
    types: List[PLOT_TYPE]
    traces: List[Optional[Figure]]

    def __init__(self, id: str, title: Optional[str] = None,
                 *args: Tuple[List[float] | List[str], List[float], PLOT_TYPE]):
        self.id = id
        self.title = title
        self.data = [(x, y) for (x, y, _) in args]
        self.types = [t for (_, _, t) in args]
        self.traces = [None for _ in args]

    def __getitem__(self, key: int) -> Tuple[List[float] | List[str], List[float]]:
        return self.data[key]

    def data_float(self, val: List[float] | List[str]) -> TypeGuard[List[float]]:
        return len(val) == 0 or isinstance(val[0], float)

    def data_str(self, val: List[float] | List[str]) -> TypeGuard[List[str]]:
        return len(val) == 0 or isinstance(val[0], str)

    def add_trace(self, data: Tuple[List[float] | List[str], List[float]] = ([], []), plotType: PLOT_TYPE = "line"):
        index = len(self.data)
        self.data.append(data)
        self.types.append(plotType)
        self.traces.append(None)
        return index

    def append(self, index: int, x: float | str, y: float):
        if len(self.data) <= index:
            raise IndexError(f"Data trace {index} out of range, only {len(self.data)} traces registered")
        xs = self.data[index][0]
        if self.data_float(xs) and isinstance(x, float):
            xs.append(x)
        elif self.data_str(xs) and isinstance(x, str):
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
