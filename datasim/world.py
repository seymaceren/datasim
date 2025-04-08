from abc import ABC
from psutil import Process
from os import getpid
from sys import stdout
from threading import Thread
from time import sleep
from typing import Final, Optional, Self

from datasim import simtime
from datasim.entity import Entity


class World(ABC):
    current: Optional[Self] = None
    title: Final[str]
    entities: Final[list[Entity]]

    def __init__(self, title: str = "Unnamed Simulation", tps: float = 10.0):
        if World.current:
            print("(Warning: Not launching another instance)")
            return
        World.current = self
        self.title: str = title
        self.entities: list[Entity] = []
        from datasim.dashboard import Dashboard
        self.dashboard: Optional[Dashboard] = None
        self.ended: bool = False
        simtime.tps = tps

        stdout.reconfigure(encoding='utf-8') # type: ignore
        print("\x1B[38;5;154m▝█▀▜\x1B[38;5;184m▖   \x1B[38;5;178m   ▗\x1B[38;5;214m▖   \x1B[38;5;208m   ▗\x1B[38;5;209m▛▀▀▖\x1B[38;5;204m ▄\n\x1B[38;5;154m █ \x1B[38;5;184m █ ▟\x1B[38;5;178m▀▜▖▗\x1B[38;5;214m▟▙▄ \x1B[38;5;208m▟▀▜▖\x1B[38;5;209m▝▙▄▄\x1B[38;5;204m ▗▄ \x1B[38;5;199m▜▛▚▛\x1B[38;5;164m▜▖\n\x1B[38;5;154m █\x1B[38;5;184m  █ \x1B[38;5;178m█ ▐▌\x1B[38;5;214m ▐▌ \x1B[38;5;208m █ ▐\x1B[38;5;209m▌   \x1B[38;5;204m▐▌ █\x1B[38;5;199m ▐▌▐\x1B[38;5;164m▌▐▌\n\x1B[38;5;154m▗\x1B[38;5;184m█▄▟▘\x1B[38;5;178m ▜▄▞\x1B[38;5;214m▙ ▝▙\x1B[38;5;208m▞ ▜▄\x1B[38;5;209m▞▙▝▄\x1B[38;5;204m▄▟▘▗\x1B[38;5;199m█▖▐▌\x1B[38;5;164m▐▌▐▌\x1B[0m\n")
        print(f"World '{self.title}' created.\n\n")

        if not self.dashboard:
            self.dashboard = Dashboard()

    def draw(self):
        if self.dashboard:
            self.dashboard.draw()

    def add(self, entity: Entity):
        self.entities.append(entity)

    def remove(self, entity: Entity) -> bool:
        try:
            self.entities.remove(entity)
        except:
            return False
        return True

    def simulate(self, tps: float = simtime.tps, end_tick: int = 0, restart: bool = False, realtime: bool = False, stop_server: bool = False):
        if self.ended and not restart:
            return

        simtime.tps = tps
        self.tick_time = 1.0 / tps
        self.end_tick = end_tick
        self.realtime = realtime
        self.stop_server = stop_server
        self.sim_thread = Thread(target=self.simulation_thread)
        self.sim_thread.start()

    def update_plots(self):
        raise NotImplementedError

    def pre_entities_tick(self):
        pass

    def post_entities_tick(self):
        pass

    def simulation_thread(self):
        print(f"\n{"#"*(36+len(self.title))}\n###  {self.title}  ###  Starting simulation  ###\n{"#"*(36+len(self.title))}\n")

        if self.end_tick > 0:
            print(f"{self.title}: Run for {self.end_tick / simtime.tps} seconds ({self.end_tick} ticks at {simtime.tps} ticks/second)...")

        self.last_update = 0

        while simtime.ticks < self.end_tick:
            self.pre_entities_tick()
            for entity in self.entities:
                entity.tick()
            self.post_entities_tick()
            simtime.ticks += 1
            if self.realtime:
                sleep(self.tick_time)

        self.ended = True
        print(f"\n{"#"*(34+len(self.title))}\n###  {self.title}  ###  End of simulation  ###\n{"#"*(34+len(self.title))}\n")

        simtime.update_time = 0.0

        if self.stop_server:
            sleep(3)
            # Terminate streamlit python process
            # use only for faster debugging workflow
            pid = getpid()
            p = Process(pid)
            p.terminate()
