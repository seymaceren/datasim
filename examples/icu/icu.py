from csv import reader
from math import inf
from typing import Any, Dict, List, Optional

import pandas as pd

from datasim import log, LogLevel, Quantity, Queue, Resource, StateData, World
from .patient import (
    DiedPatientState,
    PatientData,
    Patient,
    TreatedPatientState,
    WaitingPatientState,
)


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
        variation_dict: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            runner=runner,
            headless=headless,
            definition=definition,
            variation=variation,
            variation_dict=variation_dict,
        )

        if runner.data_source:
            self.load_patient_data(runner.data_source)
        else:
            self.generate_patient_data(500)

    def load_patient_data(self, filename: str):
        self.patients = []
        for row in list(reader(open(filename)))[1:]:
            self.patients.append(PatientData(row))
        log(f"Loaded data for {len(self.patients)} patients", LogLevel.debug)

    def generate_patient_data(self, end_enter_time: float):
        self.patients = self.generators["patient_generator"].generate(
            PatientData, limits={"enter_time": (">", end_enter_time)}, sort="enter_time"
        )
        log(f"Generated data for {len(self.patients)} patients", LogLevel.debug)

    def remove(self, obj):
        if isinstance(obj, Patient):
            if obj.state == TreatedPatientState:
                self.patients_treated += 1
            else:
                self.patients_died += 1
        return super().remove(obj)

    def before_entities_update(self):
        while len(self.patients) > 0 and self.patients[0].enter_time <= self.time:
            patient_data = self.patients.pop(0)
            patient = Patient(
                self, patient_data.id, patient_data.illness, patient_data.treatment_time
            )
            self.patients_waiting.enqueue(patient)

        # We don't want our patients to look for beds themselves but in order of the queue.
        peek = self.patients_waiting.peek()
        while peek is not None and not self.beds.occupied:
            next, _ = peek
            if next.state == DiedPatientState:
                self.patients_waiting.dequeue()
            else:
                queue_string = " // ".join(
                    [
                        f"{p.id} {p.illness} {p.critical_time:.1f}"
                        for p, _ in self.patients_waiting.queue
                    ]
                )
                log(f"Queue:\n{queue_string}", LogLevel.debug, "yellow")
                self.beds.try_use(
                    next,
                    usage_time=next.treatment_time,
                    remove_from_queue=self.patients_waiting,
                )
            peek = self.patients_waiting.peek()

    def after_entities_update(self):
        if (
            len(self.patients_waiting) == 0
            and len(self.entities) == 0
            and len(self.patients) == 0
        ):
            self.stopped = True

    def aggregate_data(self) -> Dict[str, pd.DataFrame]:
        patient_data = []
        for source in self.datasets["Patients"].sources:
            if not isinstance(source, StateData) or not isinstance(
                source.source, Patient
            ):
                continue
            arrived = None
            in_bed = None
            treated = None
            died = None
            for index, row in source._data_frame.iterrows():
                match row["state"]:
                    case "Waiting":
                        arrived = row["hours"]
                    case "Using_bed":
                        in_bed = row["hours"]
                    case "Treated":
                        treated = row["hours"]
                    case "Died":
                        died = row["hours"]
            if arrived is None:
                arrived = in_bed if in_bed else 0.0
            bed_time = (
                0.0
                if in_bed is None
                else ((treated if treated else died if died else 0.0) - in_bed)
            )
            patient_data.append(
                {
                    "id": source.source.id,
                    "condition": source.source.illness,
                    "arrived": arrived,
                    "treated": treated,
                    "died": died,
                    "waiting": (
                        (in_bed if in_bed else died if died else arrived) - arrived
                    ),
                    "bed_time": bed_time,
                }
            )

        return {
            "Patient_Timing": pd.DataFrame(
                patient_data,
                columns=[
                    "id",
                    "condition",
                    "arrived",
                    "waiting",
                    "bed_time",
                    "treated",
                    "died",
                ],
            )
        }
