import plotly.express as px
from plotly.graph_objs._figure import Figure
from plotly.subplots import make_subplots
from plotly.colors import convert_colors_to_same_type, unlabel_rgb
from typing import Dict, List, Optional
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from webcolors import name_to_rgb


from .output import Output
from .logging import log
from .types import LogLevel, PlotType


class StreamlitDashboard(Output):
    """Dashboard using Streamlit."""

    plots: Dict[int, Dict[str, Figure]]
    traces: Dict[int, Dict[str, Dict[int, Figure]]]
    frames: Dict[int, Dict[str, DeltaGenerator]]
    world_index: int

    def __init__(self):
        """Create dashboard using Streamlit."""
        st.session_state.dashboard = self

        self.plots = {}
        self.traces = {}
        self.frames = {}
        self.world_index = 0

        super().__init__()

    def _add_world(self, world: int):
        super()._add_world(world)
        self.plots[world] = {}
        self.traces[world] = {}
        self.frames[world] = {}

    def _clear(self, world: int):
        self.plots[world].clear()

    def _add_source(
        self, world: int, source_id: str, legend_x: Optional[str], secondary_y: bool
    ):
        if world not in self.plots:
            self.plots[world] = {}
        if source_id not in self.plots[world]:
            self.plots[world][source_id] = make_subplots(
                specs=[[{"secondary_y": secondary_y}]]
            )
            self.plots[world][source_id].layout.xaxis.title = legend_x  # type: ignore

    def _update_trace(self, source):
        from .dataset import DataSource, Dataset

        if (
            not isinstance(source, DataSource)
            or not isinstance(source.dataset, Dataset)
            or source.set_index is None
        ):
            return
        if source.world.index not in self.traces:
            self.traces[source.world.index] = {}
        if source.dataset.id not in self.traces[source.world.index]:
            self.traces[source.world.index][source.dataset.id] = {}

        match source.options.plot_type:
            case PlotType.bar:
                trace = px.bar(
                    source._data_frame,
                    title=source.options.title,
                    x=source.options.legend_x,
                    y=(
                        source._data_frame.columns[1]
                        if source.options.legend_y is None
                        else source.options.legend_y
                    ),
                    color=source.options.color,
                    color_continuous_scale=source.options.color_continuous_scale,
                    color_continuous_midpoint=source.options.color_continuous_midpoint,
                    color_discrete_map=source.options.color_discrete_map,
                    color_discrete_sequence=source.options.color_discrete_sequence,
                    range_color=source.options.range_color,
                    hover_name=source.options.hover_name,
                    hover_data=source.options.hover_data,
                    custom_data=source.options.custom_data,
                    text=source.options.text,
                    facet_row=source.options.facet_row,
                    facet_col=source.options.facet_col,
                    facet_row_spacing=source.options.facet_row_spacing,
                    facet_col_spacing=source.options.facet_col_spacing,
                    facet_col_wrap=source.options.facet_col_wrap,
                    error_x=source.options.error_x,
                    error_y=source.options.error_y,
                    error_x_minus=source.options.error_x_minus,
                    error_y_minus=source.options.error_y_minus,
                    category_orders=source.options.category_orders,
                    labels=(
                        source.options.labels
                        or {source.options.legend_y: source.options.name}
                        if source.options.name and source.options.legend_y != ""
                        else None
                    ),
                    orientation=source.options.orientation,
                    opacity=source.options.opacity,
                    log_x=source.options.log_x,
                    log_y=source.options.log_y,
                    range_x=source.options.range_x,
                    range_y=source.options.range_y,
                    pattern_shape=source.options.pattern_shape,
                    pattern_shape_map=source.options.pattern_shape_map,
                    pattern_shape_sequence=source.options.pattern_shape_sequence,
                    base=source.options.base,
                    barmode=source.options.barmode,
                    text_auto=source.options.text_auto,
                    template=source.options.template,
                    width=source.options.width,
                    height=source.options.height,
                    animation_frame=source.options.animation_frame,
                    animation_group=source.options.animation_group,
                )
                if source.options.secondary_y:
                    trace.update_yaxes(secondary_y=True)
                    trace.update_traces(yaxis="y2")
                self.traces[source.world.index][source.dataset.id][
                    source.set_index
                ] = trace
            case PlotType.line:
                trace = px.line(
                    source._data_frame,
                    title=source.options.title,
                    x=source.options.legend_x,
                    y=source.options.legend_y,
                    color=source.options.color,
                    color_discrete_map=source.options.color_discrete_map,
                    color_discrete_sequence=source.options.color_discrete_sequence,
                    symbol=source.options.symbol,
                    symbol_map=source.options.symbol_map,
                    symbol_sequence=source.options.symbol_sequence,
                    hover_name=source.options.hover_name,
                    hover_data=source.options.hover_data,
                    custom_data=source.options.custom_data,
                    text=source.options.text,
                    facet_row=source.options.facet_row,
                    facet_col=source.options.facet_col,
                    facet_row_spacing=source.options.facet_row_spacing,
                    facet_col_spacing=source.options.facet_col_spacing,
                    facet_col_wrap=source.options.facet_col_wrap,
                    error_x=source.options.error_x,
                    error_y=source.options.error_y,
                    error_x_minus=source.options.error_x_minus,
                    error_y_minus=source.options.error_y_minus,
                    category_orders=source.options.category_orders,
                    labels=(
                        source.options.labels
                        or {source.options.legend_y: source.options.name}
                        if source.options.name
                        else None
                    ),
                    orientation=source.options.orientation,
                    log_x=source.options.log_x,
                    log_y=source.options.log_y,
                    range_x=source.options.range_x,
                    range_y=source.options.range_y,
                    render_mode=source.options.render_mode,
                    template=source.options.template,
                    width=source.options.width,
                    height=source.options.height,
                    line_dash=source.options.line_dash,
                    line_dash_map=source.options.line_dash_map,
                    line_dash_sequence=source.options.line_dash_sequence,
                    line_group=source.options.line_group,
                    line_shape=source.options.line_shape,
                    markers=source.options.markers,
                    animation_frame=source.options.animation_frame,
                    animation_group=source.options.animation_group,
                )
                if source.options.secondary_y:
                    trace.update_yaxes(secondary_y=True)
                    trace.update_traces(yaxis="y2")
                self.traces[source.world.index][source.dataset.id][
                    source.set_index
                ] = trace
            case PlotType.pie:
                trace = px.pie(
                    source._data_frame,
                    title=source.options.title,
                    names=source.options.legend_x,
                    values=source.options.legend_y,
                    color=source.options.color,
                    color_discrete_map=source.options.color_discrete_map,
                    color_discrete_sequence=source.options.color_discrete_sequence,
                    hover_name=source.options.hover_name,
                    hover_data=source.options.hover_data,
                    custom_data=source.options.custom_data,
                    facet_row=source.options.facet_row,
                    facet_col=source.options.facet_col,
                    facet_row_spacing=source.options.facet_row_spacing,
                    facet_col_spacing=source.options.facet_col_spacing,
                    facet_col_wrap=source.options.facet_col_wrap,
                    category_orders=source.options.category_orders,
                    hole=source.options.hole,
                    labels=(
                        source.options.labels
                        or {source.options.legend_y: source.options.name}
                        if source.options.name
                        else None
                    ),
                    opacity=source.options.opacity,
                    template=source.options.template,
                    width=source.options.width,
                    height=source.options.height,
                )
                if source.options.secondary_y:
                    trace.update_yaxes(secondary_y=True)
                    trace.update_traces(yaxis="y2")
                self.traces[source.world.index][source.dataset.id][
                    source.set_index
                ] = trace
            case PlotType.scatter:
                trace = px.scatter(
                    source._data_frame,
                    x=source.options.legend_x,
                    y=source.options.legend_y,
                    title=source.options.title,
                    color=source.options.color,
                    color_continuous_scale=source.options.color_continuous_scale,
                    color_continuous_midpoint=source.options.color_continuous_midpoint,
                    color_discrete_map=source.options.color_discrete_map,
                    color_discrete_sequence=source.options.color_discrete_sequence,
                    range_color=source.options.range_color,
                    size=source.options.size,
                    size_max=source.options.size_max,
                    symbol=source.options.symbol,
                    symbol_map=source.options.symbol_map,
                    symbol_sequence=source.options.symbol_sequence,
                    hover_name=source.options.hover_name,
                    hover_data=source.options.hover_data,
                    custom_data=source.options.custom_data,
                    text=source.options.text,
                    facet_row=source.options.facet_row,
                    facet_col=source.options.facet_col,
                    facet_row_spacing=source.options.facet_row_spacing,
                    facet_col_spacing=source.options.facet_col_spacing,
                    facet_col_wrap=source.options.facet_col_wrap,
                    error_x=source.options.error_x,
                    error_y=source.options.error_y,
                    error_x_minus=source.options.error_x_minus,
                    error_y_minus=source.options.error_y_minus,
                    category_orders=source.options.category_orders,
                    labels=(
                        source.options.labels
                        or {source.options.legend_y: source.options.name}
                        if source.options.name
                        else None
                    ),
                    orientation=source.options.orientation,
                    opacity=source.options.opacity,
                    marginal_x=source.options.marginal_x,
                    marginal_y=source.options.marginal_y,
                    trendline=source.options.trendline,
                    trendline_options=source.options.trendline_options,
                    trendline_scope=source.options.trendline_scope,
                    trendline_color_override=source.options.trendline_color_override,
                    log_x=source.options.log_x,
                    log_y=source.options.log_y,
                    range_x=source.options.range_x,
                    range_y=source.options.range_y,
                    render_mode=source.options.render_mode,
                    template=source.options.template,
                    width=source.options.width,
                    height=source.options.height,
                    animation_frame=source.options.animation_frame,
                    animation_group=source.options.animation_group,
                )
                if source.options.secondary_y:
                    trace.update_yaxes(secondary_y=True)
                    trace.update_traces(yaxis="y2")
                self.traces[source.world.index][source.dataset.id][
                    source.set_index
                ] = trace

    def _update_source(self, source):
        from .dataset import DataSource, Dataset

        if (
            not isinstance(source, DataSource)
            or not isinstance(source.dataset, Dataset)
            or source.set_index is None
        ):
            return

        if source.world.index not in self.traces:
            self.traces[source.world.index] = {}
        if (
            source.dataset.id in self.traces[source.world.index]
            and source.set_index in self.traces[source.world.index][source.dataset.id]
        ):
            for data in self.traces[source.world.index][source.dataset.id][
                source.set_index
            ]["data"]:
                data["showlegend"] = True  # type: ignore
                data["name"] = source.options.name  # type: ignore
                self.plots[source.world.index][source.dataset.id].add_traces([data])

        # Part 2: TODO check if other timing needed
        if source.options.secondary_y:
            self.plots[source.world.index][source.dataset.id].layout.yaxis2.title = (  # type: ignore
                source.options.legend_y
            )
            if isinstance(source.options.color_discrete_sequence, list):
                color = source.options.color_discrete_sequence[0]
                plcolors = convert_colors_to_same_type(color, "rgb")
                if len(plcolors[0]) == 0:
                    rgb = name_to_rgb(color)
                    r, g, b = rgb.red, rgb.green, rgb.blue
                else:
                    (r, g, b) = unlabel_rgb(plcolors[0][0])
                self.plots[source.world.index][source.dataset.id].update_yaxes(
                    gridcolor=f"rgba({r},{g},{b},0.5)", secondary_y=True
                )
        else:
            self.plots[source.world.index][source.dataset.id].layout.yaxis.title = (  # type: ignore
                source.options.legend_y
            )

    def _select_world(self, worlds) -> List[int]:
        world = 0
        if len(worlds) > 1:
            world = st.selectbox(
                "Details for run:",
                range(len(worlds)),
                format_func=lambda i: worlds[i].variation,
            )
        self.world_index = worlds[world].index
        return [world]

    def _draw(self):
        if self.world_index not in self.plots:
            return
        for source_id in self.plots[self.world_index]:
            self._draw_plot(self.world_index, source_id)
            for index in self.plots:
                if (
                    index < 0
                    and Output.aggregated_title(source_id) in self.plots[index]
                ):
                    self._draw_plot(index, Output.aggregated_title(source_id))

    def _draw_plot(self, world_index, source_id):
        if source_id not in self.frames[world_index]:
            self.frames[world_index][source_id] = st.empty()

        log(f"Update plot {source_id}", LogLevel.verbose)

        with self.frames[world_index][source_id].container():
            st.plotly_chart(self.plots[world_index][source_id])

            path_p, file_p = self.export_pickle(world_index, source_id)
            st.download_button(
                label="Pickle",
                data=file_p,
                file_name=path_p,
                mime="application/octet-stream",
                icon=":material/download:",
            )
            path_c, file_c = self.export_csv(world_index, source_id)
            st.download_button(
                label="CSV",
                data=file_c,
                file_name=path_c,
                mime="text/csv",
                icon=":material/download:",
            )
