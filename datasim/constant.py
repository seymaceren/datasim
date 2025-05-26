from flatdict import FlatDict
from typing import Dict, Final, List

from .types import Value


class Constant:
    world: Final
    id: Final[str]
    value: Value

    def __init__(self, world, id: str, value: Value):
        self.world = world
        self.id = id
        self.value = value

        self.world.add(self)

    @staticmethod
    def from_yaml(world, params: Dict) -> List["Constant"]:
        flat: Dict[str, Value] = dict(FlatDict(params, delimiter=":"))

        results: List[Constant] = []

        for key, value in flat.items():
            results.append(Constant(world, key, value))

        return results

    def __eq__(self, value):
        return self.value == value or self is value

    def __int__(self):
        if self.value is None:
            return 0
        return int(self.value)

    def __float__(self):
        if self.value is None:
            return 0.0
        return float(self.value)

    def __str__(self):
        return str(self.value)
