import streamlit as st

from .logging import log, LogLevel

world = st.session_state.world
if world.update_time:
    run_every = world.update_time
else:
    run_every = None


@st.fragment(run_every=run_every)
def draw_dashboard():
    """Draw the dashboard if it has been initialized."""
    dash = st.session_state.dashboard
    if not dash:
        return
    dash._draw()

    # Logic to let the dashboard update during the simulation,
    # and to stop rerunning the Streamlit fragment when the simulation has ended
    if world.update_time and world.update_time > 0.0:
        log(f"Dashboard should update again in {world.update_time} s", LogLevel.verbose)
    else:
        if world.update_time == 0.0:
            world.update_time = None
            st.rerun()
