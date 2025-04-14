from datasim import Entity
from datasim import State


class NewPatientState(State):
    pass


class Patient(Entity):
    treatment_time: float
    condition: str

    def __init__(self, name, condition: str, treatment_time: float):
        super().__init__(name, NewPatientState)
        self.condition = condition
        self.treatment_time = treatment_time
