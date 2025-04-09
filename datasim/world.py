from abc import ABC
from psutil import Process
from os import getpid
from sys import stdout
from threading import Thread
from time import sleep
from typing import Final, Optional, Self

from . import simtime
from .entity import Entity


class World(ABC):
    """Abstract base class for the simulation world.

    A simulation should run in a subclass of World.
    """

    current: Optional[Self] = None
    title: Final[str]
    entities: Final[list[Entity]]

    def __init__(self, title: str = "Unnamed Simulation", tps: float = 10.0):
        """Create the simulation world.

        Args:
            title (str, optional): Descriptive name of the simulation (world). Defaults to "Unnamed Simulation".
            tps (float, optional): Ticks per second (only in simulation time,
                unless running `simulate` with `realtime=True`). Defaults to 10.0.
        """
        if World.current:
            print("(Warning: Not launching another instance)")
            return
        World.current = self
        self.title: str = title
        self.entities: list[Entity] = []
        from datasim import Dashboard
        self.dashboard: Optional[Dashboard] = None
        self.ended: bool = False
        simtime.tps = tps

        stdout.reconfigure(encoding='utf-8')  # type: ignore
        print("\x1B[38;5;154m▝█▀▜\x1B[38;5;184m▖   \x1B[38;5;178m   ▗\x1B[38;5;214m▖   " +
              "\x1B[38;5;208m   ▗\x1B[38;5;209m▛▀▀▖\x1B[38;5;204m ▄\n" +
              "\x1B[38;5;154m █ \x1B[38;5;184m █ ▟\x1B[38;5;178m▀▜▖▗\x1B[38;5;214m▟▙▄ " +
              "\x1B[38;5;208m▟▀▜▖\x1B[38;5;209m▝▙▄▄\x1B[38;5;204m ▗▄ \x1B[38;5;199m▜▛▚▛\x1B[38;5;164m▜▖\n" +
              "\x1B[38;5;154m █\x1B[38;5;184m  █ \x1B[38;5;178m█ ▐▌\x1B[38;5;214m ▐▌ " +
              "\x1B[38;5;208m █ ▐\x1B[38;5;209m▌   \x1B[38;5;204m▐▌ █\x1B[38;5;199m ▐▌▐\x1B[38;5;164m▌▐▌\n" +
              "\x1B[38;5;154m▗\x1B[38;5;184m█▄▟▘\x1B[38;5;178m ▜▄▞\x1B[38;5;214m▙ ▝▙" +
              "\x1B[38;5;208m▞ ▜▄\x1B[38;5;209m▞▙▝▄\x1B[38;5;204m▄▟▘▗\x1B[38;5;199m█▖▐▌\x1B[38;5;164m▐▌▐▌" +
              "\x1B[0m\n")
        print(f"World '{self.title}' created.\n\n")

        if not self.dashboard:
            self.dashboard = Dashboard()

    def _draw(self):
        if self.dashboard:
            self.dashboard._draw()

    def add(self, entity: Entity):
        """Add an entity to this `World`.

        Args:
            entity (Entity): The entity to add.
        """
        self.entities.append(entity)

    def remove(self, entity: Entity) -> bool:
        """Remove an entity from this `World`.

        Args:
            entity (Entity): The entity to remove.

        Returns:
            bool: `True` if the entity was succesfully removed.
        """
        try:
            self.entities.remove(entity)
        except ValueError:
            return False
        return True

    def simulate(self, tps: float = simtime.tps, end_tick: int = 0,
                 restart: bool = False, realtime: bool = False, stop_server: bool = False):
        """Run the simulation.

        Args:
            tps (float, optional): Ticks per second (only in simulation time, unless `realtime=True`).
                Defaults to `simtime.tps`.
            end_tick (int, optional): Tick count to end, unless set to 0. Defaults to 0.
            restart (bool, optional): Set to `True` if this is a restart. Defaults to False.
            realtime (bool, optional): Run the simulation in real seconds. Defaults to False.
            stop_server (bool, optional): Terminate streamlit python process after the simulation is done.
                For now, use only for faster debugging workflow. Defaults to False.
        """
        if self.ended and not restart:
            return

        simtime.tps = tps
        self.tick_time = 1.0 / tps
        self.end_tick = end_tick
        self.realtime = realtime
        self.stop_server = stop_server
        self.sim_thread = Thread(target=self._simulation_thread)
        self.sim_thread.start()

    def update_plots(self):
        """Update data for plots during of right after the simulation run.

        Raises:
            NotImplementedError: This function should be implemented by any subclasses.
        """
        raise NotImplementedError

    def pre_entities_tick(self):
        """Implement this function to run any code at the start of each tick, \
            before all entities are updated."""
        pass

    def post_entities_tick(self):
        """Implement this function to run any code at the end of each tick, \
            after all entities have been updated."""
        pass

    def _simulation_thread(self):
        print(f"\n{"#"*(36+len(self.title))}\n" +
              f"###  {self.title}  ###  Starting simulation  ###\n" +
              f"{"#"*(36+len(self.title))}\n")

        if self.end_tick > 0:
            print(f"{self.title}: Run for {self.end_tick / simtime.tps} seconds" +
                  " ({self.end_tick} ticks at {simtime.tps} ticks/second)...")

        self.last_update = 0

        while simtime.ticks < self.end_tick:
            self.pre_entities_tick()
            for entity in self.entities:
                entity._tick()
            self.post_entities_tick()
            simtime.ticks += 1
            if self.realtime:
                sleep(self.tick_time)

        self.ended = True
        print(f"\n{"#"*(34+len(self.title))}\n" +
              f"###  {self.title}  ###  End of simulation  ###\n" +
              f"{"#"*(34+len(self.title))}\n")

        simtime.update_time = 0.0

        if self.stop_server:
            sleep(3)
            pid = getpid()
            p = Process(pid)
            p.terminate()
