import csv
from math import sin
from typing import List, Tuple

from datasim import Plot, Queue, ResourcePlotData, Resource, simtime, World, XYPlotData
from .patient import Patient


class ICU(World):
    overview: XYPlotData
    beds: Resource
    patients: List[Tuple[float, Patient]]
    patients_waiting: Queue[Patient]

    def __init__(self):
        super().__init__("ICU world")

        self.beds = Resource(self, "icu_beds", "bed", 4)

        self.add_plot(Plot("beds", ResourcePlotData(self.beds)))

        self.patients = []
        for row in csv.reader(open("simulatiedata.csv")):
            if not (row[0]).isnumeric():
                continue
            self.patients.append((float(row[1]), Patient(row[0], row[3], float(row[2]))))
        self.patients_waiting = Queue[Patient]("patients")

    def pre_entities_tick(self):
        while self.patients[0][0] >= simtime.seconds():
            self.patients_waiting.enqueue(self.patients[0][1])
            self.patients.pop(0)



    def post_entities_tick(self):
        self.overview.append(simtime.seconds(), sin(simtime.seconds() * 5.0))
