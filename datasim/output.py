from abc import ABC
from os import mkdir, path
from pandas import DataFrame
import pickle
from typing import Dict, List, Literal, Tuple

import pandas as pd

from .logging import log
from .types import LogLevel


class Output(ABC):
    """Abstract class to show and store the state and results of the simulation."""

    dataframes: Dict[int, Dict[str, DataFrame]]
    dataframe_names: Dict[int, Dict[str, str]]

    def __init__(self):
        """Output class is created during runner initialization."""
        self.dataframes = {}
        self.dataframe_names = {}

    def _add_world(self, world: int):
        self.dataframes[world] = {}
        self.dataframe_names[world] = {}

    def aggregate_batches(self, worlds: List):
        from .world import World

        aggregated_data = []
        for world in worlds:
            if not isinstance(world, World):
                continue
            aggregated_data.append(world.get_aggregate_datapoints())

        result = pd.DataFrame(
            aggregated_data,
            columns=list(aggregated_data[0].keys()),
        )
        self.dataframes[-1] = {"Aggregated": result}
        self.dataframe_names[-1] = {"Aggregated": "Aggregated"}

    def export_pickle(self, world: int, source_id: str) -> Tuple[str, bytes]:
        """Export the data from a source to pickle format.

        Args:
            source_id (str): id of source to export.

        Returns:
            (str, bytes): filename with variation, pickle bytes.
        """
        return f"{self.dataframe_names[world][source_id]}.pickle", pickle.dumps(
            self.dataframes[world][source_id]
        )

    def export_csv(self, world: int, source_id: str) -> Tuple[str, str]:
        """Export the data from a source to CSV format.

        Args:
            source_id (str): id of source to export.

        Returns:
            (str, str): filename with variation, csv string.
        """
        return (
            f"{self.dataframe_names[world][source_id]}.csv",
            self.dataframes[world][source_id].to_csv(index=False),
        )

    def _clear(self, world: int):
        pass

    def _add_source(self, world: int, source_id: str, legend_x: str, secondary_y: bool):
        pass

    def _update_trace(self, source):
        pass

    def _update_source(self, source):
        pass

    def _select_world(self, worlds: List) -> List[int]:
        return [0]

    def _draw(self):
        pass

    def _save(self, directory: str, format: Literal["pickle", "csv"]):
        pass


class SimpleFileOutput(Output):
    """Simple/fastest output without dashboard: only stores data."""

    def _save(self, directory: str, format: Literal["pickle", "csv"]):
        directory = path.abspath(directory)
        log(
            f"Saving {sum([len(self.dataframes[world]) for world in self.dataframes])}x output to {directory}",
            LogLevel.debug,
        )

        if not path.exists(directory):
            mkdir(directory)

        match format:
            case "pickle":
                self.export_all_pickle(directory)
            case "csv":
                self.export_all_csv(directory)

    def _select_world(self, worlds) -> List[int]:
        return list(range(len(worlds)))

    def export_all_pickle(self, directory: str):
        """Export all sources as .pickle files.

        Args:
            directory (str): path of a directory to store files in.
        """
        for world in self.dataframes:
            for source_id in self.dataframes[world]:
                filename, content = self.export_pickle(world, source_id)
                log(f"...{filename} ({len(content)} bytes)")
                with open(path.join(directory, filename), "wb") as file:
                    file.write(content)

    def export_all_csv(self, directory: str):
        """Export all sources as .csv files.

        Args:
            directory (str): path of a directory to store files in.
        """
        for world in self.dataframes:
            for source_id in self.dataframes[world]:
                filename, content = self.export_csv(world, source_id)
                log(f"...{filename} ({len(content)} bytes)")
                with open(path.join(directory, filename), "w") as file:
                    file.write(content)
