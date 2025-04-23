from typing import List, Literal, Optional, Self, Tuple

from .plot import Plot, PlotType, XYPlotData
from .types import Number
import simulation


class Quantity:
    """Representation of a custom quantity that can be automatically plotted and exported."""

    """Descriptive name of the quantity."""
    id: str
    """Optional minimum value of the quantity."""
    min: Number
    """Optional maximum value of the quantity."""
    max: Number

    _plots: List[Tuple[int, XYPlotData]]
    _value: Number

    def __init__(
        self,
        id: str,
        start_value: Number = None,
        min: Number = None,
        max: Number = None,
        auto_plot: PlotType | Literal[False] = PlotType.line,
        plot_frequency: int = 1,
        plot_title: Optional[str] = None,
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
        self.id = id
        self._plots = []
        self.min = min
        self.max = max
        self._value = start_value

        simulation.world().add(self)

        if auto_plot:
            self.make_plot(auto_plot, plot_frequency, plot_title)

    def make_plot(
        self,
        auto_plot: PlotType = PlotType.line,
        plot_frequency: int = 0,
        plot_title: Optional[str] = None,
    ):
        data = XYPlotData([], [], auto_plot, plot_title, legend_y=self.id)

        self._plots.append((plot_frequency, data))

        simulation.world().add_plot(Plot(self.id, data))

    def _tick(self):
        if self._value:
            for index, (frequency, data) in enumerate(self._plots):
                if simulation.ticks % frequency == 0:
                    data.append(simulation.time, self._value)

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
                data.append(simulation.time, self._value)

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
