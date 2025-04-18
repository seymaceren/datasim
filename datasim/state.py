from abc import ABC
from typing import Any, Generic, Self

from .resource import Resource
from .types import Number


class State(ABC):
    """The current behavior state of an :class:`Entity`.

    This should be the only place that entities execute behavior code.
    """

    entity: Any = None
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


class UsingResourceState(Generic[Number], State):
    """State in which an Entity is using a :class:`Resource`."""

    resource: Resource[Number]

    def __init__(self, resource: Resource[Number]):
        """Create a :class:`UsingResourceState` for the specified :class:`Resource`.

        Args:
            resource (:class:`Resource`): The :class:`Resource` being used.
        """
        super().__init__(f"using {resource}")
        self.resource = resource

    def tick(self):
        """Use the resource for one tick."""
        if self.entity is None:
            return
        self.resource.usage_tick(self.entity)
