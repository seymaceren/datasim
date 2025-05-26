import streamlit as st

from .logging import log, LogLevel

run_every = st.session_state.update_time


@st.fragment(run_every=run_every)
def draw_dashboard():
    """Draw the dashboard if it has been initialized."""
    runner = st.session_state.runner
    if not runner:
        return
    runner._draw()

    # Logic to let the dashboard update during the simulation,
    # and to stop rerunning the Streamlit fragment when the simulation has ended
    if runner.update_time and runner.update_time > 0.0:
        log(
            f"Dashboard should update again in {runner.update_time} s", LogLevel.verbose
        )
    else:
        st.session_state.update_time = None
        st.rerun()
