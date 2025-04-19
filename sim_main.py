import sys
import streamlit as st

from datasim import World

# Use this line to specify your main world class
from examples.icu.icu import ICU as MainWorldClass


if "streamlit" in sys.argv:
    if "world" not in st.session_state:
        if World.active:
            st.session_state.world = World.current
        else:
            profiling = True
            st.session_state.world = MainWorldClass()

    if type(st.session_state.world) is MainWorldClass:
        st.session_state.world.simulate(end_tick=7000, stop_server=False)

    from datasim.streamlit_update import draw_dashboard

    draw_dashboard()

else:
    MainWorldClass(headless=True).simulate(end_tick=7000)
