from codecs import open
from inspect import getfile
from itertools import product
from os import path
import streamlit as st
from sys import stdout
from typing import Dict, Final, List, Optional
from yaml import full_load

from .dashboard import Dashboard
from .logging import log, LogLevel
from .types import Value
from .world import World


class Runner:
    dashboard: Optional[Dashboard] = None
    worlds: List[World]
    title: Final[str]
    started: bool
    _active: bool
    update_time: float | None
    tpu: float = 0.0
    end_tick: int = 0
    restart: bool = False
    realtime: bool = False
    stop_server: bool = False

    def __init__(self, world_class_object, headless: bool = False):
        definition: Optional[Dict[str, Dict]] = None

        type_file = getfile(world_class_object)
        head, tail = path.split(type_file)
        type_filename = tail or path.basename(head)
        type_filename = type_filename[: type_filename.rfind(".")]

        definition_file = path.join(
            path.abspath(path.dirname(type_file)), f"{type_filename}.yaml"
        )

        if definition_file:
            definition = full_load(open(definition_file))

        batches: List[Dict[str, Value]] = []

        if definition and "batches" in definition:
            for batch in definition["batches"]:
                batch_type: str = list(batch.keys())[0]
                batch_params: List[Dict] = list(batch.values())[0]

                match batch_type:
                    case "single":
                        for configuration in batch_params:
                            batches.append(configuration)
                    case "grid":
                        keys: List[str] = []
                        combinable: List[List] = []
                        for key, variations in batch_params[0].items():
                            keys.append(key)

                            if isinstance(variations, dict):
                                (start, end) = tuple(variations["range"])
                                step = variations["step"]
                                variations = list(
                                    range(int(start), int(end), int(step))
                                )

                            if not isinstance(variations, list):
                                raise ValueError(
                                    f"Invalid range for grid batch: {variations}"
                                )

                            combinable.append(variations)

                        for combination in product(*combinable):
                            configuration = {}
                            for i, option in enumerate(combination):
                                configuration[keys[i]] = option
                            batches.append(configuration)

        self._active = True

        if not headless:
            self.dashboard = Dashboard()

        self.worlds = []

        for batch in batches:
            world: World = world_class_object(
                self, headless, definition, variation=Runner.variation_string(batch)
            )
            for selector, value in batch.items():
                world.set_variation(selector, value)
            self.worlds.append(world)

        if len(batches) == 0:
            self.worlds.append(world_class_object(self, headless, definition))

        self.title = self.worlds[0].title
        if len(self.worlds) > 1:
            self.title = f"{len(self.worlds)}x {self.title}"
        self.started = False

        self.update_time = 1.0

        stdout.reconfigure(encoding="utf-8")  # type: ignore
        log(
            open("header", "r", "utf-8").read(),
            LogLevel.error,
            include_timestamp=False,
        )  # Draw terminal logo

    @staticmethod
    def variation_string(variations: Dict[str, Value]):
        return ", ".join([f"{k}={v}" for k, v in variations.items()])

    def simulate(
        self,
        tpu: float = 0.0,
        end_tick: int = 0,
        restart: bool = False,
        realtime: bool = False,
        stop_server: bool = False,
    ) -> bool:
        if not self.started:
            log(
                f"\n▟{"▀"*(4+len(self.title))}▜▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▙\n"
                + f"█  {self.title}  ▐  Starting simulation  █\n"
                + f"▜{"▄"*(4+len(self.title))}▟▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▛\n",
                LogLevel.debug,
            )
            self.tpu = tpu
            self.end_tick = end_tick
            self.restart = restart
            self.realtime = realtime
            self.stop_server = stop_server
            self.started = True

        return self.active

    @property
    def active(self):
        if self._active:
            any_active = False

            for world in self.worlds:
                if isinstance(world, World):
                    any_active |= world.active and world.simulate(
                        self.tpu,
                        self.end_tick,
                        self.restart,
                        self.realtime,
                        self.stop_server,
                    )

            self._active = any_active

        return self._active

    def wait(self):
        for world in self.worlds:
            world.wait()

        log(
            f"\n▟{"▀"*(4+len(self.title))}▜▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▙\n"
            + f"█  {self.title}  ▐  End of simulation  █\n"
            + f"▜{"▄"*(4+len(self.title))}▟▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▛\n",
            LogLevel.debug,
        )

    def _draw(self):
        world = 0
        if len(self.worlds) > 1:
            world = st.selectbox(
                "Details for run:",
                range(len(self.worlds)),
                format_func=lambda i: self.worlds[i].variation,
            )

        if self.dashboard:
            self.dashboard.plots.clear()

        self.worlds[world]._updateData()

        if self.dashboard:
            self.dashboard._draw()
