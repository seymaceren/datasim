from abc import ABC
from typing import Final, Optional

import numpy as np

from .state import State

class Entity(ABC):
    registry: Final[dict[type, int]] = {}
    id: Final[int]
    name: Final[str]
    state: Optional[State]
    location: Optional[np.typing.NDArray[np.float64]]

    def __init__(self, name: Optional[str] = None, initial_state: Optional[State] = None):
        # Give the entity a serial number
        self.id = Entity.registry.get(type(self), 0) + 1
        Entity.registry[type(self)] = self.id
        # Use the serial number as name if no name is given
        if not name:
            name = f"{str(type(self))} {self.id:03}"
        self.name = name
        self.state = initial_state

    def tick(self):
        if self.state:
            self.state.tick()
            if self.state.switch_to:
                self.state = self.state.switch_to
