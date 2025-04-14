from typing import Any, List, Literal, Optional

from .entity import Entity
from .queue import Queue

type TAKE_RESULT = Literal["success", "depleted", "queued", "in_use"]


class Resource[N: (int, float, None) = None]:
    """Representation of a resource in the simulation.

    This can either be a storage location for an amount of things,
    an item/tool/machine that can be used by a limited number of users,
    or a combination of both (e.g. a machine with a supply of a resource
    that also takes time to use).

    Usage:
        You can choose to make subclasses of :class:`Resource` to automatically
        more safely limit the types, or just create :class:`Resource` objects directly,
        using only :attr:`resource_type` do identify the kind of resource.
    """

    world: Any
    id: str
    resource_type: str
    users: List[Optional[Entity]]
    queue: Optional[Queue[Entity, N]]
    capacity: N
    amount: N

    def __init__(self, world: Any, id: str, resource_type: str, slots: int = 1,
                 max_queue: int = 0, capacity: N = 0, start_amount: N = 0):
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
        self.users = [None] * slots
        self.queue = Queue[Entity, N](id, max_queue) if max_queue > 0 else None
        self.capacity = capacity
        self.amount = start_amount

    def __eq__(self, other: object):
        if self is other:
            return True
        if self.amount is None:
            return other is None
        return self.amount == other

    def __lt__(self, other: object):
        if ((isinstance(self.amount, int) or isinstance(self.amount, float)) and
            (isinstance(other, int) or isinstance(other, float))):
            return self.amount < other
        return False

    def __le__(self, other: object):
        if ((isinstance(self.amount, int) or isinstance(self.amount, float)) and
            (isinstance(other, int) or isinstance(other, float))):
                return self.amount <= other
        return False

    def __gt__(self, other: object):
        if ((isinstance(self.amount, int) or isinstance(self.amount, float)) and
            (isinstance(other, int) or isinstance(other, float))):
                return self.amount > other
        return False

    def __ge__(self, other: object):
        if ((isinstance(self.amount, int) or isinstance(self.amount, float)) and
            (isinstance(other, int) or isinstance(other, float))):
                return self.amount >= other
        return False

    def __iadd__(self, other: N):
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount += int(other)
        if isinstance(self.amount, float):
            self.amount += other

    def __isub__(self, other: N):
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount -= int(other)
        if isinstance(self.amount, float):
            self.amount += other

    def __imul__(self, other: N):
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount *= int(other)
        if isinstance(self.amount, float):
            self.amount *= other

    def __itruediv__(self, other: N):
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount //= int(other)
        if isinstance(self.amount, float):
            self.amount /= other

    def __ifloordiv__(self, other: N):
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount //= int(other)
        if isinstance(self.amount, float):
            self.amount //= other

    def __imod__(self, other: N):
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount %= int(other)
        if isinstance(self.amount, float):
            self.amount %= other

    def __ipow__(self, other: N):
        if other is None:
            return
        if isinstance(self.amount, int):
            self.amount **= other

    def __int__(self):
        if isinstance(self.amount, int):
            return self.amount
        if isinstance(self.amount, float):
            return int(self.amount)
        return 0

    def __float__(self):
        if isinstance(self.amount, int):
            return float(self.amount)
        if isinstance(self.amount, float):
            return self.amount
        return 0.0

    def try_use(self, user: Entity, amount: N = None) -> TAKE_RESULT:
        if self < amount:
            if self.queue and self.queue.enqueue(user, amount):
                return "queued"

            return "depleted"

        if self > 0:
            if amount is None:
                raise ValueError(f"{user} is trying to use a capacity Resource without requested amount")
            self -= amount
            return "success"
        elif self.users.
        else:
            if self.queue and self.queue.enqueue(user, amount):
                return "queued"

            return "depleted"

    def __repr__(self):
        return (f"Resource {self.id}" if self.id == self.resource_type else
                f"Resource {self.id} of type {self.resource_type}")
