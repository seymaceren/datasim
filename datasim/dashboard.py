import pickle
from pandas import DataFrame
from plotly.graph_objs._figure import Figure
from time import monotonic
from typing import Dict
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from .logging import log
from .types import LogLevel


class Dashboard:
    """Dashboard to show the state and results of the simulation.

    Currently automatically runs on Streamlit.
    """

    plots: Dict[str, Figure]
    frames: Dict[str, DeltaGenerator]
    dataframes: Dict[str, DataFrame]
    dataframe_names: Dict[str, str]

    start_time: float

    def __init__(self):
        """Dashboard is created during sim initialization."""
        st.session_state.dashboard = self

        self.plots = {}
        self.frames = {}
        self.dataframes = {}
        self.dataframe_names = {}

        self.start_time = monotonic()

    def _draw(self):
        for plot_id in self.plots:
            if plot_id not in self.frames:
                self.frames[plot_id] = st.empty()

            log(f"Update plot {plot_id}", LogLevel.verbose)

            with self.frames[plot_id].container():
                st.plotly_chart(self.plots[plot_id])

                if (
                    st.pills(
                        "Format",
                        ["Pickle", "CSV"],
                        default="Pickle",
                        label_visibility="hidden",
                    )
                    == "Pickle"
                ):
                    st.download_button(
                        label="Download data",
                        data=pickle.dumps(self.dataframes[plot_id]),
                        file_name=f"{self.dataframe_names[plot_id]}.pickle",
                        mime="application/octet-stream",
                        icon=":material/download:",
                    )
                else:
                    st.download_button(
                        label="Download data",
                        data=self.dataframes[plot_id].to_csv(),
                        file_name=f"{self.dataframe_names[plot_id]}.csv",
                        mime="tex/csv",
                        icon=":material/download:",
                    )
