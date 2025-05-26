from importlib import import_module
from sys import argv
import streamlit as st

from datasim import logging, LogLevel, Runner


world_class = None
for arg in argv:
    if arg.startswith("world="):
        world_class = arg[6:]


if not world_class:
    raise SyntaxError(
        "No valid world class specified. Add 'world=<classname>' to your command line to specify the main World class."
    )

split = world_class.rfind(".")

world_class_module = import_module(world_class[:split])

if not world_class_module:
    raise SyntaxError(f"World class '{world_class}' not found!")

split += 1
try:
    world_class_object = getattr(world_class_module, world_class[split:])
except Exception:
    raise SyntaxError(
        f"World class '{world_class[split:]}' not found in module '{world_class_module}'!"
    )

if "-v" in argv:
    logging.level = LogLevel.verbose
elif "-d" in argv:
    logging.level = LogLevel.debug


if "streamlit" in argv:
    if "runner" not in st.session_state:
        st.session_state.update_time = 1.0
        st.session_state.runner = Runner(world_class_object)

    any_active = st.session_state.runner.simulate(stop_server=False)

    if not any_active:
        st.session_state.update_time = None
    else:
        from datasim.streamlit_update import draw_dashboard

        draw_dashboard()

else:
    Runner(world_class_object, headless=True).simulate()
