import csv
from colors import color
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
from .patient import Patient, WaitingPatientState


class ICU(World):
    overview: XYPlotData
    patients: List[Tuple[float, Patient]]
    beds: Resource
    patients_waiting: Queue[Patient]
    patients_treated: int = 0
    patients_died: int = 0
    icu: Self

    def __init__(self, headless: bool = False):
        super().__init__("ICU world", headless=headless)

        ICU.icu = self

        self.beds = Resource(self, "beds", "beds", 15)
        self.add(self.beds)

        self.add_plot(
            Plot(
                "beds",
                ResourcePlotData(
                    "beds", True, 1, PlotType.line, "Beds in use", legend_y="beds"
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
                QueuePlotData("patients_waiting", 1, PlotType.line, "Patients waiting"),
            )
        )

        self.treated = XYPlotData(
            [], [], PlotType.line, "Patients treated", "seconds", "patients"
        )
        self.died = XYPlotData(
            [], [], PlotType.line, "Patients died", "seconds", "patients"
        )
        self.treated_vs_died = Plot("treated", self.treated)
        self.died_plot = Plot("died", self.died)
        self.add_plot(self.treated_vs_died)
        self.add_plot(self.died_plot)

    def remove(self, obj):
        if isinstance(obj, Patient):
            if obj.alive:
                self.patients_treated += 1
                self.treated.append(World.seconds(), self.patients_treated)
            else:
                self.patients_died += 1
                self.died.append(World.seconds(), self.patients_died)
        return super().remove(obj)

    def pre_entities_tick(self):
        while len(self.patients) > 0 and self.patients[0][0] <= World.seconds():
            print(
                color(
                    f"Patient joining queue of {len(self.patients_waiting)} at {self.patients[0][0]}",
                    fg=45,
                )
            )
            patient = self.patients[0][1]
            patient.set_state(WaitingPatientState)
            self.patients_waiting.enqueue(patient)
            self.patients.pop(0)

        # We don't want our patients to look for beds themselves but in order of arrival.
        while not self.beds.occupied and not len(self.patients_waiting) == 0:
            next = self.patients_waiting.peek()
            if not next.alive:
                self.patients_waiting.dequeue()
            else:
                result = self.beds.try_use(next, usage_time=next.treatment_time)
                print(
                    color(
                        f"Patient {next.name} trying to use a bed at {World.seconds()}: {result}",
                        fg="blue",
                    )
                )
                if result == UseResult.success:
                    self.patients_waiting.dequeue()

    def post_entities_tick(self):
        if len(self.patients_waiting) == 0 and len(self.entities) == 0:
            self.stopped = True
