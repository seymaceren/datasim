from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .entity import Entity, State
from .queue import Queue
from .types import Number


class UseResult(Enum):
    """The result of a resource usage attempt."""

    success = "success"
    depleted = "depleted"
    queued = "queued"
    in_use = "in_use"

    def __str__(self) -> str:
        """Get a string representation of the result."""
        match self:
            case UseResult.success:
                return "Success"
            case UseResult.depleted:
                return "Failed: Resource depleted"
            case UseResult.queued:
                return "Queued"
            case UseResult.in_use:
                return "Failed: Resource in use"


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

    world: Any
    id: str
    resource_type: str
    users: List[Entity]
    user_index: Dict[Entity, int]
    slots: int
    usage_time: int
    simple_time_left: List[int]
    queue: Optional[Queue[Entity]]
    capacity: Number
    amount: Number

    def __init__(
        self,
        world: Any,
        id: str,
        resource_type: str,
        slots: int = 1,
        usage_time: int = 1,
        max_queue: int = 0,
        capacity: Number = None,
        start_amount: Number = None,
    ):
        """Create a resource.

        Args:
            id (str): Descriptive name of the resource.
            resource_type (str): Identifier of the resource in the pool.
            slots (int, optional): Number of possible simultaneous users.
                If set to 0, the resource is a pure counter. Defaults to 1.
            max_queue (int, optional): Size of optional queue of users who can automatically
                (without a separate State) wait for the resource when occupied. Defaults to 0.
            capacity (int, optional): Optional maximum amount stored in the pool. No maximum if set to 0. Defaults to 0.
            start_amount (int, optional): Starting amount of resources in the pool. Defaults to 0.
        """
        self.world = world
        self.id = id
        self.resource_type = resource_type
        self.users = []
        self.user_index = {}
        self.slots = slots
        self.usage_time = usage_time
        self.simple_time_left = []
        self.queue = Queue[Entity](id, max_queue) if max_queue > 0 else None
        self.capacity = capacity
        self.amount = start_amount

    @property
    def occupied(self) -> bool:
        """Check if the resource is fully occupied."""
        return len(self.users) >= self.slots

    def try_use(
        self, user: Entity | Tuple[Entity, Number], amount: Number = None
    ) -> UseResult:
        """Try to use the resource.

        Taking a specified amount if this is a capacity resource,
        and using a slot if there are slots.

        Args:
            user (:class:`Entity`): The :class:`Entity` trying to use the resource, or a tuple with the amount included.
            amount (`int` or `float`, optional): The amount to take. Defaults to None.

        Raises:
            `TypeError`: When trying to take from a capacity resource without specifying an amount.

        Returns:
            :class:`TakeResult`: The result of the attempt.
        """
        if isinstance(user, tuple):
            amount = user[1]
            user = user[0]

        if self < amount:
            if self.queue and self.queue.enqueue(user, amount):
                return UseResult.queued

            return UseResult.depleted

        if self > 0:
            if amount is None:
                raise TypeError(
                    f"{user} is trying to use a capacity Resource without requested amount"
                )
            self -= amount
            return UseResult.success
        elif not self.occupied:
            self.users.append(user)
            self.user_index[user] = len(self.users) - 1
            self.simple_time_left.append(self.usage_time)

            user.set_state(UsingResourceState(self))
            return UseResult.success
        else:
            if self.queue and self.queue.enqueue(user, amount):
                return UseResult.queued

            return UseResult.depleted

    def usage_tick(self, user: Entity) -> bool:
        """Override this function for more complex usage time than a flat number of seconds."""
        index = self.user_index[user]
        left = self.simple_time_left[index]
        left -= 1
        if left <= 0:
            del self.users[index]
            del self.simple_time_left[index]
            return False

        self.simple_time_left[index] = left
        return True

    # region Utility functions

    def __eq__(self, other: object):
        """Check if the amount of the resource is equal to a number."""
        if self is other:
            return True
        if self.amount is None:
            return other is None
        return self.amount == other

    def __lt__(self, other: object):
        """Check if the amount of the resource is less than a number."""
        if (isinstance(self.amount, int) or isinstance(self.amount, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self.amount < other
        return False

    def __le__(self, other: object):
        """Check if the amount of the resource is less than or equal to a number."""
        if (isinstance(self.amount, int) or isinstance(self.amount, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self.amount <= other
        return False

    def __gt__(self, other: object):
        """Check if the amount of the resource is greater than a number."""
        if (isinstance(self.amount, int) or isinstance(self.amount, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self.amount > other
        return False

    def __ge__(self, other: object):
        """Check if the amount of the resource is greater than or equal to a number."""
        if other is None:
            return False
        if (isinstance(self.amount, int) or isinstance(self.amount, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self.amount >= other
        return False

    def __iadd__(self, other: Number):
        """Add a number to the amount of the resource."""
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount += int(other)
        elif isinstance(self.amount, float):
            self.amount += other

    def __isub__(self, other: Number):
        """Subtract a number from the amount of the resource."""
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount -= int(other)
        elif isinstance(self.amount, float):
            self.amount += other

    def __imul__(self, other: Number):
        """Multiply the amount of the resource by a number."""
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount *= int(other)
        elif isinstance(self.amount, float):
            self.amount *= other

    def __itruediv__(self, other: Number):
        """Divide the amount of the resource by a number."""
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount //= int(other)
        elif isinstance(self.amount, float):
            self.amount /= other

    def __ifloordiv__(self, other: Number):
        """Integer divide the amount of the resource by a number."""
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount //= int(other)
        elif isinstance(self.amount, float):
            self.amount //= other

    def __imod__(self, other: Number):
        """Make the amount of the resource the modulus of a number."""
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount %= int(other)
        elif isinstance(self.amount, float):
            self.amount %= other

    def __ipow__(self, other: Number):
        """Raise the amount of the resource by a power."""
        if other is None:
            return
        if self.amount is not None:
            self.amount **= other

    def __int__(self):
        """Get the amount of this resourcce as an int. Returns -1 if the resource has no amount."""
        if isinstance(self.amount, int):
            return self.amount
        elif isinstance(self.amount, float):
            return int(self.amount)
        return -1

    def __float__(self):
        """Get the amount of this resourcce as a float. Returns -1.0 if the resource has no amount."""
        if isinstance(self.amount, int):
            return float(self.amount)
        if isinstance(self.amount, float):
            return self.amount
        return -1.0

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

    from .resource import Resource

    resource: Resource

    def __init__(self, resource: Resource):
        """Create a :class:`UsingResourceState` for the specified :class:`Resource`.

        Args:
            resource (:class:`Resource`): The :class:`Resource` being used.
        """
        super().__init__(f"using {resource}")
        self.resource = resource

    def tick(self):
        """Use the resource for one tick."""
        if self.entity is None:
            raise ValueError("UsingResourceState has no entity set!")
        if not self.resource.usage_tick(self.entity):
            self.switch_to = None
