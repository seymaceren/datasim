from datasim import Entity
from datasim import State


class NewPatientState(State):
    pass


class Patient(Entity):
    def start(self):
        self.set_state(NewPatientState)
