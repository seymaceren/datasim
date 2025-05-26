from time import monotonic
from typing import Dict
from plotly.graph_objs._figure import Figure
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from .logging import log
from .types import LogLevel


class Dashboard:
    """Dashboard to show the state and results of the simulation.

    Currently automatically runs on Streamlit.
    """

    def __init__(self, runner):
        """Dashboard is created during sim initialization."""
        st.session_state.dashboard = self

        self.plots: Dict[str, Figure] = {}
        self.frames: Dict[str, DeltaGenerator] = {}

        self.start_time = monotonic()

    def _draw(self):
        log(f"Update {len(self.plots)} plots", LogLevel.verbose)
        for plot_id in self.plots:
            if plot_id not in self.frames:
                self.frames[plot_id] = st.empty()
            log(f"Update plot {plot_id}", LogLevel.verbose)

            self.frames[plot_id].plotly_chart(self.plots[plot_id])
