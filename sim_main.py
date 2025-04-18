import sys
from time import sleep
from typing import Optional
import streamlit as st

from datasim import Dashboard
from datasim import World

# Use this line to specify your main world class
from examples.icu.icu import ICU as MainWorldClass


@st.fragment(run_every=World.update_time)
def draw_dashboard():
    # Draw our dashboard if it has been initialized
    dash: Optional[Dashboard] = st.session_state.dashboard
    if not dash:
        return
    dash._draw()

    # Logic to let the dashboard update during the simulation,
    # and to stop rerunning the Streamlit fragment when the simulation has ended
    if World.update_time and World.update_time > 0.0:
        sleep(World.update_time)
    else:
        if World.update_time == 0.0:
            World.update_time = None
            st.rerun()


if "streamlit" in sys.argv:
    if "world" not in st.session_state:
        if World.current:
            st.session_state.world = World.current
        else:
            st.session_state.world = MainWorldClass()

    if type(st.session_state.world) is MainWorldClass:
        st.session_state.world.simulate(end_tick=7000, stop_server=True)

    draw_dashboard()

else:
    MainWorldClass(headless=True).simulate(end_tick=7000)
