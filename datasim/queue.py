from typing import Final, List
from .entity import Entity


class Queue:
    """A queue for entities to wait for resource availability."""
    id: Final[str]
    queue: Final[List[Entity]]

    def __init__(self, id: str):
        self.id = id
        self.queue = []

    def enqueue(self, entity: Entity):
        self.queue.insert(0, entity)

    def dequeue(self) -> Entity:
        return self.queue.pop()

    def prioritize(self, entity: Entity):
        self.queue.remove(entity)
        self.queue.append(entity)
