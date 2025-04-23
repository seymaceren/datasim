import csv
from colors import color
from typing import List, Self

from datasim import (
    Quantity,
    Queue,
    Resource,
    simulation,
    UseResult,
    World,
    XYPlotData,
)
from .patient import PatientData, Patient, WaitingPatientState


class ICU(World):
    overview: XYPlotData
    patients: List[PatientData]
    beds: Resource
    patients_waiting: Queue[Patient]
    patients_treated: Quantity
    patients_died: Quantity
    icu: Self

    def __init__(self, headless: bool = False):
        super().__init__("ICU world", headless=headless)

        ICU.icu = self

        self.load_patient_data("examples/icu/simulatiedata.csv")

        self.beds = Resource("beds", "beds", 5, plot_title="Beds in use")
        self.patients_waiting = Queue[Patient]("patients_waiting")
        self.patients_treated = Quantity("Patients treated", 0)
        self.patients_died = Quantity("Patients died", 0)

    def load_patient_data(self, filename: str):
        self.patients = []
        for row in csv.reader(open(filename)):
            patient = PatientData()
            patient.__dict__ = {
                "id": row[0],
                "enter_time": float(row[1]),
                "treatment_time": float(row[2]),
                "condition": row[3],
            }
            self.patients.append(patient)

    def remove(self, obj):
        if isinstance(obj, Patient):
            if obj.alive:
                self.patients_treated += 1
            else:
                self.patients_died += 1
        return super().remove(obj)

    def pre_entities_tick(self):
        while len(self.patients) > 0 and self.patients[0].enter_time <= simulation.time:
            patient = self.patients[0]
            print(
                color(
                    f"Patient joining queue of {len(self.patients_waiting)} at {patient.enter_time}",
                    fg=45,
                )
            )
            patient = Patient(patient.id, patient.condition, patient.treatment_time)
            patient.state = WaitingPatientState
            self.patients_waiting.enqueue(patient)
            self.patients.pop(0)

        # We don't want our patients to look for beds themselves but in order of arrival.
        next = self.patients_waiting.peek()
        while not self.beds.occupied and next is not None:
            if not next.alive:
                self.patients_waiting.dequeue()
            else:
                result = self.beds.try_use(next, usage_time=next.treatment_time)
                print(
                    color(
                        f"Patient {next.name} trying to use a bed at {simulation.time}: {result}",
                        fg="blue",
                    )
                )
                if result == UseResult.success:
                    self.patients_waiting.dequeue()

    def post_entities_tick(self):
        if len(self.patients_waiting) == 0 and len(self.entities) == 0:
            self.stopped = True
