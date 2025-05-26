from typing import Dict, Final, Generic, List, Tuple, TypeVar

from .entity import Entity
from .logging import log
from .types import LogLevel, Number, PlotOptions

EntityType = TypeVar("EntityType", bound=Entity)


class Queue(Generic[EntityType]):
    """A queue for entities to wait for resource availability."""

    world: Final
    id: Final[str]
    queue: Final[List[Tuple[EntityType, Number]]]
    capacity: int
    changed_tick: int

    def __init__(
        self,
        world,
        id: str,
        capacity: int = 0,
        auto_plot: bool = True,
        plot_id: str = "",
        plot_frequency: int = 1,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a waiting queue for entities.

        Args:
            id (str): Identifier / name of the queue.
            capacity (int): Maximum queue length. Defaults to 0 for no maximum.
            auto_plot (`PlotType` or `False`, optional): Whether to automatically add a plot to the dashboard
                for this resource, and which type of plot if so. Defaults to `PlotType.line`.
            plot_frequency (int, optional): Whether to add a data point every `frequency` ticks.
                If set to `0`, adds a data point only when the quantity changes. Defaults to `1`.
            plot_title (Optional[str], optional): An optional plot title. Defaults to `None`.
        """
        self.id = id
        self.world = world
        self.capacity = capacity
        self.queue = []
        self.changed_tick = 0

        self.world.add(self)

        if auto_plot:
            self.make_plot(plot_id, plot_frequency, plot_options)

    @staticmethod
    def from_yaml(world, params: Dict) -> "Queue":
        id = list(params.keys())
        if len(id) > 1:
            raise ValueError(f"Unable to parse yaml: Multiple keys found in {params}")

        id = id[0]
        params = params[id]

        return Queue(
            world,
            id,
            params.get("capacity", 0),
            params.get("auto_plot", True),
            params.get("plot_id", ""),
            params.get("plot_frequency", 1),
            PlotOptions.from_yaml(params.get("plot_options", {})),
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

    def make_plot(
        self,
        plot_id: str = "",
        frequency: int = 1,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a plot for this Queue. Also automatically used when `auto_plot` is True at creation.

        Args:
            plot_type (PlotType, optional): The type of plot to add. Defaults to PlotType.line.
            frequency (int, optional): Plot every x ticks or only on change if set to 0. Defaults to 0.
            plot_title (Optional[str], optional): Optional title for the plot. Defaults to None.
        """
        from .plot import QueuePlotData

        if plot_id == "":
            plot_id = self.id

        self.plot = QueuePlotData(self.world, self.id, frequency, plot_options)
        self.world.add_plot(plot_id, self.plot)

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
        if hasattr(self, "plot") and self.plot.options.legend_y == "":
            self.plot.options.legend_y = str(entity.plural).lower()

        if not self.full:
            log(
                f"{entity} joining {self}",
                LogLevel.verbose,
                45,
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
