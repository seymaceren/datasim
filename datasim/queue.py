from typing import Final, List
from .entity import Entity


class Queue:
    """A queue for entities to wait for resource availability."""

    id: Final[str]
    queue: Final[List[Entity]]

    def __init__(self, id: str):
        """TODO: write.

        Args:
            id (str): _description_
        """
        self.id = id
        self.queue = []

    def enqueue(self, entity: Entity):
        """TODO: write.

        Args:
            entity (Entity): _description_
        """
        self.queue.insert(0, entity)

    def dequeue(self) -> Entity:
        """TODO: write.

        Returns:
            Entity: _description_
        """
        return self.queue.pop()

    def prioritize(self, entity: Entity):
        """TODO: write.

        Args:
            entity (Entity): _description_
        """
        self.queue.remove(entity)
        self.queue.append(entity)
