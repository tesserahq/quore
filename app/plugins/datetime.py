import time
from datetime import datetime, timezone
from fastmcp import FastMCP
from zoneinfo import ZoneInfo
from app.core.logging_config import get_logger
from llama_index.core.tools.function_tool import FunctionTool
from fastmcp import Context

logger = get_logger()
plugin_app = FastMCP("datetime")


@plugin_app.tool()
def format_datetime(format_type: str) -> str:
    """Format the current date and time according to the specified format type.

    Parameters:
        format_type (str): The type of format to use. Available formats:
            - date: 2024-12-10
            - date_slash: 2024/12/10
            - date_jp: 2024年12月10日
            - datetime: 2024-12-10 00:54:01
            - datetime_jp: 2024年12月10日 00時54分01秒
            - datetime_t: 2024-12-10T00:54:01
            - compact: 20241210005401
            - compact_date: 20241210
            - compact_time: 005401
            - filename_md: 20241210005401.md
            - filename_txt: 20241210005401.txt
            - filename_log: 20241210005401.log
            - iso: 2024-12-10T00:54:01+0900
            - iso_basic: 20241210T005401+0900
            - log: 2024-12-10 00:54:01.123456
            - log_compact: 20241210_005401
            - time: 00:54:01
            - time_jp: 00時54分01秒

    Returns:
        str: The formatted date and time string.

    Raises:
        ValueError: If the format_type is not recognized.
        RuntimeError: If there is an error formatting the date.
    """
    # Generate a new time object each time, considering timezone
    current_time = datetime.now(timezone.utc).astimezone()
    formats = {
        # Basic date formats
        "date": "%Y-%m-%d",  # 2024-12-10
        "date_slash": "%Y/%m/%d",  # 2024/12/10
        # Basic datetime formats
        "datetime": "%Y-%m-%d %H:%M:%S",  # 2024-12-10 00:54:01
        "datetime_t": "%Y-%m-%dT%H:%M:%S",  # 2024-12-10T00:54:01
        # Compact formats for filenames or IDs
        "compact": "%Y%m%d%H%M%S",  # 20241210005401
        "compact_date": "%Y%m%d",  # 20241210
        "compact_time": "%H%M%S",  # 005401
        # Filename formats
        "filename_md": "%Y%m%d%H%M%S.md",  # 20241210005401.md
        "filename_txt": "%Y%m%d%H%M%S.txt",  # 20241210005401.txt
        "filename_log": "%Y%m%d%H%M%S.log",  # 20241210005401.log
        # ISO 8601 formats
        "iso": "%Y-%m-%dT%H:%M:%S%z",  # 2024-12-10T00:54:01+0900
        "iso_basic": "%Y%m%dT%H%M%S%z",  # 20241210T005401+0900
        # Log formats
        "log": "%Y-%m-%d %H:%M:%S.%f",  # 2024-12-10 00:54:01.123456
        "log_compact": "%Y%m%d_%H%M%S",  # 20241210_005401
        # Time-only formats
        "time": "%H:%M:%S",  # 00:54:01
    }

    if format_type not in formats:
        raise ValueError(f"Unknown format type: {format_type}")

    try:
        return current_time.strftime(formats[format_type])
    except Exception as e:
        logger.error("Format error: %s", str(e))
        raise RuntimeError(f"Error formatting date: {str(e)}") from e


@plugin_app.tool()
def get_datetime(tz_name="UTC") -> str:
    """Get the current date and time in 'YYYY-MM-DD HH:MM:SS' format for the specified timezone.

    Parameters:
      tz_name (str): A timezone name in IANA format (e.g., 'UTC', 'America/New_York', 'Europe/Paris').
                     Defaults to 'UTC'.

    Returns:
      str: The formatted date and time.
    """
    current_time = datetime.now(ZoneInfo(tz_name))
    return current_time.strftime("%Y-%m-%d %H:%M:%S")


def get_current_unix_timestamp() -> float:
    """
    Return the current Unix timestamp.

    The Unix timestamp represents the number of seconds that have elapsed since
    January 1, 1970 (UTC).

    Returns:
        float: The current Unix timestamp.
    """

    return time.time()


def get_tools():
    return [
        FunctionTool.from_defaults(format_datetime),
        FunctionTool.from_defaults(get_datetime),
        FunctionTool.from_defaults(get_current_unix_timestamp),
    ]
