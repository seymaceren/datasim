import sys
import streamlit as st

from datasim import logging, LogLevel, simulation

# Use this line to specify your main world class
from examples.icu.icu import ICU as MainWorldClass


if "streamlit" in sys.argv:
    logging.level = LogLevel.debug

    if "world" not in st.session_state:
        if simulation.active:
            st.session_state.world = simulation.world()
        else:
            profiling = True
            st.session_state.world = MainWorldClass()

    if type(st.session_state.world) is MainWorldClass:
        st.session_state.world.simulate(stop_server=False)

    from datasim.streamlit_update import draw_dashboard

    draw_dashboard()

else:
    logging.level = LogLevel.verbose
    MainWorldClass(headless=True).simulate()
