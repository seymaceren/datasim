import csv
from typing import List, Self

from datasim import Quantity, Queue, Resource, simulation, World
from .patient import PatientData, Patient


class ICU(World):
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
        self.patients_waiting = Queue[Patient](
            "patients_waiting", plot_title="Patients waiting"
        )
        self.patients_treated = Quantity(
            "patients_treated", "patients", 0, plot_title="Patients treated"
        )
        self.patients_died = Quantity(
            "patients_died", "patients", 0, plot_title="Patients died"
        )

    def load_patient_data(self, filename: str):
        self.patients = []
        for row in list(csv.reader(open(filename)))[1:]:
            self.patients.append(PatientData(row))

    def remove(self, obj):
        if isinstance(obj, Patient):
            if obj.alive:
                self.patients_treated += 1
            else:
                self.patients_died += 1
        return super().remove(obj)

    def before_entities_update(self):
        while len(self.patients) > 0 and self.patients[0].enter_time <= simulation.time:
            patient = self.patients.pop(0)
            self.patients_waiting.enqueue(
                Patient(patient.id, patient.illness, patient.treatment_time)
            )

        # We don't want our patients to look for beds themselves but in order of arrival.
        next = self.patients_waiting.peek()
        while next is not None and not self.beds.occupied:
            if not next.alive:
                self.patients_waiting.dequeue()
            else:
                self.beds.try_use(
                    next,
                    usage_time=next.treatment_time,
                    remove_from_queue=self.patients_waiting,
                )

    def after_entities_update(self):
        if len(self.patients_waiting) == 0 and len(self.entities) == 0:
            self.stopped = True
