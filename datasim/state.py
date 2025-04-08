from abc import ABC
from typing import Self

class State(ABC):
    name: str
    switch_to: Self | None

    def __init__(self, name: str):
        self.name = name
        self.switch_to = None

    def tick(self):
        pass
