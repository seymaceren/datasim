import sys
from runpy import run_module

# This main file is used to run Streamlit from python code without the command line tool.
# You can also run the application using 'streamlit run sim_main.py'.
sys.argv = ["streamlit", "run", "sim_main.py", "streamlit"]
run_module("streamlit", run_name="__main__")
