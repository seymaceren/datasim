from codecs import open
from datetime import datetime
from inspect import getfile
from itertools import product
from os import path
from threading import Thread
from time import sleep
from sys import stdout
from typing import Dict, Final, List, Optional
from yaml import full_load

from .output import Output, SimpleFileOutput
from .logging import log, LogLevel
from .types import Value
from .world import World


class Runner:
    """Main simulation runner for DataSim.

    This class creates the World objects for any batches of runs defined in the definition yaml of the target class.
    """

    complete_log: str = ""

    output: Output
    single_world: bool
    worlds: List[World]
    title: Final[str]
    headless: bool
    started: bool
    _active: bool
    update_time: float | None
    tpu: float = 0.0
    end_tick: int = 0
    restart: bool = False
    realtime: bool = False
    stop_server: bool = False
    control_thread: Thread
    auto_output_path: str | None
    auto_output_csv: bool
    date: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __init__(
        self,
        world_class_object,
        headless: bool = False,
        auto_output_path: str | None = None,
        auto_output_csv: bool = False,
    ):
        """Create a simulation Runner.

        Args:
            world_class_object (type or object): Type, class or object by which
                the world's type is determined
            headless (bool, optional): Run without dashboard. Defaults to False.

        Raises:
            ValueError: If the definition file contains an invalid grid definition.
        """

        definition: Optional[Dict[str, Dict]] = None

        type_file = getfile(world_class_object)
        head, tail = path.split(type_file)
        type_filename = tail or path.basename(head)
        type_filename = type_filename[: type_filename.rfind(".")]

        definition_file = path.join(
            path.abspath(path.dirname(type_file)), f"{type_filename}.yaml"
        )

        if definition_file and path.exists(definition_file):
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
                                    range(
                                        round(start),
                                        round(end) + round(step),
                                        round(step),
                                    )
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

        self.headless = headless
        if headless:
            self.output = SimpleFileOutput()
        else:
            from .streamlit_dashboard import StreamlitDashboard

            self.output = StreamlitDashboard()

        self.worlds = []
        self.single_world = len(batches) == 0

        for batch in batches:
            world: World = world_class_object(
                self,
                headless=headless,
                definition=definition,
                variation=Runner._variation_string(batch),
                variation_dict=batch,
            )
            for selector, value in batch.items():
                world._set_variation(selector, value)
            self.worlds.append(world)

        if self.single_world:
            self.worlds.append(
                world_class_object(self, headless=headless, definition=definition)
            )

        for world in self.worlds:
            self.output._add_world(world.index)

        self.title = self.worlds[0].title
        if len(self.worlds) > 1:
            self.title = f"{len(self.worlds)}x {self.title}"
        self.started = False

        self.update_time = 1.0

        self.auto_output_path = auto_output_path
        self.auto_output_csv = auto_output_csv

        stdout.reconfigure(encoding="utf-8")  # type: ignore
        log(
            open("header", "r", "utf-8").read(),
            LogLevel.error,
            include_timestamp=False,
        )  # Draw terminal logo

        if self.single_world:
            log("No batches defined, created a single world.", LogLevel.verbose)
        else:
            log(f"Created {len(batches)} worlds.", LogLevel.verbose)

        Runner.no_world = World(self, "NO_INDEX")

    @staticmethod
    def _variation_string(variations: Dict[str, Value]):
        return ", ".join([f"{k}={v}" for k, v in variations.items()])

    def simulate(
        self,
        tpu: float = 0.0,
        end_tick: int = 0,
        restart: bool = False,
        realtime: bool = False,
        stop_server: bool = False,
    ):
        """Run the simulation for all worlds.

        Args:
            tps (float, optional): Ticks per time unit (only in simulation time, unless `realtime=True`).
                Defaults to :data:`simulation.tpu`.
            end_tick (int, optional): Tick count to end, unless set to 0. Defaults to 0.
            restart (bool, optional): Set to `True` if this is a restart. Defaults to False.
            realtime (bool, optional): Run the simulation in real time. Defaults to False.
            stop_server (bool, optional): Terminate streamlit python process after the simulation is done.
                For now, use only for faster debugging workflow. Defaults to False.

        Returns:
            `True` if the simulation is still running.
        """
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
            self.control_thread = Thread(target=self._check_active)
            self.control_thread.start()

        self.control_thread.join()
        self._finish()

    def _check_active(self):
        while True:
            sleep(1.0)
            if not self.active:
                break

    def _finish(self):
        self.wait()

        log(
            f"\n▟{"▀"*(4+len(self.title))}▜▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▙\n"
            + f"█  {self.title}  ▐  End of simulation  █\n"
            + f"▜{"▄"*(4+len(self.title))}▟▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▛\n",
            LogLevel.debug,
        )

        if self._gather(True):
            self.output.aggregate_batches(self.worlds)

        if self.auto_output_path:
            self.output._save(
                self.auto_output_path, "csv" if self.auto_output_csv else "pickle"
            )

        self._draw()

    @property
    def active(self):
        """Check if the simulation is still actively running."""
        if self._active:
            any_active = False

            for world in self.worlds:
                if isinstance(world, World):
                    any_active |= world.active and world._simulate(
                        self.tpu,
                        self.end_tick,
                        self.restart,
                        self.realtime,
                        self.stop_server,
                    )

            self._active = any_active

        return self._active

    def stop(self):
        """Stop the simulation and wait for it to end."""
        for world in self.worlds:
            world._stop()

    def wait(self):
        """Wait for the simulation of all worlds to end."""
        for world in self.worlds:
            world._wait()

    def _gather(self, calculate_all: bool = False) -> bool:
        any_changed = False

        if calculate_all:
            worlds = list(range(len(self.worlds)))
        else:
            worlds = self.output._select_world(self.worlds)

        if self.output:
            for world in worlds:
                self.output._clear(self.worlds[world].index)

        for world in worlds:
            any_changed = self.worlds[world]._updateData() or any_changed

        return any_changed

    def _draw(self):
        self.output._select_world(self.worlds)
        if self.output:
            self.output._draw()
