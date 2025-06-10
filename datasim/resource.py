from typing import Dict, Final, List, Optional, Self, Tuple

from .entity import Entity, State
from .logging import log
from .queue import Queue
from .types import LogLevel, Number, PlotOptions, PlotType, UseResult


class Resource:
    """Representation of a resource in the simulation.

    This can either be a storage location for an amount of things,
    an item/tool/machine that can be used by a limited number of users,
    or a combination of both (e.g. a machine with a supply of a resource
    that also takes time to use).

    Usage:
        You can choose to make subclasses of :class:`Resource` to automatically
        more safely limit the types and implement your own more complex usage logic,
        or just create :class:`Resource` objects directly, using only :attr:`resource_type`
        to identify the kind of resource, and set a single usage_time if more than 1 tick.
    """

    world: Final
    id: Final[str]
    resource_type: Final[str]
    users: List[Entity]
    user_index: Dict[Entity, int]
    slots: int
    usage_time: float
    simple_time_left: List[float]
    queue: Optional[Queue[Entity]]
    capacity: Number
    _amount: Number
    changed_tick: int

    _outputs: Final

    def __init__(
        self,
        world,
        id: str,
        resource_type: str,
        slots: int = 1,
        usage_time: float = 0.0,
        max_queue: int = 0,
        capacity: Number = None,
        start_amount: Number = None,
        gather: bool = True,
        data_id: str = "",
        sample_frequency: int = 1,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a resource.

        Args:
            world: The world to add this Resource to.
            id (`str`): Descriptive name of the resource.
            resource_type (`str`): Identifier of the resource in the pool.
            slots (`int`, optional): Number of possible simultaneous users.
                If set to `0`, the resource is a pure counter. Defaults to `1`.
            usage_time: The default amount of time one use of this resource takes.
                Set to `0.0` if the resource doesn't take time to use; if set to `0.0` and capacity
                is `None`, the resource only limits its usage on a single concurrent tick.
                You should probably only use that if your tick duration is very long. Defaults to `0.0`.
            max_queue (`int`, optional): Size of optional queue of users who can automatically
                (without a separate State) wait for the resource when occupied. Defaults to `0`.
            capacity (`int`, optional): Optional maximum amount stored in the pool. No maximum if set to 0.
                Defaults to `0`.
            start_amount (`int`, optional): Starting amount of resources in the pool. Defaults to `0`.
            gather (`PlotType` or `False`, optional): Whether to automatically gather data for the output
                for this resource, and which type of plot if so. Defaults to `PlotType.none` to only save.
            data_id (str, optional): id for the data source if `gather` is True. Defaults to empty string
                which sets `data_id` to the value of this Resource's `id`.
            sample_frequency (int, optional): Whether to add a data point every `frequency` ticks.
                If set to `0`, adds a data point only when the quantity changes. Defaults to `1`.
            plot_options (Optional[PlotOptions], optional): Options for a plot. Defaults to default PlotOptions.
        """
        self.world = world
        self.id = id
        self.resource_type = resource_type
        self.users = []
        self.user_index = {}
        self.slots = slots
        self.usage_time = usage_time
        self.simple_time_left = []
        self.queue = Queue[Entity](world, id, max_queue) if max_queue > 0 else None
        self.capacity = capacity
        self._amount = start_amount
        self.changed_tick = 0

        from .dataset import ResourceData

        self._outputs: List[ResourceData] = []

        self.world.add(self)

        if gather:
            self.add_output(data_id, sample_frequency, plot_options)

    @staticmethod
    def _from_yaml(world, params: Dict) -> "Resource":
        id = list(params.keys())
        if len(id) > 1:
            raise ValueError(f"Unable to parse yaml: Multiple keys found in {params}")

        id = id[0]
        params = params[id]

        return Resource(
            world,
            id,
            params["resource_type"],
            params.get("slots", 1),
            params.get("usage_time", 0),
            params.get("max_queue", 0),
            params.get("capacity", None),
            params.get("start_amount", None),
            params.get("gather", True),
            params.get("data_id", ""),
            params.get("sample_frequency", 1),
            PlotOptions._from_yaml(params.get("plot_options", {})),
        )

    def add_output(
        self,
        data_id: str = "",
        frequency: int = 1,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create an output source for this Resource. Also automatically used when `gather` is True at creation.

        Args:
            data_id (str, optional): Unique identifier of the source. Defaults to empty string which sets `data_id`
                to the value of this Resource's `id`.
            frequency (int, optional): Saves every x ticks or only on change if set to 0. Defaults to 0.
            plot_options (Optional[PlotOptions], optional): Options for a plot. Defaults to default PlotOptions.
        """
        from .dataset import ResourceData

        if data_id == "":
            data_id = self.id

        if plot_options.aggregate_only:
            plot_options.plot_type = PlotType.none
        elif plot_options.plot_type == PlotType.none:
            plot_options.plot_type = PlotType.line
        if plot_options.legend_y == "":
            plot_options.legend_y = self.resource_type

        data = ResourceData(
            self.world, self.id, self.capacity is None, frequency, plot_options
        )
        self._outputs.append(data)

        self.world.add_data(data_id, data)

    def _get(self) -> Number:
        return self._amount

    def _set(self, amount: int | float):
        self._amount = amount
        self.changed_tick = self.world.ticks

    amount = property(_get, _set, None, """Current amount of the resource.""")

    @property
    def occupied(self) -> bool:
        """Check if the resource is fully occupied."""
        return len(self.users) >= self.slots

    def try_use(
        self,
        user: Entity | Tuple[Entity, Number],
        amount: Number = None,
        usage_time: Optional[float] = None,
        remove_from_queue: Optional[Queue] = None,
    ) -> UseResult:
        """Try to use the resource.

        Taking a specified amount if this is a capacity resource,
        and using a slot if there are slots.

        Args:
            user (:class:`Entity`): The :class:`Entity` trying to use the resource, or a tuple with the amount included.
            amount (`int` or `float`, optional): The amount to take. Defaults to None.
            usage_time (`float`, optional): The time this use will take.
                If set to None, uses this resource's default usage time. Defaults to None.

        Raises:
            `TypeError`: When trying to take from a capacity resource without specifying an amount.

        Returns:
            :class:`TakeResult`: The result of the attempt.
        """
        if isinstance(user, tuple):
            amount = user[1]
            user = user[0]

        if self._amount is None:
            if not self.occupied:
                self.users.append(user)
                self.user_index[user] = len(self.users) - 1
                self.simple_time_left.append(
                    self.usage_time if usage_time is None else usage_time
                )

                user.state = UsingResourceState(self, user)
                return self._logResult(
                    UseResult.success, user, amount, remove_from_queue
                )
            else:
                if self.queue and self.queue.enqueue(user, amount):
                    return self._logResult(
                        UseResult.queued, user, amount, remove_from_queue
                    )

                return self._logResult(
                    UseResult.in_use, user, amount, remove_from_queue
                )
        elif self < amount:
            if self.queue and self.queue.enqueue(user, amount):
                return self._logResult(
                    UseResult.queued, user, amount, remove_from_queue
                )

            if self._amount == 0:
                return self._logResult(
                    UseResult.depleted, user, amount, remove_from_queue
                )
            else:
                return self._logResult(
                    UseResult.insufficient, user, amount, remove_from_queue
                )
        else:
            if amount is None:
                raise TypeError(
                    f"{user} is trying to use a capacity Resource without requested amount"
                )
            self -= amount
            return self._logResult(UseResult.success, user, amount, remove_from_queue)

    def _logResult(
        self,
        result: UseResult,
        user: Entity,
        amount: Number,
        remove_from_queue: Optional[Queue],
    ):
        usage = str(self) if self._amount is None else f"{amount} of {self}"
        log(
            f"{user} trying to use {usage}: {result}",
            LogLevel.verbose,
            "blue",
        )
        if result == UseResult.success and remove_from_queue is not None:
            remove_from_queue.dequeue()

        return result

    def remove_user(self, user: Entity) -> bool:
        """Try to remove a resource user.

        Returns:
            True if the user was successfully removed.
        """
        if user not in self.user_index:
            return False
        index = self.user_index[user]
        del self.users[index]
        del self.simple_time_left[index]
        del self.user_index[user]
        for other in range(index, len(self.users)):
            self.user_index[self.users[other]] = other
        return True

    def usage_tick(self, user: Entity) -> bool:
        """Override this function for more complex usage time than a flat number of time units."""
        index = self.user_index[user]
        left = self.simple_time_left[index]
        left -= self.world.tick_time
        if left <= 0:
            self.remove_user(user)
            return False

        self.simple_time_left[index] = left
        return True

    # region Utility functions

    def __eq__(self, other: object):
        """Check if the amount of the resource is equal to a number."""
        if self is other:
            return True
        if self._amount is None:
            return other is None
        return self._amount == other

    def __lt__(self, other: object):
        """Check if the amount of the resource is less than a number."""
        if (isinstance(self._amount, int) or isinstance(self._amount, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self._amount < other
        return False

    def __le__(self, other: object):
        """Check if the amount of the resource is less than or equal to a number."""
        if (isinstance(self._amount, int) or isinstance(self._amount, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self._amount <= other
        return False

    def __gt__(self, other: object):
        """Check if the amount of the resource is greater than a number."""
        if (isinstance(self._amount, int) or isinstance(self._amount, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self._amount > other
        return False

    def __ge__(self, other: object):
        """Check if the amount of the resource is greater than or equal to a number."""
        if other is None:
            return False
        if (isinstance(self._amount, int) or isinstance(self._amount, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self._amount >= other
        return False

    def __iadd__(self, other: Number) -> Self:
        """Add a number to the amount of the resource."""
        if other is None:
            return self
        if isinstance(self._amount, int):
            self.amount += int(other)
        elif isinstance(self._amount, float):
            self.amount += other
        return self

    def __isub__(self, other: Number) -> Self:
        """Subtract a number from the amount of the resource."""
        if other is None:
            return self
        if isinstance(self._amount, int):
            self.amount -= int(other)
        elif isinstance(self._amount, float):
            self.amount -= other
        return self

    def __imul__(self, other: Number) -> Self:
        """Multiply the amount of the resource by a number."""
        if other is None:
            return self
        if isinstance(self._amount, int):
            self.amount *= int(other)
        elif isinstance(self._amount, float):
            self.amount *= other
        return self

    def __itruediv__(self, other: Number) -> Self:
        """Divide the amount of the resource by a number."""
        if other is None:
            return self
        if isinstance(self._amount, int):
            self.amount //= int(other)
        elif isinstance(self._amount, float):
            self.amount /= other
        return self

    def __ifloordiv__(self, other: Number) -> Self:
        """Integer divide the amount of the resource by a number."""
        if other is None:
            return self
        if isinstance(self._amount, int):
            self.amount //= int(other)
        elif isinstance(self._amount, float):
            self.amount //= other
        return self

    def __imod__(self, other: Number) -> Self:
        """Make the amount of the resource the modulus of a number."""
        if other is None:
            return self
        if isinstance(self._amount, int):
            self.amount %= int(other)
        elif isinstance(self._amount, float):
            self.amount %= other
        return self

    def __ipow__(self, other: Number) -> Self:
        """Raise the amount of the resource by a power."""
        if other is None:
            return self
        if self._amount is not None:
            self.amount **= other
        return self

    def __int__(self):
        """Get the amount of this resource as an int. Returns -1 if the resource has no amount."""
        if isinstance(self._amount, int):
            return self._amount
        elif isinstance(self._amount, float):
            return int(self._amount)
        return -1

    def __float__(self):
        """Get the amount of this resource as a float. Returns -1.0 if the resource has no amount."""
        if isinstance(self._amount, int):
            return float(self._amount)
        if isinstance(self._amount, float):
            return self._amount
        return -1.0

    def __str__(self) -> str:
        """Get a string representation of the resource."""
        return self.__repr__()

    def __repr__(self):
        """Get a string representation of the resource."""
        return (
            f"Resource {self.id}"
            if self.id == self.resource_type
            else f"Resource {self.id} of type {self.resource_type}"
        )

    # endregion


class UsingResourceState(State):
    """State in which an Entity is using a :class:`Resource`."""

    type_id: str = "UsingResource"

    resource: Resource

    def __init__(self, resource: Resource, entity: Entity):
        """Create a :class:`UsingResourceState` for the specified :class:`Resource`.

        Args:
            resource (:class:`Resource`): The :class:`Resource` being used.
        """
        super().__init__(f"using {resource}", entity, False)
        self.resource = resource
        self.type_id = f"Using_{resource.resource_type}"

    def tick(self):
        """Use the resource for one tick."""
        if not hasattr(self, "entity"):
            raise ValueError("UsingResourceState has no entity set!")
        if not self.resource.usage_tick(self.entity):
            self.completed = True
            self.switch_to = None
