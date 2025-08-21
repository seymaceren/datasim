from importlib import import_module
from sys import argv, modules

from datasim import logging, LogLevel, Runner


world_class = None
output_path = None
for arg in argv:
    if arg.startswith("world="):
        world_class = arg[6:]
    if arg.startswith("-o="):
        output_path = arg[3:]
    if arg.startswith("--out-path="):
        output_path = arg[11:]


if not world_class:
    print(
        """Usage: [streamlit run]/[python] datasim.py [options] world=<classname>
    classname: specify the main World class

    Options:
    -d / --debug: print debug output
    -v / --verbose: print all verbose output
    -o=<path> / --out-path=<path>: save output in the specified directory
    -s / --split-worlds: split output into one file per run
    --clear-output: first delete anything in the specified output directory (use with caution!)
    -c / --csv: save csv output instead of Pickle"""
    )
    exit()

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

if "-v" in argv or "--verbose" in argv:
    logging.level = LogLevel.verbose
elif "-d" in argv or "--debug" in argv:
    logging.level = LogLevel.debug

output_csv = "-c" in argv or "--csv" in argv

split_worlds = "-s" in argv or "--split-worlds" in argv

clear_output = "--clear-output" in argv


if "streamlit" in modules:
    import streamlit as st

    if "runner" not in st.session_state:
        st.session_state.update_time = 1.0
        st.session_state.runner = Runner(
            world_class_object,
            auto_output_path=output_path,
            clear_auto_output_path=clear_output,
            auto_output_csv=output_csv,
            split_worlds=split_worlds,
        )

    any_active = st.session_state.runner.simulate(stop_server=False)

    if not any_active:
        st.session_state.update_time = None
    else:
        from datasim.streamlit_update import draw_dashboard

        draw_dashboard()

else:
    runner = Runner(
        world_class_object,
        headless=True,
        auto_output_path=output_path,
        clear_auto_output_path=clear_output,
        auto_output_csv=output_csv,
    ).simulate()
