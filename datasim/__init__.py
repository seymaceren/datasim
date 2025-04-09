"""This module provides a framework for generating data by running simulations."""

from .dashboard import Dashboard
from .entity import Entity
from .plot import Plot
from .queue import Queue
from .resource import Resource
from .state import State
from .world import World
__all__ = ("Dashboard", "Entity", "Plot", "Queue", "Resource", "State", "World")
