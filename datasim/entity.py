from abc import ABC
from typing import Final, Optional, Self

import numpy as np

import simulation


class Entity(ABC):
    """An entity in the simulation world.

    This can be anything that exhibits behavior.
    """

    registry: Final[dict[type, int]] = {}
    id: Final[int]
    name: Final[str]
    _state: "State | None"
    ticks_in_current_state: int
    location: Optional[np.typing.NDArray[np.float64]]

    def __init__(
        self,
        name: Optional[str] = None,
        initial_state: Optional["State | type[State]"] = None,
    ):
        """Create an entity.

        Args:
            name (Optional[str], optional): Descriptive name of the entity. Defaults to None.
            initial_state (Optional[State or type], optional): Initial state of the entity. If using a type,
                that type needs to have a constructor with only name as paramater. Defaults to None,
                meaning no behavior will be executed.
        """
        # Give the entity a serial number
        self.id = Entity.registry.get(type(self), 0) + 1
        Entity.registry[type(self)] = self.id
        # Use the serial number as name if no name is given
        if not name:
            name = f"{str(type(self))} {self.id:03}"
        self.name = name
        if isinstance(initial_state, State):
            self.state = initial_state
        elif isinstance(initial_state, type):
            self.state = initial_state(initial_state.__name__)
        else:
            self.state = None

        if self.state:
            self.state.switch_to = self.state
            self.state.entity = self

        self.ticks_in_current_state = 0

        simulation.world().add(self)

    def _set_state(self, new_state: "State | type"):
        """Change the state of the entity.

        The new behavior will be executed starting at the next tick.

        Args:
            new_state (State | type): The new state of the entity.
                This can also be a State subtype, in which case a default object
                of that class will be created to execute update ticks.

        Raises:
            TypeError: If the provided type is not a subclass of :class:`State`.
        """
        if isinstance(new_state, type):
            new_state = new_state()
        if not isinstance(new_state, State):
            raise TypeError("Given type is not a subclass of State")

        if self._state:
            self._state.switch_to = new_state
        else:
            self._change_state(new_state)

    def _get_state(self) -> "State | None":
        return self._state

    state = property(
        _get_state, _set_state, None, """The current state of the entity."""
    )

    def resource_done(self, resource):
        """Override to run when this entity's UsingResourceState is done."""
        pass

    def _tick(self):
        if self._state:
            self._state.tick()
            if self._state.switch_to != self._state:
                self._change_state(self._state.switch_to)

    def _change_state(self, new_state):
        if self._state == new_state:
            return

        print(
            f"{self}: {self._state.__class__.__name__} >> {new_state.__class__.__name__}"
        )
        self._state = new_state
        if self._state:
            self._state.entity = self
            self._state.switch_to = self._state

        self.ticks_in_current_state = 0

    def __repr__(self):
        """Get a string representation of the entity."""
        return "Unnamed Entity" if self.name is None else f"Entity {self.name}"


class State(ABC):
    """The current behavior state of an :class:`Entity`.

    This should be the only place that entities execute behavior code.
    """

    entity: Entity
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
