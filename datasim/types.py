from enum import Enum, IntEnum
from typing import Any, Dict, Optional


Number = int | float | None
Value = str | Number


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


class PlotOptions:
    """Defines the options for plotting a PlotData."""

    title: Optional[str]
    name: Optional[str]
    plot_type: Optional[PlotType]
    legend_x: str
    legend_y: str
    secondary_y: bool
    color: Optional[str]
    color_continuous_scale: Optional[Any]
    color_continuous_midpoint: Optional[Any]
    color_discrete_map: Optional[Any]
    color_discrete_sequence: Optional[Any]
    range_color: Optional[Any]
    hover_name: Optional[Any]
    hover_data: Optional[Any]
    custom_data: Optional[Any]
    text: Optional[Any]
    facet_row: Optional[Any]
    facet_col: Optional[Any]
    facet_row_spacing: Optional[Any]
    facet_col_spacing: Optional[Any]
    facet_col_wrap: int
    error_x: Optional[Any]
    error_y: Optional[Any]
    error_x_minus: Optional[Any]
    error_y_minus: Optional[Any]
    category_orders: Optional[Any]
    labels: Optional[Any]
    orientation: Optional[Any]
    opacity: Optional[Any]
    log_x: bool
    log_y: bool
    range_x: Optional[Any]
    range_y: Optional[Any]
    pattern_shape: Optional[Any]
    pattern_shape_map: Optional[Any]
    pattern_shape_sequence: Optional[Any]
    base: Optional[Any]
    barmode: str
    text_auto: bool
    template: Optional[Any]
    width: Optional[Any]
    height: Optional[Any]
    animation_frame: Optional[Any]
    animation_group: Optional[Any]
    symbol: Optional[Any]
    symbol_map: Optional[Any]
    symbol_sequence: Optional[Any]
    render_mode: str
    line_dash: Optional[Any]
    line_dash_map: Optional[Any]
    line_dash_sequence: Optional[Any]
    line_group: Optional[Any]
    line_shape: Optional[Any]
    markers: bool
    hole: Optional[Any]
    size: Optional[Any]
    size_max: Optional[Any]
    marginal_x: Optional[Any]
    marginal_y: Optional[Any]
    trendline: Optional[Any]
    trendline_options: Optional[Any]
    trendline_scope: str
    trendline_color_override: Optional[Any]

    def __init__(
        self,
        title: Optional[str] = None,
        name: Optional[str] = None,
        plot_type: Optional[PlotType] = None,
        legend_x: str = "",
        legend_y: str = "",
        secondary_y: bool = False,
        color: Optional[str] = None,
        color_continuous_scale: Optional[Any] = None,
        color_continuous_midpoint: Optional[Any] = None,
        color_discrete_map: Optional[Any] = None,
        color_discrete_sequence: Optional[Any] = None,
        range_color: Optional[Any] = None,
        hover_name: Optional[Any] = None,
        hover_data: Optional[Any] = None,
        custom_data: Optional[Any] = None,
        text: Optional[Any] = None,
        facet_row: Optional[Any] = None,
        facet_col: Optional[Any] = None,
        facet_row_spacing: Optional[Any] = None,
        facet_col_spacing: Optional[Any] = None,
        facet_col_wrap: int = 0,
        error_x: Optional[Any] = None,
        error_y: Optional[Any] = None,
        error_x_minus: Optional[Any] = None,
        error_y_minus: Optional[Any] = None,
        category_orders: Optional[Any] = None,
        labels: Optional[Any] = None,
        orientation: Optional[Any] = None,
        opacity: Optional[Any] = None,
        log_x: bool = False,
        log_y: bool = False,
        range_x: Optional[Any] = None,
        range_y: Optional[Any] = None,
        pattern_shape: Optional[Any] = None,
        pattern_shape_map: Optional[Any] = None,
        pattern_shape_sequence: Optional[Any] = None,
        base: Optional[Any] = None,
        barmode: str = "relative",
        text_auto: bool = False,
        template: Optional[Any] = None,
        width: Optional[Any] = None,
        height: Optional[Any] = None,
        animation_frame: Optional[Any] = None,
        animation_group: Optional[Any] = None,
        symbol: Optional[Any] = None,
        symbol_map: Optional[Any] = None,
        symbol_sequence: Optional[Any] = None,
        render_mode: str = "auto",
        line_dash: Optional[Any] = None,
        line_dash_map: Optional[Any] = None,
        line_dash_sequence: Optional[Any] = None,
        line_group: Optional[Any] = None,
        line_shape: Optional[Any] = None,
        markers: bool = False,
        hole: Optional[Any] = None,
        size: Optional[Any] = None,
        size_max: Optional[Any] = None,
        marginal_x: Optional[Any] = None,
        marginal_y: Optional[Any] = None,
        trendline: Optional[Any] = None,
        trendline_options: Optional[Any] = None,
        trendline_scope: str = "trace",
        trendline_color_override: Optional[Any] = None,
    ):
        """Create Plot options.

        Args:
            title (Optional[str], optional): Title of the plot. Defaults to None.
            name (Optional[str], optional): Name of the series. Defaults to None.
            plot_type (Optional[PlotType], optional): TODO. Defaults to None.
            legend_x (str, optional): TODO. Defaults to "".
            legend_y (str, optional): TODO. Defaults to "".
            secondary_y (bool, optional): TODO. Defaults to False.
            color (Optional[str], optional): TODO. Defaults to None.
            color_continuous_scale (Optional[Any], optional): TODO. Defaults to None.
            color_continuous_midpoint (Optional[Any], optional): TODO. Defaults to None.
            color_discrete_map (Optional[Any], optional): TODO. Defaults to None.
            color_discrete_sequence (Optional[Any], optional): TODO. Defaults to None.
            range_color (Optional[Any], optional): TODO. Defaults to None.
            hover_name (Optional[Any], optional): TODO. Defaults to None.
            hover_data (Optional[Any], optional): TODO. Defaults to None.
            custom_data (Optional[Any], optional): TODO. Defaults to None.
            text (Optional[Any], optional): TODO. Defaults to None.
            facet_row (Optional[Any], optional): TODO. Defaults to None.
            facet_col (Optional[Any], optional): TODO. Defaults to None.
            facet_row_spacing (Optional[Any], optional): TODO. Defaults to None.
            facet_col_spacing (Optional[Any], optional): TODO. Defaults to None.
            facet_col_wrap (int, optional): TODO. Defaults to 0.
            error_x (Optional[Any], optional): TODO. Defaults to None.
            error_y (Optional[Any], optional): TODO. Defaults to None.
            error_x_minus (Optional[Any], optional): TODO. Defaults to None.
            error_y_minus (Optional[Any], optional): TODO. Defaults to None.
            category_orders (Optional[Any], optional): TODO. Defaults to None.
            labels (Optional[Any], optional): TODO. Defaults to None.
            orientation (Optional[Any], optional): TODO. Defaults to None.
            opacity (Optional[Any], optional): TODO. Defaults to None.
            log_x (bool, optional): TODO. Defaults to False.
            log_y (bool, optional): TODO. Defaults to False.
            range_x (Optional[Any], optional): TODO. Defaults to None.
            range_y (Optional[Any], optional): TODO. Defaults to None.
            pattern_shape (Optional[Any], optional): TODO. Defaults to None.
            pattern_shape_map (Optional[Any], optional): TODO. Defaults to None.
            pattern_shape_sequence (Optional[Any], optional): TODO. Defaults to None.
            base (Optional[Any], optional): TODO. Defaults to None.
            barmode (str, optional): TODO. Defaults to "relative".
            text_auto (bool, optional): TODO. Defaults to False.
            template (Optional[Any], optional): TODO. Defaults to None.
            width (Optional[Any], optional): TODO. Defaults to None.
            height (Optional[Any], optional): TODO. Defaults to None.
            animation_frame (Optional[Any], optional): TODO. Defaults to None.
            animation_group (Optional[Any], optional): TODO. Defaults to None.
            symbol (Optional[Any], optional): TODO. Defaults to None.
            symbol_map (Optional[Any], optional): TODO. Defaults to None.
            symbol_sequence (Optional[Any], optional): TODO. Defaults to None.
            render_mode (str, optional): TODO. Defaults to "auto".
            line_dash (Optional[Any], optional): TODO. Defaults to None.
            line_dash_map (Optional[Any], optional): TODO. Defaults to None.
            line_dash_sequence (Optional[Any], optional): TODO. Defaults to None.
            line_group (Optional[Any], optional): TODO. Defaults to None.
            line_shape (Optional[Any], optional): TODO. Defaults to None.
            markers (bool, optional): TODO. Defaults to False.
            hole (Optional[Any], optional): TODO. Defaults to None.
            size (Optional[Any], optional): TODO. Defaults to None.
            size_max (Optional[Any], optional): TODO. Defaults to None.
            marginal_x (Optional[Any], optional): TODO. Defaults to None.
            marginal_y (Optional[Any], optional): TODO. Defaults to None.
            trendline (Optional[Any], optional): TODO. Defaults to None.
            trendline_options (Optional[Any], optional): TODO. Defaults to None.
            trendline_scope (str, optional): TODO. Defaults to "trace".
            trendline_color_override (Optional[Any], optional): TODO. Defaults to None.
        """
        self.title = title
        self.name = name
        self.plot_type = plot_type
        self.legend_x = legend_x
        self.legend_y = legend_y
        self.secondary_y = secondary_y
        self.color = color
        self.color_continuous_scale = color_continuous_scale
        self.color_continuous_midpoint = color_continuous_midpoint
        self.color_discrete_map = color_discrete_map
        self.color_discrete_sequence = color_discrete_sequence
        self.range_color = range_color
        self.hover_name = hover_name
        self.hover_data = hover_data
        self.custom_data = custom_data
        self.text = text
        self.facet_row = facet_row
        self.facet_col = facet_col
        self.facet_row_spacing = facet_row_spacing
        self.facet_col_spacing = facet_col_spacing
        self.facet_col_wrap = facet_col_wrap
        self.error_x = error_x
        self.error_y = error_y
        self.error_x_minus = error_x_minus
        self.error_y_minus = error_y_minus
        self.category_orders = category_orders
        self.labels = labels
        self.orientation = orientation
        self.opacity = opacity
        self.log_x = log_x
        self.log_y = log_y
        self.range_x = range_x
        self.range_y = range_y
        self.pattern_shape = pattern_shape
        self.pattern_shape_map = pattern_shape_map
        self.pattern_shape_sequence = pattern_shape_sequence
        self.base = base
        self.barmode = barmode
        self.text_auto = text_auto
        self.template = template
        self.width = width
        self.height = height
        self.animation_frame = animation_frame
        self.animation_group = animation_group
        self.symbol = symbol
        self.symbol_map = symbol_map
        self.symbol_sequence = symbol_sequence
        self.render_mode = render_mode
        self.line_dash = line_dash
        self.line_dash_map = line_dash_map
        self.line_dash_sequence = line_dash_sequence
        self.line_group = line_group
        self.line_shape = line_shape
        self.markers = markers
        self.hole = hole
        self.size = size
        self.size_max = size_max
        self.marginal_x = marginal_x
        self.marginal_y = marginal_y
        self.trendline = trendline
        self.trendline_options = trendline_options
        self.trendline_scope = trendline_scope
        self.trendline_color_override = trendline_color_override

    @staticmethod
    def _from_yaml(params: Dict) -> "PlotOptions":
        if "series_color" in params:
            if "color_discrete_sequence" not in params:
                params["color_discrete_sequence"] = [params["series_color"]]
            del params["series_color"]
        options = PlotOptions()
        for key in params:
            options.__setattr__(key, params[key])

        return options


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
