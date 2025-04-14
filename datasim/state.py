from abc import ABC
from typing import Self


class State(ABC):
    """The current behavior state of an :class:`Entity`.

    This should be the only place that entities execute behavior code.
    """

    name: str
    switch_to: Self | None

    def __init__(self, name: str):
        """Create a state object.

        Args:
            name (str): Descriptive name of this state.
        """
        self.name = name
        self.switch_to = None

    def tick(self):
        """Implement this function to have the state execute any behavior \
            for its entity."""
        pass
