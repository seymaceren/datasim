# DataSim

[![Test Status](https://github.com/sabvdf/datasim/actions/workflows/code-tests.yml/badge.svg)](https://github.com/sabvdf/datasim/actions/workflows/code-tests.yml)
[![Docs Status](https://github.com/sabvdf/datasim/actions/workflows/docs-pages.yml/badge.svg)](https://github.com/sabvdf/datasim/actions/workflows/docs-pages.yml)
[![Coverage Status](https://coveralls.io/repos/github/sabvdf/datasim/badge.svg?branch=main)](https://coveralls.io/github/sabvdf/datasim?branch=main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Quick Python data generating simulation tool with readable code and optional dashboard.

> [!WARNING]
> Work in progress: this code base is not fully functional yet. Study at your own risk, usage for real projects is slightly discouraged.

The code is meant to be as short as possible without too many bells and whistles, leaving anything other than the main simulation to external proven libraries.

The simulation is optionally tied to a Streamlit dashboard, from which the generated data can be easily exported as Pickle or CSV files.

Without the dashboard, generated data can be automatically saved from the command line running the simulation.

## API Documentation
Auto-generated, on [sabvdf.github.io/datasim](https://sabvdf.github.io/datasim/)

## Usage (warning: outdated!)
See sample code, the basic setup is:

- Implement entities as subclasses of `datasim.Entity` and their behavior as subclasses of `datasim.State`
- Implement a subclass of `datasim.World`
  - Add any needed entities in `__init__()` after calling `super().__init__("NAME_HERE")`
  - Add plots in `update_plots()`
- Run `datasim.py` in the following way:

  ```python
  Usage: [streamlit run]/[python] datasim.py [options] world=<classname>
    classname: specify the main World class

    Options:
    -d / --debug: print debug output
    -v / --verbose: print all verbose output
    -o=<path> / --out-path=<path>: save output in the specified directory
    -s / --split-worlds: split output into one file per run
    --clear-output: first delete anything in the specified output directory (use with caution!)
    -c / --csv: save csv output instead of Pickle
  
  Example: streamlit run datasim.py -v world=examples.icu.icu.ICU
  ```

## Plans
### Beta
Before calling a release 0.9 (beta), I plan to implement the following:

- Output all data from the simulation
- Add entity generator class using Numpy random distributions
  - With options for skewed or biased distributions
- Add more options to the batch runner
  - Using different (combinations of) source data files and generators
  - Outputting plots and data aggregated over the runs
- Automatically save data from a command line invocation
- Get test coverage to 100%

### Future versions
After an initial version, I have more ideas to expand the functionalities:

- Add a physics mode (using a library) to entities, so that it's possible to run more complex simulations
- Show a live updating representation of a longer running simulation with physical representation
