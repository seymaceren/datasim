from abc import ABC
from ordered_set import OrderedSet
from psutil import Process
from os import getpid
from threading import Thread
from time import sleep
from typing import Any, Dict, Final, Optional, Tuple

from .constant import Constant
from .entity import Entity
from .logging import log, LogLevel
from .plot import Plot, PlotData
from .quantity import Quantity
from .queue import Queue
from .resource import Resource
from .types import Value


class World(ABC):
    """Abstract base class for the simulation world.

    A simulation should run in a subclass of World.
    """

    update_time: float | None = 1.0

    runner: Final
    headless: bool
    title: Final[str]
    entities: Final[OrderedSet[Entity]]
    _entity_dict: Final[Dict[str, Entity]]
    plots: Final[Dict[str, Plot]]
    constants: Final[Dict[str, Any]]
    resources: Final[Dict[str, Resource]]
    queues: Final[Dict[str, Queue]]
    quantities: Final[Dict[str, Quantity]]
    stopped: bool = False

    """Number of ticks elapsed in the current simulation."""
    ticks: int = 0
    """Number of time units elapsed in the current simulation."""
    time: float = 0.0
    """The maximum number of ticks the simulation will run, if greater than 0."""
    end_tick: int = 0
    """Time unit."""
    time_unit: str = "seconds"
    """Number of ticks per simulated time unit (or also real time if running in realtime mode)."""
    tpu: float = 10.0
    """Number of simulated time units per tick (or also real time if running in realtime mode)."""
    tick_time: float = 0.1

    """Checks if the simulation is active."""
    active: bool = False

    def __init__(
        self,
        runner,
        title: str = "Unnamed Simulation",
        tpu: float = 10.0,
        time_unit: str = "seconds",
        headless: bool = False,
        definition: Optional[Dict] = None,
    ):
        """Create the simulation world.

        Args:
            title (str, optional): Descriptive name of the simulation (world). Defaults to "Unnamed Simulation".
            tps (float, optional): Ticks per second (only in simulation time,
                unless running :meth:`simulate()` with `realtime=True`). Defaults to 10.0.
        """
        self.runner = runner

        if self.active:
            log(
                "(Warning: Not launching another instance)",
                LogLevel.warning,
                include_timestamp=False,
            )
            return

        if definition:
            if "title" in definition:
                title = definition["title"]
            if "tpu" in definition:
                tpu = definition["tpu"]
            if "time_unit" in definition:
                time_unit = definition["time_unit"]
            if "headless" in definition:
                headless = definition["headless"]

        self.active = True
        self.title = title
        self.entities = OrderedSet[Entity]([])
        self._entity_dict = {}
        self.plots = {}
        self.constants = {}
        self.resources = {}
        self.queues = {}
        self.quantities = {}

        self.ended: bool = False
        self.tpu = tpu
        self.time_unit = time_unit

        self.headless = headless

        if definition:
            if "constants" in definition:
                for constant in definition["constants"]:
                    Constant.from_yaml(self, constant)

            if "resources" in definition:
                for resource in definition["resources"]:
                    Resource.from_yaml(self, resource)

            if "queues" in definition:
                for queue in definition["queues"]:
                    Queue.from_yaml(self, queue)

            if "quantities" in definition:
                for quantity in definition["quantities"]:
                    Quantity.from_yaml(self, quantity)

    def reset(self):
        """Reset the World so you can start a different simulation."""
        self.active = False

    def add(self, obj: Constant | Entity | Resource | Queue | Quantity):
        """Add an entity to this :class:`World`.

        Args:
            obj (:class:`Entity` | :class:`Resource` | (:class:`Queue`): The entity, resource or queue to add.
        """
        try:
            other = self.__getattribute__(obj.id)
        except Exception:
            other = None
        if other:
            if obj != other:
                raise ValueError(f"Another object with id {obj.id} already exists!")
            return
        self.__setattr__(obj.id, obj)

        if isinstance(obj, Constant):
            self.constants[obj.id] = obj
        elif isinstance(obj, Entity):
            self.entities.append(obj)
            self._entity_dict[obj.id] = obj
        elif isinstance(obj, Resource):
            self.resources[obj.id] = obj
        elif isinstance(obj, Queue):
            self.queues[obj.id] = obj
        elif isinstance(obj, Quantity):
            self.quantities[obj.id] = obj

    def remove(self, obj: Constant | Entity | Resource | Queue | Quantity) -> bool:
        """Remove an entity from this :class:`World`.

        Args:
            entity (:class:`Entity`): The entity to remove.

        Returns:
            bool: `True` if the entity was succesfully removed.
        """
        try:
            self.__delattr__(obj.id)

            if isinstance(obj, Constant):
                self.constants.pop(obj.id)
            elif isinstance(obj, Entity):
                self.entities.remove(obj)
            elif isinstance(obj, Resource):
                self.resources.pop(obj.id)
            elif isinstance(obj, Queue):
                self.queues.pop(obj.id)
            elif isinstance(obj, Quantity):
                self.quantities.pop(obj.id)
        except Exception:
            return False
        return True

    def set_variation(self, selector: str, value: Value):
        obj_path = selector.split(".")
        current = self
        for path_part in obj_path[:-1]:
            current = getattr(current, path_part)

        destination = getattr(current, obj_path[-1])

        if (
            destination is None
            or isinstance(destination, int)
            or isinstance(destination, float)
            or isinstance(destination, str)
        ):
            setattr(current, obj_path[-1], value)
        elif isinstance(destination, Constant):
            destination.value = value

    def constant(self, *keys) -> Value:
        """Get a constant from the current simulation."""
        key = ":".join(keys)
        constant = self.constants.get(
            key, KeyError(f"No constant with id '{key}' found!")
        )
        if isinstance(constant, KeyError):
            raise constant
        return constant

    def entity(self, key: str) -> Entity:
        """Get a Resource by id."""
        entity = self._entity_dict.get(key, None)
        if entity is not None:
            return entity
        raise KeyError(f"No entity with id '{key}' found!")

    def resource(self, key: str) -> Resource:
        """Get a Resource by id."""
        resource = self.resources.get(key, None)
        if resource is not None:
            return resource
        raise KeyError(f"No resource with id '{key}' found!")

    def queue(self, key: str) -> Queue:
        """Get a Queue by id."""
        queue = self.queues.get(key, None)
        if queue is not None:
            return queue
        raise KeyError(f"No queue with id '{key}' found!")

    def quantity(self, key: str) -> Quantity:
        """Get a Quantity by id."""
        quantity = self.quantities.get(key, None)
        if quantity is not None:
            return quantity
        raise KeyError(f"No queue with id '{key}' found!")

    def simulate(
        self,
        tpu: float = 0.0,
        end_tick: int = 0,
        restart: bool = False,
        realtime: bool = False,
        stop_server: bool = False,
    ) -> bool:
        """Run the simulation.

        Args:
            tps (float, optional): Ticks per time unit (only in simulation time, unless `realtime=True`).
                Defaults to :data:`simulation.tpu`.
            end_tick (int, optional): Tick count to end, unless set to 0. Defaults to 0.
            restart (bool, optional): Set to `True` if this is a restart. Defaults to False.
            realtime (bool, optional): Run the simulation in real time. Defaults to False.
            stop_server (bool, optional): Terminate streamlit python process after the simulation is done.
                For now, use only for faster debugging workflow. Defaults to False.
        """
        if self.ended and not restart:
            return False

        if tpu > 0.0:
            self.tpu = tpu
        self.ticks = 0
        self.time = 0.0
        self.tick_time = 1.0 / self.tpu
        self.end_tick = end_tick
        self.realtime = realtime
        self.stop_server = stop_server
        self.sim_thread = Thread(target=self._simulation_thread)
        self.sim_thread.start()
        return True

    def stop(self):
        """Stop the simulation and wait for it to end."""
        self.stopped = True
        self.wait()

    def wait(self):
        """Wait for the simulation to end."""
        if self.sim_thread:
            self.sim_thread.join()

    def before_entities_update(self):
        """Implement this function to run any code at the start of each tick, \
            before all entities are updated."""
        pass

    def after_entities_update(self):
        """Implement this function to run any code at the end of each tick, \
            after all entities have been updated."""
        pass

    def _simulation_thread(self):
        if self.end_tick > 0:
            log(
                f"{self.title}: Run for {self.end_tick / self.tpu} {self.time_unit}"
                + f" ({self.end_tick} ticks at {self.tpu} ticks/{self.time_unit})...",
                LogLevel.debug,
                include_timestamp=False,
            )
        else:
            log(
                f"{self.title}: Running indefinitely at {self.tpu} ticks/{self.time_unit})...",
                LogLevel.debug,
                include_timestamp=False,
            )

        if self.realtime and self.time_unit != "seconds":
            log(
                "Warning: Running realtime only works with seconds as time unit:\n"
                + f"Simulation timing will use seconds instead of {self.time_unit}!",
                LogLevel.warning,
                include_timestamp=False,
            )

        self.last_update = 0

        while (self.end_tick == 0 or self.ticks < self.end_tick) and not self.stopped:
            self.before_entities_update()

            for entity in self.entities:
                entity._tick()
            for quantity in self.quantities.values():
                quantity._tick()

            self.after_entities_update()

            for plot in self.plots.values():
                plot._tick()

            self.ticks += 1
            self.time = self.ticks / self.tpu
            if self.realtime:
                sleep(self.tick_time)

        self.ended = True
        log(
            f"\n▟{"▀"*(4+len(self.title))}▜▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▙\n"
            + f"█  {self.title}  ▐  End of simulation  █\n"
            + f"▜{"▄"*(4+len(self.title))}▟▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▛\n",
            LogLevel.debug,
            include_timestamp=False,
        )

        self.update_time = 0.0

        # TODO fix threading
        if self.stop_server:
            sleep(10)
            pid = getpid()
            p = Process(pid)
            p.terminate()

    def _draw(self):
        for plot in self.plots.values():
            plot._update()

    def add_plot(self, plot_id: str, data: PlotData) -> Tuple[Plot, int]:
        """Add a plot to the world: collects data, and plots if dashboard is present."""
        index = 0
        if plot_id not in self.plots:
            self.plots[plot_id] = Plot(self, plot_id, data)
        else:
            index = self.plots[plot_id].add_trace(data)

        return (self.plots[plot_id], index)
