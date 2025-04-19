from colors import color
from typing import Dict, Optional
from datasim import Entity, State, Resource, World


class WaitingPatientState(State):
    patient: "Patient"

    def __init__(self):
        super().__init__("Waiting for a bed")

    def tick(self):
        if not hasattr(self, "patient"):
            if isinstance(self.entity, Patient):
                self.patient = self.entity
            else:
                return

        self.patient.deteriorate()


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
        super().__init__(name)
        self.condition = condition
        self.treatment_time = treatment_time
        self.alive = True

        self.critical_time = critical_time_for_condition[condition]

    def deteriorate(self):
        if self.critical_time:
            self.critical_time -= World.tick_time
            if self.critical_time <= 0.0:
                self.died()

    def resource_done(self, resource: Resource):
        if resource.resource_type == "beds":
            print(color(f"Patient {self.name} is treated!", fg="green"))
            World.current.remove(self)

    def died(self):
        self.alive = False
        print(
            color(f"Patient {self.name} died of condition {self.condition}!", fg="red")
        )
        World.current.remove(self)
        pass
