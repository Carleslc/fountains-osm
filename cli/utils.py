from typing import Any, List, Tuple, Generator, Optional

from datetime import datetime, timezone

import math
import os.path
import requests
import typer

from rich.console import Console
from rich.theme import Theme

theme = Theme({
    "debug": "dim",
    "file": "grey50"
})
console = Console(theme=theme)
err_console = Console(stderr=True, theme=Theme({ "error": "bold red" }), style='error')

def now() -> datetime:
    return datetime.now(timezone.utc)

def error(message: str):
    err_console.print(f"ERROR: {message}")
    raise typer.Exit(code=1)

def debug(message: Any, highlight: bool = False):
    console.print(message, style="debug", highlight=highlight)

def print_cancellable(message: str, style: Optional[str] = None):
    console.print(f"{message} [dim](Ctrl^C to cancel)[/dim]", style=style)

def debug_time(time_name: str, start_timestamp: datetime) -> Tuple[datetime, float]:
    current_timestamp = now()
    total_seconds_elapsed = seconds_elapsed = (current_timestamp - start_timestamp).total_seconds()
    time_message = f"{time_name} Time: "
    if seconds_elapsed > 60:
        minutes_elapsed = int(seconds_elapsed // 60)
        seconds_elapsed -= minutes_elapsed * 60
        time_message += f"{minutes_elapsed} minutes and "
    time_message += f"{seconds_elapsed:.2g} seconds"
    debug(time_message, highlight=True)
    return current_timestamp, total_seconds_elapsed

def check_url_method(url: str, method: str = 'POST'):
    try:
        options = requests.options(url, timeout=10)

        if options.status_code in [200, 204]:
            allow_header = options.headers.get('Allow') or options.headers.get('Access-Control-Allow-Methods')

            if allow_header:
                allowed_methods = [method.strip() for method in allow_header.split(',')]

                if method not in allowed_methods:
                    error(f"{method} not allowed for URL {url}")
            
            # Assume method is allowed if successful response but Allow header is not present
        else:
            error(f"{method} not allowed for URL {url} ({options.status_code})")
    except requests.ConnectionError:
        error(f"Invalid URL {url} (Connection Error)")
    except requests.RequestException as e:
        error(f"Invalid URL {url}: {str(e)}")

def format_size(size_bytes: float) -> str:
    if size_bytes == 0:
        return "0B"
    size_units = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    size = round(size_bytes / p, 2)
    return f"{size:g} {size_units[i]}"

def file_size(file_path: str) -> float:
    return os.path.getsize(file_path)

def batches(l: List[Any], size: int) -> Generator[Tuple[int, int, List[Any]], None, None]:
    """Yield successive chunks of a specific size for list l."""
    len_l = len(l)
    for i in range(0, len_l, size):
        start_index = i
        end_index = min(i + size, len_l)
        yield start_index, end_index, l[start_index:end_index]
