from enum import Enum, IntEnum


Number = int | float | None


class LogLevel(IntEnum):
    """The result of a resource usage attempt."""

    verbose = 3
    debug = 2
    warning = 1
    error = 0

    def __str__(self) -> str:
        """Get a string representation of the result."""
        match self:
            case LogLevel.verbose:
                return "Verbose"
            case LogLevel.debug:
                return "Debug"
            case LogLevel.warning:
                return "Warnings"
            case LogLevel.error:
                return "Errors"


class PlotType(Enum):
    """The type of plot to render."""

    bar = "bar"
    line = "line"
    pie = "pie"
    scatter = "scatter"

    def __str__(self) -> str:
        """Get a string representation of the plot type."""
        match self:
            case PlotType.bar:
                return "Bar chart"
            case PlotType.line:
                return "Line graph"
            case PlotType.pie:
                return "Pie chart"
            case PlotType.scatter:
                return "Scatter plot"


class UseResult(Enum):
    """The result of a resource usage attempt."""

    success = "success"
    depleted = "depleted"
    insufficient = "insufficient"
    queued = "queued"
    in_use = "in_use"

    def __str__(self) -> str:
        """Get a string representation of the result."""
        match self:
            case UseResult.success:
                return "Success"
            case UseResult.depleted:
                return "Failed: Resource depleted"
            case UseResult.insufficient:
                return "Failed: Insufficient amount available"
            case UseResult.queued:
                return "Queued"
            case UseResult.in_use:
                return "Failed: Resource in use"
