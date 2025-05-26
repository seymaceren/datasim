from typing import Dict, Final, List, Self, Tuple

from .plot import PlotOptions, XYPlotData
from .types import Number


class Quantity:
    """Representation of a custom quantity that can be automatically plotted and exported."""

    world: Final
    """Unique identifier of the quantity."""
    id: Final[str]
    """Descriptive type of things or unit of the quantity, used as plot axis legend."""
    quantity_type: str
    """Optional minimum value of the quantity."""
    min: Number
    """Optional maximum value of the quantity."""
    max: Number

    _plots: List[Tuple[int, XYPlotData]]
    _value: Number

    def __init__(
        self,
        world,
        id: str,
        quantity_type: str,
        start_value: Number = None,
        min: Number = None,
        max: Number = None,
        auto_plot: bool = True,
        plot_id: str = "",
        plot_frequency: int = 1,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a quantity.

        Args:
            world (`World`): the World to add this quantity to.
            id (str): Descriptive name of the quantity.
            start_value (int | float | None, optional): Starting value of the quantity.
                If set to `None`, won't add data points until `__set__` is called, even if auto_plot is set
                and plot_frequency is greater than zero. Defaults to `None`.
            min (int | float | None, optional): Optional minimum value of the quantity.
                If set, any attempts to set an amount below this value will be clamped off. Defaults to `None`.
            max (int | float | None, optional): Optional maximum value of the quantity.
                If set, any attempts to set an amount above this value will be clamped off. Defaults to `None`.
            auto_plot (`PlotType` or `False`, optional): Whether to automatically add a plot to the dashboard
                for this quantity, and which type of plot if so. Defaults to `PlotType.line`.
            plot_frequency (int, optional): Whether to add a data point every `frequency` ticks.
                If set to `0`, adds a data point only when the quantity changes. Defaults to `0`.
            plot_title (Optional[str], optional): An optional plot title. Defaults to `None`.
        """
        self.world = world
        self.id = id
        self.quantity_type = quantity_type
        self._plots = []
        self.min = min
        self.max = max
        self._value = start_value

        self.world.add(self)

        if auto_plot:
            self.make_plot(plot_id, plot_frequency, plot_options)

    @staticmethod
    def from_yaml(world, params: Dict) -> "Quantity":
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
            params.get("auto_plot", True),
            params.get("plot_id", ""),
            params.get("plot_frequency", 1),
            PlotOptions.from_yaml(params.get("plot_options", {})),
        )

    def make_plot(
        self,
        plot_id="",
        frequency: int = 0,
        plot_options: PlotOptions = PlotOptions(),
    ):
        """Create a plot for this Quantity. Also automatically used when `auto_plot` is True at creation.

        Args:
            plot_type (PlotType, optional): The type of plot to add. Defaults to PlotType.line.
            frequency (int, optional): Plot every x ticks or only on change if set to 0. Defaults to 0.
            plot_title (Optional[str], optional): Optional title for the plot. Defaults to None.
        """
        if plot_id == "":
            plot_id = self.id

        if plot_options.legend_x == "":
            plot_options.legend_x = self.world.time_unit
        if plot_options.legend_y == "":
            plot_options.legend_y = self.quantity_type

        x = []
        y = []
        if self._value:
            x.append(0.0)
            y.append(self._value)
        data = XYPlotData(self.world, x, y, plot_options)

        self._plots.append((frequency, data))

        self.world.add_plot(plot_id, data)

    def _tick(self):
        if self._value:
            for index, (frequency, data) in enumerate(self._plots):
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
        for frequency, data in self._plots:
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
