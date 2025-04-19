import csv
from typing import List, Tuple

from datasim import (
    Plot,
    PlotType,
    Queue,
    QueuePlotData,
    Resource,
    ResourcePlotData,
    World,
    XYPlotData,
)
from .patient import Patient


class ICU(World):
    overview: XYPlotData
    beds: Resource
    patients: List[Tuple[float, Patient]]
    patients_waiting: Queue[Patient]

    def __init__(self, headless: bool = False):
        super().__init__("ICU world", headless=headless)

        self.beds = Resource(self, "icu_beds", "beds", 4)

        self.add_plot(
            Plot(
                "beds",
                ResourcePlotData(
                    self.beds, 1, PlotType.bar, "Beds in use", legend_y="beds"
                ),
            )
        )

        self.patients = []
        for row in csv.reader(open("examples/icu/simulatiedata.csv")):
            if not (row[0]).isnumeric():
                continue
            self.patients.append(
                (float(row[1]), Patient(row[0], row[3], float(row[2])))
            )
        self.patients_waiting = Queue[Patient]("patients")

        self.add_plot(
            Plot(
                "waiting",
                QueuePlotData(
                    self.patients_waiting, 1, PlotType.bar, "Patients waiting"
                ),
            )
        )

    def pre_entities_tick(self):
        while len(self.patients) > 0 and self.patients[0][0] <= World.seconds():
            self.patients_waiting.enqueue(self.patients[0][1])
            self.patients.pop(0)

        while not self.beds.occupied and not self.patients_waiting == 0:
            next = self.patients_waiting.peek()
            self.beds.try_use(next)

    # def post_entities_tick(self):
    # if not self.headless:
    # self.overview.append(World.seconds(), World.seconds() * 5.0)
