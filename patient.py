from datasim.entity import Entity


class Patient(Entity):
    def start():
        set_state(NewPatientState)
