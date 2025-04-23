from colors import color
from typing import Optional

from .types import LogLevel


level: LogLevel = LogLevel.warning


def log(
    message: str,
    log_level: LogLevel = LogLevel.debug,
    fg_color: Optional[int | str] = None,
    bg_color: Optional[int | str] = None,
    style: Optional[str] = None,
):
    """Print a log message if the log level is set at least as high as the message.

    Args:
        message (str): The log message
        log_level (LogLevel, optional): Minimum log level to filter. Defaults to LogLevel.debug.
        fg_color (Optional[int | str], optional): Optional text foreground color. Defaults to None.
        bg_color (Optional[int | str], optional): Optional text background color. _description_. Defaults to None.
        style (Optional[str], optional): Optional text style. Defaults to None.
    """
    if level >= log_level:
        print(color(message, fg=fg_color, bg=bg_color, style=style))
