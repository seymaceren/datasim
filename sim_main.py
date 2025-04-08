from time import sleep
from typing import Optional
import streamlit as st

from datasim import simtime
from datasim.dashboard import Dashboard
from datasim.world import World

# Use this line to specify your main world class
from icu import ICU as MainWorldClass


@st.fragment(run_every=simtime.update_time)
def draw_dashboard():
    # Draw our dashboard if it has been initialized
    dash: Optional[Dashboard] = st.session_state.dashboard
    if not dash:
        return
    dash.draw()

    # Logic to let the dashboard update during the simulation,
    # and to stop rerunning the Streamlit fragment when the simulation has ended
    if simtime.update_time and simtime.update_time > 0.0:
        sleep(simtime.update_time)
    else:
        if simtime.update_time == 0.0:
            simtime.update_time = None
            st.rerun()


if 'world' not in st.session_state:
    if World.current:
        st.session_state.world = World.current
    else:
        st.session_state.world = MainWorldClass()

if type(st.session_state.world) is MainWorldClass:
    st.session_state.world.simulate(end_tick=30, realtime=True, stop_server=True)

draw_dashboard()
