from typing import Final, Generic, List, Tuple, TypeVar

from .entity import Entity
from .types import Number

EntityType = TypeVar("EntityType", bound=Entity)


class Queue(Generic[EntityType]):
    """A queue for entities to wait for resource availability."""

    id: Final[str]
    queue: Final[List[Tuple[EntityType, Number]]]
    capacity: int

    def __init__(self, id: str, capacity: int = 0):
        """Create a waiting queue for entities.

        Args:
            id (str): Identifier / name of the queue.
            capacity (int): Maximum queue length. Defaults to 0 for no maximum.
        """
        self.id = id
        self.capacity = capacity
        self.queue = []

    @property
    def full(self) -> bool:
        """Check the queue is full."""
        return 0 < self.capacity <= len(self.queue)

    def __len__(self) -> int:
        """Get the current length of the queue."""
        return len(self.queue)

    def __int__(self) -> int:
        """Get the current length of the queue."""
        return self.__len__()

    def enqueue(self, entity: EntityType, amount: Number = None) -> bool:
        """Put an entity at the end of the queue.

        Args:
            entity (T): The entity to enqueue.
                Beware: If this entity is already in the list, it will be added another time.
            amount (int or float, optional): The amount that the entity wants to take from the resource.
                Defaults to None.

        Returns:
            bool:
                If the entity was succesfully added to the queue.
        """
        if not self.full:
            self.queue.insert(0, (entity, amount))
            return True

        return False

    def dequeue(self) -> EntityType | Tuple[EntityType, Number]:
        """Remove the entity from the front of the queue and returns it.

        Returns:
            Entity: The entity that was at the front of this queue.
        """
        (e, a) = self.queue.pop()
        if a is None:
            return e
        return (e, a)

    def peek(self) -> EntityType:
        """Return the entity at the front of the queue without removing it.

        Returns:
            Entity: The entity at the front of this queue.
        """
        (e, a) = self.queue[-1]
        return e

    def peek_with_amount(self) -> Tuple[EntityType, Number]:
        """Return the entity at the front of the queue without removing it.

        Returns:
            Entity: The entity at the front of this queue.
        """
        return self.queue[-1]

    def prioritize(self, entity: EntityType) -> bool:
        """Pushes an entity to the front of the list.

        If the entity was not in the list, it will not be added;
        If the entity is in the list more than once, the copy furthest to the back will be put at the front.

        Args:
            entity (Entity): _description_
        """
        (_, entry) = [
            (i, (e, a)) for i, (e, a) in enumerate(self.queue) if e is entity
        ][0]
        if self.queue.remove(entry):
            self.queue.append(entry)
            return True

        return False

    def __repr__(self):
        """Get a string representation of this queue."""
        return f"Queue {self.id} length {len(self.queue)}" + (
            "" if self.capacity == 0 else "/{self.capacity}"
        )
