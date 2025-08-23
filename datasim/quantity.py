from typing import Dict, Final, List, Self, Tuple

from .dataset import PlotOptions, XYData
from .types import Number, PlotType


class Quantity:
    """Representation of a custom quantity that can be automatically saved and plotted."""

    world: Final
    """Unique identifier of the quantity."""
    id: Final[str]
    """Descriptive type of things or unit of the quantity (also used as plot axis legend)."""
    quantity_type: str
    """Optional minimum value of the quantity."""
    min: Number
    """Optional maximum value of the quantity."""
    max: Number

    _outputs: List[Tuple[int, XYData]]
    _value: Number

    def __init__(
        self,
        world,
        id: str,
        quantity_type: str,
        start_value: Number = None,
        min: Number = None,
        max: Number = None,
        gather: bool = True,
        data_id: str = "",
        sample_frequency: int = 1,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a quantity.

        Args:
            world (`World`): the World to add this quantity to.
            id (str): Descriptive name of the quantity.
            start_value (int | float | None, optional): Starting value of the quantity.
                If set to `None`, won't add data points until `__set__` is called, even if gather is set
                and sample_frequency is greater than zero. Defaults to `None`.
            min (int | float | None, optional): Optional minimum value of the quantity.
                If set, any attempts to set an amount below this value will be clamped off. Defaults to `None`.
            max (int | float | None, optional): Optional maximum value of the quantity.
                If set, any attempts to set an amount above this value will be clamped off. Defaults to `None`.
            gather (`PlotType` or `False`, optional): Whether to automatically gather data for the output
                for this quantity, and which type of plot if so. Defaults to `PlotType.none` to only save.
            data_id (str, optional): id for the data source if `gather` is True. Defaults to empty string
                which sets `data_id` to the value of this Quantity's `id`.
            sample_frequency (int, optional): Whether to add a data point every `frequency` ticks.
                If set to `0`, adds a data point only when the quantity changes. Defaults to `0`.
            plot_options (Optional[PlotOptions], optional): Options for a plot. Defaults to default PlotOptions.
        """
        self.world = world
        self.id = id
        self.quantity_type = quantity_type
        self._outputs = []
        self.min = min
        self.max = max
        self._value = start_value

        self.world.add(self)

        if gather:
            self.add_output(data_id, sample_frequency, plot_options)

    @staticmethod
    def _from_yaml(world, params: Dict) -> "Quantity":
        id = list(params.keys())
        if len(id) > 1:
            raise ValueError(f"Unable to parse yaml: Multiple keys found in {params}")

        id = id[0]
        params = params[id]

        return Quantity(
            world,
            id,
            params["quantity_type"],
            params.get("start_value", None),
            params.get("min", None),
            params.get("max", None),
            params.get("gather", True),
            params.get("data_id", ""),
            params.get("sample_frequency", 1),
            PlotOptions._from_yaml(params.get("plot_options", {})),
        )

    def add_output(
        self,
        data_id: str = "",
        frequency: int = 0,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create an output source for this Quantity. Also automatically used when `gather` is True at creation.

        Args:
            data_id (str, optional): Unique identifier of the source. Defaults to empty string which sets `data_id`
                to the value of this Quantity's `id`.
            frequency (int, optional): Saves every x ticks or only on change if set to 0. Defaults to 0.
            plot_options (Optional[PlotOptions], optional): Options for a plot. Defaults to default PlotOptions.
        """
        if data_id == "":
            data_id = self.id

        if (
            plot_options.aggregate_only
            and plot_options.plot_type != PlotType.export_only
        ):
            plot_options.plot_type = PlotType.none

        if plot_options.legend_x == "":
            plot_options.legend_x = self.world.time_unit
        if plot_options.legend_y == "":
            plot_options.legend_y = self.quantity_type

        x = []
        y = []
        if self._value:
            x.append(self.world.time)
            y.append(self._value)
        data = XYData(self.world, x, y, plot_options)
        self._outputs.append((frequency, data))
        self.world.add_data(data_id, data)

    def _tick(self):
        if self._value is not None:
            for index, (frequency, data) in enumerate(self._outputs):
                if self.world.ticks % frequency == 0:
                    data.append(self.world.time, self._value)

    def _get(self) -> Number:
        return self._value

    def _set(self, value: int | float | None):
        if value is None:
            if self._value is not None:
                raise ValueError(
                    "Quantities can't be set to None after having had a value!"
                )
            return
        self._value = value
        for frequency, data in self._outputs:
            if frequency == 0:
                data.append(self.world.time, self._value)

    value = property(_get, _set, None, """Current value of the quantity.""")

    # region Utility functions

    def __eq__(self, other: object):
        """Check if the quantity is equal to a number."""
        if self is other:
            return True
        if self._value is None:
            return other is None
        return self._value == other

    def __lt__(self, other: object):
        """Check if the quantity is less than a number."""
        if (isinstance(self._value, int) or isinstance(self._value, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self._value < other
        return False

    def __le__(self, other: object):
        """Check if the quantity is less than or equal to a number."""
        if (isinstance(self._value, int) or isinstance(self._value, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self._value <= other
        return False

    def __gt__(self, other: object):
        """Check if the quantity is greater than a number."""
        if (isinstance(self._value, int) or isinstance(self._value, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self._value > other
        return False

    def __ge__(self, other: object):
        """Check if the quantity is greater than or equal to a number."""
        if other is None:
            return False
        if (isinstance(self._value, int) or isinstance(self._value, float)) and (
            isinstance(other, int) or isinstance(other, float)
        ):
            return self._value >= other
        return False

    def __iadd__(self, other: Number) -> Self:
        """Add a number to the quantity."""
        if self.value is None:
            raise ValueError(
                "Can't add to a Quantity that did not have a starting value."
            )
        if other is None:
            return self
        if isinstance(self._value, int):
            self.value += int(other)
        elif isinstance(self._value, float):
            self.value += other
        return self

    def __isub__(self, other: Number) -> Self:
        """Subtract a number from the quantity."""
        if self.value is None:
            raise ValueError(
                "Can't subtract from a Quantity that did not have a starting value."
            )
        if other is None:
            return self
        if isinstance(self._value, int):
            self.value -= int(other)
        elif isinstance(self._value, float):
            self.value -= other
        return self

    def __imul__(self, other: Number) -> Self:
        """Multiply the quantity by a number."""
        if self.value is None:
            raise ValueError(
                "Can't multiply a Quantity that did not have a starting value."
            )
        if other is None:
            return self
        if isinstance(self._value, int):
            self.value *= int(other)
        elif isinstance(self._value, float):
            self.value *= other
        return self

    def __itruediv__(self, other: Number) -> Self:
        """Divide the quantity by a number."""
        if self.value is None:
            raise ValueError(
                "Can't divide a Quantity that did not have a starting value."
            )
        if other is None:
            return self
        if isinstance(self._value, int):
            self.value //= int(other)
        elif isinstance(self._value, float):
            self.value /= other
        return self

    def __ifloordiv__(self, other: Number) -> Self:
        """Integer divide the quantity by a number."""
        if self.value is None:
            raise ValueError(
                "Can't divide a Quantity that did not have a starting value."
            )
        if other is None:
            return self
        if isinstance(self._value, int):
            self.value //= int(other)
        elif isinstance(self._value, float):
            self.value //= other
        return self

    def __imod__(self, other: Number) -> Self:
        """Make the quantity the modulus of a number."""
        if self.value is None:
            raise ValueError(
                "Can't take modulus of a Quantity that did not have a starting value."
            )
        if other is None:
            return self
        if isinstance(self._value, int):
            self.value %= int(other)
        elif isinstance(self._value, float):
            self.value %= other
        return self

    def __ipow__(self, other: Number) -> Self:
        """Raise the quantity by a power."""
        if self.value is None:
            raise ValueError(
                "Can't raise a Quantity that did not have a starting value to any power."
            )
        if other is None:
            return self
        if self._value is not None:
            self.value **= other
        return self

    def __int__(self) -> int:
        """Get the quantity as an int. Returns -1 if the resource has no amount."""
        if isinstance(self._value, int):
            return self._value
        elif isinstance(self._value, float):
            return int(self._value)
        return -1

    def __float__(self) -> float:
        """Get the quantity as a float. Returns -1.0 if the resource has no amount."""
        if isinstance(self._value, int):
            return float(self._value)
        if isinstance(self._value, float):
            return self._value
        return -1.0

    def __str__(self) -> str:
        """Get a string representation of the quantity."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Get a string representation of the quantity."""
        return f"Quantity {self.id}"

    # endregion
