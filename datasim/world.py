from abc import ABC
import codecs
from ordered_set import OrderedSet
from psutil import Process
from os import getpid
from sys import stdout
from threading import Thread
from time import sleep
from typing import Dict, Final, Optional, Self

from .entity import Entity
from .logging import log, LogLevel
from .plot import Plot
from .quantity import Quantity
from .queue import Queue
from .resource import Resource
import datasim.simulation as simulation


class World(ABC):
    """Abstract base class for the simulation world.

    A simulation should run in a subclass of World.
    """

    update_time: float | None = 1.0

    headless: bool
    current: Self
    title: Final[str]
    entities: Final[OrderedSet[Entity]]
    _entity_dict: Final[Dict[str, Entity]]
    plots: Final[Dict[str, Plot]]
    resources: Final[Dict[str, Resource]]
    queues: Final[Dict[str, Queue]]
    quantities: Final[Dict[str, Quantity]]
    stopped: bool = False

    def __init__(
        self,
        title: str = "Unnamed Simulation",
        tps: float = 10.0,
        headless: bool = False,
    ):
        """Create the simulation world.

        Args:
            title (str, optional): Descriptive name of the simulation (world). Defaults to "Unnamed Simulation".
            tps (float, optional): Ticks per second (only in simulation time,
                unless running :meth:`simulate()` with `realtime=True`). Defaults to 10.0.
        """
        if simulation.active:
            log("(Warning: Not launching another instance)", LogLevel.warning)
            return
        World.current = self
        simulation.active = True
        self.title = title
        self.entities = OrderedSet[Entity]([])
        self._entity_dict = {}
        self.plots = {}
        self.resources = {}
        self.queues = {}
        self.quantities = {}
        from datasim import Dashboard

        self.dashboard: Optional[Dashboard] = None
        self.ended: bool = False
        simulation.tps = tps

        stdout.reconfigure(encoding="utf-8")  # type: ignore
        log(
            codecs.open("header", "r", "utf-8").read(), LogLevel.error
        )  # Draw terminal logo

        self.headless = headless
        if not headless and not self.dashboard:
            self.dashboard = Dashboard()

    @staticmethod
    def reset():
        """Reset the World so you can start a different simulation."""
        simulation.active = False

    def add(self, obj: Entity | Resource | Queue | Quantity):
        """Add an entity to this :class:`World`.

        Args:
            obj (:class:`Entity` | :class:`Resource` | (:class:`Queue`): The entity, resource or queue to add.
        """
        if isinstance(obj, Entity):
            if obj.name in self._entity_dict:
                if obj != self._entity_dict[obj.name]:
                    raise ValueError(
                        f"Another entity with name {obj.name} already exists!"
                    )
                return
            self.entities.append(obj)
            self._entity_dict[obj.name] = obj
        elif isinstance(obj, Resource):
            self.resources[obj.id] = obj
        elif isinstance(obj, Queue):
            self.queues[obj.id] = obj
        elif isinstance(obj, Quantity):
            self.quantities[obj.id] = obj

    def remove(self, obj: Entity | Resource | Queue | Quantity) -> bool:
        """Remove an entity from this :class:`World`.

        Args:
            entity (:class:`Entity`): The entity to remove.

        Returns:
            bool: `True` if the entity was succesfully removed.
        """
        try:
            if isinstance(obj, Entity):
                self.entities.remove(obj)
            elif isinstance(obj, Resource):
                self.resources.pop(obj.id)
            elif isinstance(obj, Queue):
                self.queues.pop(obj.id)
            elif isinstance(obj, Quantity):
                self.quantities.pop(obj.id)
        except ValueError:
            return False
        return True

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
        tps: float = 0.0,
        end_tick: int = 0,
        restart: bool = False,
        realtime: bool = False,
        stop_server: bool = False,
    ) -> bool:
        """Run the simulation.

        Args:
            tps (float, optional): Ticks per second (only in simulation time, unless `realtime=True`).
                Defaults to :data:`simulation.tps`.
            end_tick (int, optional): Tick count to end, unless set to 0. Defaults to 0.
            restart (bool, optional): Set to `True` if this is a restart. Defaults to False.
            realtime (bool, optional): Run the simulation in real seconds. Defaults to False.
            stop_server (bool, optional): Terminate streamlit python process after the simulation is done.
                For now, use only for faster debugging workflow. Defaults to False.
        """
        if self.ended and not restart:
            return False

        if tps > 0.0:
            simulation.tps = tps
        simulation.ticks = 0
        simulation.time = 0.0
        simulation.tick_time = 1.0 / simulation.tps
        simulation.end_tick = end_tick
        self.realtime = realtime
        self.stop_server = stop_server
        self.sim_thread = Thread(target=self._simulation_thread)
        self.sim_thread.start()
        self.sim_thread.join()
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
        log(
            f"\n▟{"▀"*(4+len(self.title))}▜▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▙\n"
            + f"█  {self.title}  ▐  Starting simulation  █\n"
            + f"▜{"▄"*(4+len(self.title))}▟▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▛\n",
            LogLevel.debug,
        )
        if simulation.end_tick > 0:
            log(
                f"{self.title}: Run for {simulation.end_tick / simulation.tps} seconds"
                + f" ({simulation.end_tick} ticks at {simulation.tps} ticks/second)...",
                LogLevel.debug,
            )

        self.last_update = 0

        while (
            simulation.end_tick == 0 or simulation.ticks < simulation.end_tick
        ) and not self.stopped:

            self.before_entities_update()

            for entity in self.entities:
                entity._tick()
            for quantity in self.quantities.values():
                quantity._tick()

            self.after_entities_update()

            if self.dashboard:
                for plot in self.plots.values():
                    plot._tick()

            simulation.ticks += 1
            simulation.time = simulation.ticks / simulation.tps
            if self.realtime:
                sleep(simulation.tick_time)

        self.ended = True
        log(
            f"\n▟{"▀"*(4+len(self.title))}▜▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▙\n"
            + f"█  {self.title}  ▐  End of simulation  █\n"
            + f"▜{"▄"*(4+len(self.title))}▟▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▛\n",
            LogLevel.debug,
        )

        self.update_time = 0.0

        # TODO fix threading
        if self.stop_server:
            sleep(10)
            pid = getpid()
            p = Process(pid)
            p.terminate()

    def _draw(self):
        if self.dashboard:
            self.dashboard._draw()

    def _update_plots(self):
        for plot in self.plots.values():
            plot._update()

    def add_plot(self, plot: Plot):
        """Add a plot to the dashboard."""
        # if self.dashboard:
        self.plots[plot.id] = plot
