from typing import Final, List
from .entity import Entity


class Queue:
    """A queue for entities to wait for resource availability."""

    id: Final[str]
    queue: Final[List[Entity]]

    def __init__(self, id: str):
        """Create a waiting queue for entities.

        Args:
            id (str): Identifier / name of the queue.
        """
        self.id = id
        self.queue = []

    def enqueue(self, entity: Entity):
        """Put an entity at the end of the queue.

        Args:
            entity (Entity): The entity to enqueue.
                Beware: If this entity is already in the list, it will be added another time.
        """
        self.queue.insert(0, entity)

    def dequeue(self) -> Entity:
        """Remove the entity from the front of the queue and returns it.

        Returns:
            Entity: The entity that was at the front of this queue.
        """
        return self.queue.pop()

    def peek(self) -> Entity:
        """Return the entity at the front of the queue without removing it.

        Returns:
            Entity: The entity at the front of this queue.
        """
        return self.queue[-1]

    def prioritize(self, entity: Entity) -> bool:
        """Pushes an entity to the front of the list.

        If the entity was not in the list, it will not be added;
        If the entity is in the list more than once, the copy furthest to the back will be put at the front.

        Args:
            entity (Entity): _description_
        """
        if self.queue.remove(entity):
            self.queue.append(entity)
            return True

        return False
