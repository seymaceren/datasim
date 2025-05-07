from abc import ABC
from typing import Final, Optional, Self

import numpy as np

from .logging import log
from .types import LogLevel
from . import simulation


class Entity(ABC):
    """An entity in the simulation world.

    This can be anything that exhibits behavior.
    """

    plural: str = "Entities"

    registry: Final[dict[type, int]] = {}
    id: Final[int]
    name: Final[str]
    _state: "State | None" = None
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
            self.state = initial_state(initial_state.__name__, self)

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
            new_state = new_state(f"{self}{type.__name__}", self)
        if not isinstance(new_state, State):
            raise TypeError(
                f"Given type {new_state.__class__.__name__} is not a subclass of State!"
            )
        if new_state.entity is not None and new_state.entity != self:
            raise ValueError(f"{new_state} already belongs to {new_state.entity}!")
        new_state.entity = self

        if self._state:
            self._state.switch_to = new_state
        else:
            self._change_state(new_state)

    def _get_state(self) -> "State | None":
        return self._state

    state = property(
        _get_state, _set_state, None, """The current state of the entity."""
    )

    def _tick(self):
        if self._state:
            if self._state.switch_to != self._state:
                self._change_state(self._state.switch_to)
            if self._state:
                self._state.tick()

    def _change_state(self, new_state: "State | None"):
        if self._state == new_state:
            return

        log(
            f"{self}: {self._state.__class__.__name__} >> {new_state.__class__.__name__}",
            LogLevel.verbose,
        )
        if self._state:
            self.on_state_leaving(self._state, new_state)
        self._state = new_state
        if self._state:
            self._state.switch_to = self._state
            if self._state:
                self.on_state_entered(self._state, new_state)

        self.ticks_in_current_state = 0

    def on_state_entered(self, old_state: "State | None", new_state: "State | None"):
        """Implement this function to run when the state starts.

        Args:
            old_state (State or None): The current state that is being left.
            new_state (State or None): The state that will replace the current state.
        """
        pass

    def on_state_leaving(self, old_state: "State | None", new_state: "State | None"):
        """Implement this function to run when the current state is being left.

        Args:
            old_state (State or None): The state that was left.
            new_state (State or None): The new and current state.
        """
        pass

    def __str__(self) -> str:
        """Get a string representation of the entity."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Get a string representation of the entity."""
        return (
            "Unnamed Entity"
            if self.name is None
            else f"{self.__class__.__name__} {self.name}"
        )


class State(ABC):
    """The current behavior state of an :class:`Entity`.

    This should be the only place that entities execute behavior code.
    """

    _entity: Entity
    name: str
    completed: bool | None
    switch_to: Self | None

    def __init__(self, name: str, entity: Entity, completion: bool | None = None):
        """Create a state object.

        Args:
            name (str): Descriptive name of this state.
            entity (Entity): The entity this state belongs to.
            completion (bool or None, optional): Initial value of this state's `completed` variable,
                set to `False` if the state represents a task that can be completed or not.
        """
        self.name = name
        self.switch_to = None
        self.entity = entity
        self.completed = completion

    def _get_entity(self) -> Entity:
        return self._entity

    def _set_entity(self, entity: Entity):
        self._entity = entity

    entity = property(
        _get_entity, _set_entity, None, """The entity this state belongs to."""
    )

    def tick(self):
        """Implement this function to have the state execute any behavior \
            for its entity."""
        pass
