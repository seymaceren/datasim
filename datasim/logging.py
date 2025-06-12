from sys import stdout
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
    world=None,
    include_timestamp: bool = True,
):
    """Print a log message if the log level is set at least as high as the message.

    Args:
        message (str): The log message
        log_level (LogLevel, optional): Minimum log level to filter. Defaults to LogLevel.debug.
        fg_color (Optional[int | str], optional): Optional text foreground color. Defaults to None.
        bg_color (Optional[int | str], optional): Optional text background color. _description_. Defaults to None.
        style (Optional[str], optional): Optional text style. Defaults to None.
        include_timestamp (bool, optional): Whether to include the timestamp before the message. Defaults to True.
    """
    if level >= log_level:
        formatted = (
            f"[{world.index}:{world.time}] {message}\n"
            if world and include_timestamp
            else f"{message}\n"
        )
        print(
            color(
                formatted,
                fg=fg_color,
                bg=bg_color,
                style=style,
            ),
            end="",
        )
        from .runner import Runner

        Runner.complete_log = Runner.complete_log + formatted
        stdout.flush()
