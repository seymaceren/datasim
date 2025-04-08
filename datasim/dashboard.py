from time import monotonic
from typing import Dict, List
from plotly.graph_objs._figure import Figure
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from datasim.world import World


class Dashboard():
    def __init__(self):
        if not World.current:
            return

        st.session_state.dashboard = self

        self.plots: Dict[str, Figure] = {}
        self.frames: Dict[str, DeltaGenerator] = {}

        self.start_time = monotonic()

    def draw(self):
        if not World.current:
            return

        world: World = World.current
        world.update_plots()
        for plot_id in self.plots:
            if plot_id not in self.frames:
                self.frames[plot_id] = st.empty()
            self.frames[plot_id].plotly_chart(self.plots[plot_id])

    # def plot_test(self):
    #     if not self.fig2:
    #         # Add histogram data
    #         x1 = np.random.randn(200) - 2
    #         x2 = np.random.randn(200)
    #         x3 = np.random.randn(200) + 2

    #         # Group data together
    #         hist_data = [x1, x2, x3]

    #         group_labels = ['Group 1', 'Group 2', 'Group 3']

    #         # Create distplot with custom bin_size
    #         self.fig2 = ff.create_distplot(hist_data, group_labels, bin_size=[.1, .25, .5])

    #     # Plot!
    #     if not self.fig2frame:
    #         self.fig2frame = st.empty()
    #     self.fig2frame.plotly_chart(self.fig2, key="fig2")
