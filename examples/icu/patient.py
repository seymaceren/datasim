from typing import Dict, Optional
from datasim import Entity, State, World


class WaitingPatientState(State):
    def tick(self):
        patient: Patient = self.entity
        patient.deteriorate()


critical_time_for_condition: Dict[str, Optional[float]] = {
    "A": None,
    "B": 400.0,
    "C": 200.0,
}


class Patient(Entity):
    treatment_time: float
    condition: str
    alive: bool

    critical_time: Optional[float] = None

    def __init__(self, name, condition: str, treatment_time: float):
        super().__init__(name, WaitingPatientState)
        self.condition = condition
        self.treatment_time = treatment_time
        self.alive = True

        self.critical_time = critical_time_for_condition[condition]

    def deteriorate(self):
        if self.critical_time:
            self.critical_time -= World.tick_time
            if self.critical_time <= 0.0:
                self.died()

    def died(self):
        self.alive = False
        print(f"Patient {self.name} died of condition {self.condition}!")
        World.current.remove(self)
        pass
