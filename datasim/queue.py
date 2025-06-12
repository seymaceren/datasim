from typing import Dict, Final, Generic, List, Tuple, TypeVar

from .entity import Entity
from .logging import log
from .types import LogLevel, Number, PlotOptions, PlotType

EntityType = TypeVar("EntityType", bound=Entity)


class Queue(Generic[EntityType]):
    """A queue for entities to wait for resource availability."""

    world: Final
    id: Final[str]
    queue: Final[List[Tuple[EntityType, Number]]]
    capacity: int
    changed_tick: int
    _outputs: Final

    def __init__(
        self,
        world,
        id: str,
        capacity: int = 0,
        gather: bool = True,
        data_id: str = "",
        sample_frequency: int = 1,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a waiting queue for entities.

        Args:
            world: The world to add this Queue to.
            id (str): Identifier / name of the queue.
            capacity (int): Maximum queue length. Defaults to 0 for no maximum.
            gather (`PlotType` or `False`, optional): Whether to automatically gather data for the output
                for this resource, and which type of plot if so. Defaults to `PlotType.none` to only save.
            data_id (str, optional): id for the data source if `gather` is True. Defaults to empty string
                which sets `data_id` to the value of this Queue's `id`.
            sample_frequency (int, optional): Whether to add a data point every `frequency` ticks.
                If set to `0`, adds a data point only when the quantity changes. Defaults to `1`.
            plot_options (Optional[PlotOptions], optional): Options for a plot. Defaults to default PlotOptions.
        """
        self.id = id
        self.world = world
        self.capacity = capacity
        self.queue = []
        self.changed_tick = 0

        self.world.add(self)

        from .dataset import QueueData

        self._outputs: List[QueueData] = []

        if gather:
            self.add_output(data_id, sample_frequency, plot_options)

    @staticmethod
    def _from_yaml(world, params: Dict) -> "Queue":
        id = list(params.keys())
        if len(id) > 1:
            raise ValueError(f"Unable to parse yaml: Multiple keys found in {params}")

        id = id[0]
        params = params[id]

        return Queue(
            world,
            id,
            params.get("capacity", 0),
            params.get("gather", True),
            params.get("data_id", ""),
            params.get("sample_frequency", 1),
            PlotOptions._from_yaml(params.get("plot_options", {})),
        )

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

    def add_output(
        self,
        data_id: str = "",
        frequency: int = 1,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create an output source for this Queue. Also automatically used when `gather` is True at creation.

        Args:
            data_id (str, optional): Unique identifier of the source. Defaults to empty string which sets `data_id`
                to the value of this Queue's `id`.
            frequency (int, optional): Saves every x ticks or only on change if set to 0. Defaults to 0.
            plot_options (Optional[PlotOptions], optional): Options for a plot. Defaults to default PlotOptions.
        """
        from .dataset import QueueData

        if (
            plot_options.aggregate_only
            and plot_options.plot_type != PlotType.export_only
        ):
            plot_options.plot_type = PlotType.none
        elif plot_options.plot_type == PlotType.none:
            plot_options.plot_type = PlotType.line
        if data_id == "":
            data_id = self.id

        data = QueueData(self.world, self.id, frequency, plot_options)
        self._outputs.append(data)
        self.world.add_data(data_id, data)

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
        for output in self._outputs:
            if output.options.legend_y == "":
                output.options.legend_y = str(entity.plural).lower()

        if not self.full:
            log(
                f"{entity} joining {self}",
                LogLevel.verbose,
                45,
                world=self.world,
            )

            self.queue.insert(0, (entity, amount))
            self.changed_tick = self.world.ticks

            return True

        return False

    def dequeue(self) -> EntityType | Tuple[EntityType, Number] | None:
        """Remove the entity from the front of the queue and returns it.

        Returns:
            Entity: The entity that was at the front of this queue.
        """
        if len(self.queue) == 0:
            return None

        (e, a) = self.queue.pop()
        self.changed_tick = self.world.ticks

        log(
            f"{e} left {self}",
            LogLevel.verbose,
            45,
        )

        if a is None:
            return e
        return (e, a)

    def peek(self) -> EntityType | None:
        """Return the entity at the front of the queue without removing it.

        Returns:
            Entity: The entity at the front of this queue.
        """
        if len(self.queue) == 0:
            return None

        (e, a) = self.queue[-1]
        return e

    def peek_with_amount(self) -> Tuple[EntityType, Number] | None:
        """Return the entity at the front of the queue without removing it.

        Returns:
            Entity: The entity at the front of this queue.
        """
        if len(self.queue) == 0:
            return None

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
            self.changed_tick = self.world.ticks
            return True

        return False

    def __str__(self) -> str:
        """Get a string representation of this queue."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Get a string representation of this queue."""
        return f"Queue {self.id} length {len(self.queue)}" + (
            "" if self.capacity == 0 else "/{self.capacity}"
        )
