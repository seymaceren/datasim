from typing import List, Optional

from .entity import Entity
from .queue import Queue


class Resource:
    """Representation of a resource in the simulation.

    This can either be a storage location for an amount of things,
    an item/tool/machine that can be used by a limited number of users,
    or a combination of both (e.g. a machine with a supply of a resource
    that also takes time to use).

    Usage:
        You can choose to make subclasses of `Resource` to automatically
        more safely limit the types, or just create `Resource` objects directly,
        using only `resource_type` do identify the kind of resource.
    """

    id: str
    resource_type: str
    users: List[Optional[Entity]]
    queue: Queue
    capacity: int
    amount: int

    def __init__(self, id: str, resource_type: str, slots: int = 1,
                 max_queue: int = 0, capacity: int = 0, start_amount: int = 0):
        """Create a resource.

        Args:
            id (str): Descriptive name of the resource.
            resource_type (str): Identifier of the resource in the pool.
            slots (int, optional): Number of possible simultaneous users.
                If set to 0, the resource is a pure counter. Defaults to 1.
            max_queue (int, optional): Size of optional queue of users who can wait
                for the resource when occupied. Defaults to 0.
            capacity (int, optional): Optional maximum amount stored in the pool. No maximum if set to 0. Defaults to 0.
            start_amount (int, optional): Starting amount of resources in the pool. Defaults to 0.
        """
        self.id = id
        self.resource_type = resource_type
        self.users = [None] * slots
        if max_queue > 0:
            self.queue = Queue(id)
        self.capacity = capacity
        self.amount = start_amount
