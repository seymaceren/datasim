from math import sin
from typing import Dict, Optional, cast
from plotly.graph_objs._figure import Figure
import streamlit as st
import plotly.express as px
# import plotly.figure_factory as ff

from datasim import simtime
from datasim import Dashboard
from datasim import World


class ICU(World):
    def __init__(self):
        super().__init__("ICU world")
        self.overview_plot: Optional[Figure] = None
        self.overview_data: Dict[float, float] = {}

    def post_entities_tick(self):
        self.overview_data[simtime.seconds()] = sin(simtime.seconds() * 5.0)

    def update_plots(self):
        dash: Dashboard = st.session_state.dashboard
        if len(self.overview_data) > 0:
            if not self.overview_plot:
                self.overview_plot = cast(Figure,
                                          px.line(x=list(self.overview_data.keys()),
                                                  y=list(self.overview_data.values()),
                                                  markers=True, title="ICU simulatie"))
            else:
                self.overview_plot.update_traces(x=list(self.overview_data.keys()),
                                                 y=list(self.overview_data.values()))
            if "overview" not in dash.plots and self.overview_plot is not None:
                dash.plots["overview"] = self.overview_plot

        # self.beds = Bed()
        # self.beds.set_count(4)
        # add_resource(self.beds)
