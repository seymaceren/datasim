from flatdict import FlatDict
from typing import Dict, Final, List

from .types import Value


class Constant:
    """A numeric or string value used to initialise a simulation run. Can also be set to `None`.

    These are used to create variations of constant values outside of other simulation
    objects (e.g. `Resource`s or `Queue`s) between different batches.
    """

    world: Final
    id: Final[str]
    value: Value

    def __init__(self, world, id: str, value: Value):
        """Create a constant value.

        Args:
            world (World): The world the constant belongs to.
            id (str): Unique identifier of the `Constant`.
            value (int or float or str or None): The value of the constant.
        """
        self.world = world
        self.id = id
        self.value = value

        self.world.add(self)

    @staticmethod
    def _from_yaml(world, params: Dict) -> List["Constant"]:
        flat: Dict[str, Value] = dict(FlatDict(params, delimiter=":"))

        results: List[Constant] = []

        for key, value in flat.items():
            results.append(Constant(world, key, value))

        return results

    def __eq__(self, value):
        """Constants can be compared by their value."""
        return self.value == value or self is value

    def __int__(self):
        """Get the int value of the constant. Returns `0` if the value is `None`."""
        if self.value is None:
            return 0
        return int(self.value)

    def __float__(self):
        """Get the float value of the constant. Returns `0.0` if the value is `None`."""
        if self.value is None:
            return 0.0
        return float(self.value)

    def __str__(self):
        """Get the value of the constant as a string."""
        return str(self.value)
