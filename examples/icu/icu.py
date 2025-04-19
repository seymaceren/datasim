import csv
from typing import List, Self, Tuple

from datasim import (
    Plot,
    PlotType,
    Queue,
    QueuePlotData,
    Resource,
    ResourcePlotData,
    UseResult,
    World,
    XYPlotData,
)
from .patient import Patient


class ICU(World):
    overview: XYPlotData
    patients: List[Tuple[float, Patient]]
    beds: Resource
    patients_waiting: Queue[Patient]
    icu: Self

    def __init__(self, headless: bool = False):
        super().__init__("ICU world", headless=headless)

        ICU.icu = self

        self.beds = Resource(self, "beds", "beds", 4)
        self.add(self.beds)

        self.add_plot(
            Plot(
                "beds",
                ResourcePlotData(
                    "beds", 1, PlotType.bar, "Beds in use", legend_y="beds"
                ),
            )
        )

        self.patients = []
        for row in csv.reader(open("examples/icu/simulatiedata.csv")):
            if not (row[0]).isnumeric():
                continue
            patient = Patient(row[0], row[3], float(row[2]))
            self.patients.append((float(row[1]), patient))
            self.add(patient)

        self.patients_waiting = Queue[Patient]("patients_waiting")
        self.add(self.patients_waiting)

        self.add_plot(
            Plot(
                "waiting",
                QueuePlotData("patients_waiting", 1, PlotType.bar, "Patients waiting"),
            )
        )

    def pre_entities_tick(self):
        while len(self.patients) > 0 and self.patients[0][0] <= World.seconds():
            print(
                f"Patient joining queue of {len(self.patients_waiting)} at {self.patients[0][0]}"
            )
            self.patients_waiting.enqueue(self.patients[0][1])
            self.patients.pop(0)

        # We don't want our patients to look for beds themselves but in order of arrival.
        while not self.beds.occupied and not len(self.patients_waiting) == 0:
            next = self.patients_waiting.peek()
            if not next.alive:
                self.patients_waiting.dequeue()
            else:
                result = self.beds.try_use(next)
                print(
                    f"Patient {next.name} trying to use a bed at {World.seconds()}: {result}"
                )
                if result == UseResult.success:
                    self.patients_waiting.dequeue()
