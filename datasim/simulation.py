"""Global simulation properties."""

"""Number of ticks elapsed in the current simulation."""
ticks: int = 0
"""Number of time units elapsed in the current simulation."""
time: float = 0.0
"""The maximum number of ticks the simulation will run, if greater than 0."""
end_tick: int = 0
"""Time unit."""
time_unit: str = "seconds"
"""Number of ticks per simulated time unit (or also real time if running in realtime mode)."""
tpu: float = 10.0
"""Number of simulated time units per tick (or also real time if running in realtime mode)."""
tick_time: float = 0.1

"""Checks if the simulation is active."""
active: bool = False


def world():
    """Get the current simulation `World`."""
    from .world import World

    return World.current


def constant(*keys) -> int | float | str:
    """Get a constant from the current simulation."""
    from .world import World

    obj = World.current.constants
    for key in keys:
        obj = obj.get(key, None)
        if obj is None:
            raise KeyError(f"Key {key} not found in lookup {keys[:]}")

    if (
        not isinstance(obj, int)
        and not isinstance(obj, float)
        and not isinstance(obj, str)
    ):
        raise TypeError(f"{keys[:]} is not a constant!")

    return obj
