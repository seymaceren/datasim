from abc import ABC
from typing import Any, Final, List, Optional, Self

import numpy as np

from .logging import log
from .types import LogLevel, PlotOptions, PlotType


class Entity(ABC):
    """An entity in the simulation world.

    This can be anything that exhibits behavior.
    """

    plural: str = "Entities"

    world: Any
    id: Final[str]
    index: Final[int]
    _state: "State | None" = None
    _outputs: Final
    ticks_in_current_state: int
    location: Optional[np.typing.NDArray[np.float64]]

    def __init__(
        self,
        world: Any,
        id: Optional[str] = None,
        initial_state: Optional["State | type[State]"] = None,
        gather: bool = False,
        data_id: str = "",
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create an entity.

        Args:
            name (Optional[str], optional): Descriptive name of the entity. Defaults to None.
            initial_state (Optional[State or type], optional): Initial state of the entity. If using a type,
                that type needs to have a constructor with only name as paramater. Defaults to None,
                meaning no behavior will be executed.
        """
        self.world = world
        # Give the entity a serial number
        self.index = world._entity_registry.get(type(self), 0) + 1
        world._entity_registry[type(self)] = self.index
        # Use the serial number as name if no name is given
        if id is None:
            id = f"{str(type(self))} {self.index:03}"
        self.id = id
        if isinstance(initial_state, State):
            self.state = initial_state
        elif isinstance(initial_state, type):
            self.state = initial_state(initial_state.__name__, self)

        if self.state:
            self.state.switch_to = self.state
            self.state.entity = self

        self.ticks_in_current_state = 0

        from .dataset import StateData

        self._outputs: List[StateData] = []

        if gather:
            if plot_options.auto_name:
                plot_options.name = str(self)
            self.add_output(data_id, plot_options)

        self.world.add(self)

    def add_output(
        self,
        data_id: str = "",
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a plot for this Resource. Also automatically used when `gather` is True at creation.

        Args:
            plot_type (PlotType, optional): The type of plot to add. Defaults to PlotType.line.
            frequency (int, optional): Saves every x ticks or only on change if set to 0. Defaults to 0.
            plot_title (Optional[str], optional): Optional title for the plot. Defaults to None.
        """
        from .dataset import StateData

        if (
            plot_options.aggregate_only
            and plot_options.plot_type != PlotType.export_only
        ):
            plot_options.plot_type = PlotType.none

        if data_id == "":
            data_id = str(self)

        if plot_options.legend_y == "":
            plot_options.legend_y = "state"

        self.world.add_data(
            data_id,
            StateData(self.world, self, 0, plot_options),
        )

    def _link_output(self, data_source):
        self._outputs.append(data_source)

    def _bind_state(self, new_state: "State | type | None") -> "State | None":
        if new_state is None:
            return None
        if isinstance(new_state, type):
            new_state = new_state(f"{self}{type.__name__}", self)
        if not isinstance(new_state, State):
            raise TypeError(
                f"Given type {new_state.__class__.__name__} is not a subclass of State!"
            )
        if new_state.entity is None:
            new_state.entity = self
        elif new_state.entity != self:
            raise ValueError(f"{new_state} already belongs to {new_state.entity}!")

        return new_state

    def _set_state(self, new_state: "State | type | None"):
        """Change the state of the entity.

        The new behavior will be executed starting at the next tick.

        Args:
            new_state (State | type): The new state of the entity.
                This can also be a State subtype, in which case a default object
                of that class will be created to execute update ticks.

        Raises:
            TypeError: If the provided type is not a subclass of :class:`State`.
        """
        new_state = self._bind_state(new_state)

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
        self.ticks_in_current_state += 1

    @property
    def time_in_current_state(self) -> float:
        return self.ticks_in_current_state / self.world.tpu

    def _change_state(self, new_state: "State | None"):
        if self._state == new_state:
            return

        if self._state:
            new_state = self._bind_state(self.on_state_leaving(self._state, new_state))

        log(
            f"{self}: {self._state.__class__.__name__} >> {new_state.__class__.__name__}",
            LogLevel.verbose,
            world=self.world,
        )

        self.changed_tick = self.world.ticks

        self._state = new_state
        if self._state:
            self._state.switch_to = self._state
            if self._state:
                self.on_state_entered(self._state, new_state)

        self.ticks_in_current_state = 0

    def remove(self):
        """Remove this `Entity` from its `World`."""
        self.world.remove(self)

    def on_state_entered(self, old_state: "State | None", new_state: "State | None"):
        """Implement this function to run when the state starts.

        Args:
            old_state (State or None): The state that the current state has replaced.
            new_state (State or None): The current state that is being started.
        """
        pass

    def on_state_leaving(
        self, old_state: "State | None", new_state: "State | None"
    ) -> "State | type | None":
        """Implement this function to run when the current state is being left.

        Can be used (with care) to override the new state to enter.

        Args:
            old_state (State or None): The state that was left.
            new_state (State or None): The new and current state.
        Returns:
            (State or None): The new state to enter. Make sure to return `new_state`
            or the result of the superclass function when you override this.
        """
        return new_state

    def __str__(self) -> str:
        """Get a string representation of the entity."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Get a string representation of the entity."""
        return f"{self.__class__.__name__} {self.id}"


class State(ABC):
    """The current behavior state of an :class:`Entity`.

    This should be the only place that entities execute behavior code.
    """

    _entity: Entity
    name: str
    completed: bool | None
    switch_to: Self | None
    type_id: str = "State (base class!)"

    def __init__(
        self,
        name: str,
        entity: Entity,
        completion: bool | None = None,
    ):
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

    def __eq__(self, object):
        """Directly compare a State object to a type to check if it is an instance of that type."""
        return self is object or (isinstance(object, type) and isinstance(self, object))
