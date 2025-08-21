from abc import ABC
from os import mkdir, path
from re import split
import shutil
from pandas import DataFrame
import pickle
from typing import Any, Dict, List, Literal, Optional, Tuple

import pandas as pd

from .logging import log
from .types import LogLevel, PlotOptions, PlotType


class Output(ABC):
    """Abstract class to show and store the state and results of the simulation."""

    dataframes: Dict[int, Dict[str, DataFrame]]
    dataframe_names: Dict[int, Dict[str, str]]
    sources: Dict[int, Dict[str, Dict[int, Any]]]
    runner: Any
    split_worlds: bool

    def __init__(self, runner: Any, split_worlds: bool):
        """Output class is created during runner initialization."""
        self.dataframes = {}
        self.dataframe_names = {}
        self.sources = {}
        self.runner = runner
        self.split_worlds = split_worlds

    def _add_world(self, world: int):
        self.dataframes[world] = {}
        self.sources[world] = {}
        self.dataframe_names[world] = {}

    @staticmethod
    def _aggregated_title(set_name):
        return f"{set_name} - Aggregated"

    def _aggregate_batches(self, worlds: List):
        from .world import World

        aggregated_data = []
        for world in worlds:
            if not isinstance(world, World) or world.index < 0:
                continue
            aggregated_data.append(world.get_aggregate_datapoints())

        set_data = {}
        for set_name in aggregated_data[0]:
            set_data[set_name] = []
            for world_data in aggregated_data:
                set_data[set_name].append(world_data[set_name])

        from .dataset import DataFrameData, Dataset

        for set_name, data in set_data.items():
            if -1 not in self.dataframes:
                self._add_world(-1)

            self._clear(-1)

            result = pd.DataFrame(
                data,
                columns=list(data[0].keys()),
            )

            key = Output._aggregated_title(set_name)
            self.dataframes[-1][key] = result
            self.dataframe_names[-1][key] = key

            from .runner import Runner

            source = DataFrameData(
                Runner.no_world,
                result,
                PlotOptions(plot_type=PlotType.export_only, name=key),
            )
            aggregate_data: Dataset = Dataset(Runner.no_world, key, source)
            aggregate_data._update()

    def _concat_worlds(self, source_id: str) -> Tuple[str, DataFrame]:
        frames = []
        name = list(self.dataframe_names.values())[0][source_id]
        for id, frame in self.dataframes.items():
            if len(frame) == 0:
                continue
            if len(self.runner.worlds) == 1:
                return name, frame[source_id]

            with_variation = frame[source_id].copy()
            with_variation.insert(0, "world_id", id)
            for variation, value in self.runner.worlds[id].variation_dict.items():
                with_variation.insert(0, variation, value)

            frames.append(with_variation)
        return name, pd.concat(frames)

    def export_pickle(self, world: int | None, source_id: str) -> Tuple[str, bytes]:
        """Export the data from a source to pickle format.

        Args:
            world (int or None): world ID of source, or None for a single world,
                                 which will add world ID as a column if batched
            source_id (str): ID of source to export.

        Returns:
            (str, bytes): filename, pickle bytes.
        """
        if world is None:
            name, frames = self._concat_worlds(source_id)
            return f"{name}.pickle", pickle.dumps(frames)
        else:
            return (
                f"{self.dataframe_names[world][source_id]}.pickle",
                pickle.dumps(self.dataframes[world][source_id]),
            )

    def export_csv(self, world: int | None, source_id: str) -> Tuple[str, str]:
        """Export the data from a source to CSV format.

        Args:
            world (int or None): world ID of source, or None for a single world,
                                 which will add world ID as a column if batched
            source_id (str): ID of source to export.

        Returns:
            (str, str): filename, csv string.
        """
        if world is None:
            name, frames = self._concat_worlds(source_id)
            return f"{name}.csv", frames.to_csv(index=False)
        else:
            return (
                f"{self.dataframe_names[world][source_id]}.csv",
                self.dataframes[world][source_id].to_csv(index=False),
            )

    def _clear(self, world: int):
        pass

    def _add_source(
        self, world: int, source_id: str, legend_x: Optional[str], secondary_y: bool
    ):
        pass

    def _update_trace(self, source):
        pass

    def _update_source(self, source):
        pass

    def _select_world(self, worlds: List) -> List[int]:
        return [0]

    def _draw(self):
        pass

    def _save(
        self,
        directory: str,
        clear_directory: bool,
        split_worlds: bool,
        format: Literal["pickle", "csv"],
    ):
        pass


class SimpleFileOutput(Output):
    """Simple/fastest output without dashboard: only stores data."""

    def _save(
        self,
        directory: str,
        clear_directory: bool,
        split_worlds: bool,
        format: Literal["pickle", "csv"],
    ):
        directory = path.abspath(directory)
        outputs = [len(self.dataframes[world]) for world in self.dataframes]
        num_outputs = sum(outputs) if split_worlds else max(outputs)
        log(
            f"Saving {num_outputs}x output to {directory}",
            LogLevel.debug,
        )

        if clear_directory and path.exists(directory):
            shutil.rmtree(directory)
        if not path.exists(directory):
            mkdir(directory)

        self.export_all(directory, split_worlds, format)

    def export_all(
        self, directory: str, split_worlds: bool, format: Literal["pickle", "csv"]
    ):
        """Export all sources as .pickle or .csv files.

        Args:
            directory (str): path of a directory to store files in.
        """
        if split_worlds:
            for world in self.dataframes:
                for source_id in self.dataframes[world]:
                    match format:
                        case "pickle":
                            filename, content = self.export_pickle(world, source_id)
                        case "csv":
                            filename, content = self.export_csv(world, source_id)
                    log(f"...{filename} ({len(content)} bytes)")
                    with open(
                        path.join(directory, filename),
                        "wb" if format == "pickle" else "w",
                    ) as file:
                        file.write(content)
        else:
            source_ids = set()
            for world in self.dataframes:
                for source_id in self.dataframes[world]:
                    source_ids.add(source_id)

            for source_id in source_ids:
                match format:
                    case "pickle":
                        filename, content = self.export_pickle(None, source_id)
                    case "csv":
                        filename, content = self.export_csv(None, source_id)
                log(f"...{filename} ({len(content)} bytes)")
                with open(
                    path.join(directory, filename), "wb" if format == "pickle" else "w"
                ) as file:
                    file.write(content)
