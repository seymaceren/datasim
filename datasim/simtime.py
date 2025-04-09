ticks: int = 0
tps: float = 10.0

update_time: float = 1.0


def seconds() -> float:
    """Get the current number of seconds elapsed in simulation time."""
    return ticks / tps
