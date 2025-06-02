from csv import reader
from typing import Dict, List, Optional

from datasim import Quantity, Queue, Resource, World
from .patient import DiedPatientState, PatientData, Patient, TreatedPatientState


class ICU(World):
    patients: List[PatientData]

    # You can define the types of objects loaded from YAML as attributes to get type checking
    # and IDE completion and such.
    beds: Resource
    patients_waiting: Queue[Patient]
    patients_treated: Quantity
    patients_died: Quantity

    def __init__(
        self,
        runner,
        headless: bool = False,
        definition: Optional[Dict] = None,
        variation: Optional[str] = None,
    ):
        super().__init__(
            runner=runner, headless=headless, definition=definition, variation=variation
        )

        self.load_patient_data("examples/icu/simulatiedata.csv")

    def load_patient_data(self, filename: str):
        self.patients = []
        for row in list(reader(open(filename)))[1:]:
            self.patients.append(PatientData(row))

    def remove(self, obj):
        if isinstance(obj, Patient):
            if obj.state == TreatedPatientState:
                self.patients_treated += 1
            else:
                self.patients_died += 1
        return super().remove(obj)

    def before_entities_update(self):
        while len(self.patients) > 0 and self.patients[0].enter_time <= self.time:
            patient = self.patients.pop(0)
            self.patients_waiting.enqueue(
                Patient(self, patient.id, patient.illness, patient.treatment_time)
            )

        # We don't want our patients to look for beds themselves but in order of arrival.
        next = self.patients_waiting.peek()
        while next is not None and not self.beds.occupied:
            if next.state == DiedPatientState:
                self.patients_waiting.dequeue()
            else:
                self.beds.try_use(
                    next,
                    usage_time=next.treatment_time,
                    remove_from_queue=self.patients_waiting,
                )
            next = self.patients_waiting.peek()

    def after_entities_update(self):
        if len(self.patients_waiting) == 0 and len(self.entities) == 0:
            self.stopped = True
