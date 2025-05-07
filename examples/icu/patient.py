from typing import Dict, List, Optional
from datasim import Entity, log, LogLevel, State, UsingResourceState, simulation


critical_duration_for_illness: Dict[str, Optional[float]] = {
    "A": None,
    "B": 400.0,
    "C": 200.0,
}


class WaitingPatientState(State):
    patient: "Patient"

    def __init__(self, _name, patient: "Patient"):
        super().__init__("Waiting for a bed", patient)
        self.patient = patient

        critical_duration = critical_duration_for_illness[self.patient.illness]
        self.critical_time = (
            simulation.time + critical_duration if critical_duration else None
        )

    def tick(self):
        if (
            self.patient.critical_time is not None
            and simulation.time >= self.patient.critical_time
        ):
            self.patient.died()


class PatientData:
    id: str
    enter_time: float
    treatment_time: float
    illness: str

    def __init__(self, data: List):
        self.id = data[0]
        self.enter_time = float(data[1])
        self.treatment_time = float(data[2])
        self.illness = data[3]


class Patient(Entity):
    plural: str = "Patients"

    treatment_time: float
    illness: str
    alive: bool

    critical_time: Optional[float] = None

    def __init__(self, name, illness: str, treatment_time: float):
        self.illness = illness
        self.treatment_time = treatment_time
        self.alive = True
        super().__init__(name, WaitingPatientState)

    def on_state_leaving(self, old_state: State | None, new_state: State | None):
        if (
            isinstance(old_state, UsingResourceState)
            and old_state.resource.id == "beds"
            and old_state.completed
        ):
            log(f"{self} is treated!", LogLevel.debug, "green")
            simulation.world().remove(self)

    def died(self):
        self.alive = False
        log(f"{self} died of illness {self.illness}!", LogLevel.debug, "red")
        simulation.world().remove(self)
