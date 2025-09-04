from math import inf
from typing import List
from datasim import (
    Entity,
    log,
    LogLevel,
    PlotOptions,
    PlotType,
    State,
    UsingResourceState,
)


class WaitingPatientState(State):
    type_id: str = "Waiting"
    patient: "Patient"

    def __init__(self, _name, patient: "Patient"):
        super().__init__("Waiting for a bed", patient)
        self.patient = patient

        critical_duration = self.patient.world.constant(
            "critical_duration", self.patient.illness
        )

        self.patient.critical_time = (
            (self.patient.world.time + float(critical_duration))
            if critical_duration.value is not None
            else inf
        )
        log(
            f"{self.patient} will be critical at time {self.patient.critical_time}",
            LogLevel.verbose,
            world=self.entity.world,
        )

    def tick(self):
        if self.patient.world.time >= self.patient.critical_time - (
            self.patient.world.tick_time * 0.01
        ):
            self.patient.state = DiedPatientState


class TreatedPatientState(State):
    type_id: str = "Treated"

    def __init__(self, _name, entity):
        super().__init__("Treated", entity)

    def tick(self):
        log(
            f"{self.entity} is treated!",
            LogLevel.debug,
            "green",
            world=self.entity.world,
        )
        self.entity.remove()


class DiedPatientState(State):
    type_id: str = "Died"

    def __init__(self, _name, patient: "Patient"):
        super().__init__("Died", patient)
        self.patient = patient

    def on_enter(self):
        log(
            f"{self.patient} died of illness {self.patient.illness}!",
            LogLevel.debug,
            "red",
            world=self.entity.world,
        )

    def tick(self):
        self.entity.remove()


class PatientData:
    id: str
    enter_time: float
    treatment_time: float
    illness: str

    def __init__(self, data: List = []):
        if len(data) > 3:
            self.id = data[0]
            self.enter_time = float(data[1])
            self.treatment_time = float(data[2])
            self.illness = data[3]

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} {self.id}, {self.illness}, "
            f"E {self.enter_time:.1f}, T {self.treatment_time:.1f}"
        )


class Patient(Entity):
    plural: str = "Patients"

    treatment_time: float
    illness: str

    critical_time: float = inf

    def __init__(self, world, name, illness: str, treatment_time: float):
        self.illness = illness
        self.treatment_time = treatment_time
        options = PlotOptions(
            auto_name=True,
            plot_type=PlotType.none,
        )
        super().__init__(world, name, WaitingPatientState, True, "Patients", options)

    def on_state_leaving(
        self, old_state: State | None, new_state: State | None
    ) -> State | type | None:
        if (
            isinstance(old_state, UsingResourceState)
            and old_state.resource.id == "beds"
            and old_state.completed
        ):
            return TreatedPatientState
        return new_state

    def __repr__(self) -> str:
        """Get a string representation of the Patient."""
        return (
            f"{self.__class__.__name__} {self.id}, {self.illness} "
            f"(T {self.treatment_time:.1f} C {self.critical_time:.1f})"
        )
