from typing import Any, List, Dict, Callable, Optional

from datetime import datetime

import os.path
import json
import typer
import requests

from rich.table import Table

from cli.utils import console, error, debug, debug_time, print_cancellable, batches, now, check_url_method, file_size, format_size

from app.models.fountain import FountainOpenStreetMap
from app.services.openstreetmap_api import OpenStreetMapAPI
from app.services.transform_fountains import transform_fountains_osm
from app.errors import RequestError

CLI_NAME = os.path.basename(__file__)
LOG_FILE = ".fountains_cli.log"
LOG_FILE_ENCODING = "utf8"
MAX_LOGS = 100
REQUEST_BATCH_SIZE = 1000

app = typer.Typer(context_settings={ "help_option_names": ["-h", "--help"] })

def fountains_filename(area: Optional[str], timestamp: datetime) -> str:
    timestamp_iso = timestamp.isoformat(timespec='seconds').replace('+00:00', 'Z')
    return f"fountains-{area or 'World'}-{timestamp_iso}.json"

def fountains_body(fountains: List[FountainOpenStreetMap]) -> List[Dict[str, Any]]:
    return [fountain.model_dump(mode='json', exclude_none=True) for fountain in fountains]

def save_fountains_to_file(fountains: List[FountainOpenStreetMap], filename: str):
    with open(filename, 'w', encoding=LOG_FILE_ENCODING) as f:
        json.dump(fountains_body(fountains), f, indent=4)
    console.print("Saved to file: ", end='')
    console.print(filename, style="file", highlight=False, end=' ')
    console.print(f"({format_size(file_size(filename))})", style="dim")

def post_fountains_to_url(request_type: str, request_method: Callable[..., requests.Response], fountains: List[FountainOpenStreetMap], endpoint_url: str, timeout: int):
    headers = { 'Content-Type': 'application/json' }

    i = 0

    for batch in batches(fountains, REQUEST_BATCH_SIZE):
        console.print(request_type, end=' ')
        console.print(endpoint_url, style="file", highlight=False, end=' ')
        console.print(f"{i} .. {min(i + REQUEST_BATCH_SIZE, len(fountains))}")

        response = request_method(endpoint_url, json=fountains_body(batch), headers=headers, timeout=timeout)

        console.print(f"{request_type} ({response.status_code})")
        response_body = response.json() if response.content else None
        print_response(response_body)

        response.raise_for_status()

        i += REQUEST_BATCH_SIZE

def print_response(response: Optional[str] = None):
    if response:
        console.print(response, style='debug')

def load_logs() -> List[Dict[str, Any]]:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding=LOG_FILE_ENCODING) as log_file:
            return json.load(log_file)
    return []

def log_request(logs: List[Dict[str, Any]],
                timestamp: datetime,
                area: Optional[str],
                since: Optional[datetime],
                osm: bool, timeout: int,
                post: Optional[str],
                put: Optional[str],
                request_time: float,
                post_time: float,
                count: int):
    log_entry = {
        "timestamp": timestamp.isoformat(),
        "since": since.isoformat() if since else None,
        "area": area,
        "osm": osm,
        "timeout": timeout,
        "post": post,
        "put": put,
        "request_time": request_time,
        "post_time": post_time,
        "count": count,
    }

    logs.append(log_entry)
    logs = logs[-MAX_LOGS:]

    with open(LOG_FILE, 'w', encoding=LOG_FILE_ENCODING) as log_file:
        json.dump(logs, log_file, indent=4)

def since_latest_log(logs: List[Dict[str, Any]], area: Optional[str],
                     post: Optional[str], put: Optional[str]) -> Optional[datetime]:
    parameter_area = area.lower() if area else None

    for log in reversed(logs): # logs are ordered by timestamp (ascending)
        log_area = log["area"].lower() if log.get("area") else None

        if log_area == parameter_area and (log.get("post") == post and log.get("put") == put):
            return datetime.fromisoformat(log["timestamp"]) # latest timestamp

    return None

def update_since(logs: List[Dict[str, Any]], since: Optional[datetime], area: Optional[str],
                 post: Optional[str], put: Optional[str]) -> Optional[datetime]:
    if since:
        debug(f"Update: --since {since.isoformat()} (explicitly specified)")
    else:
        since = since_latest_log(logs, area, post, put)

        if since:
            debug(f"Update: --since {since.isoformat()}")
        else:
            debug("Update: No matching logs for area")
    return since

@app.command(name="log", help="Show the log of previous requests. Alias: --logs")
@app.command(name="logs", hidden=True)
def show_log():
    """
    Show the log of previous requests.
    """
    def empty_log():
        console.print(f"[bold]Log is empty[/bold]\nUsage: python {CLI_NAME} --help")
        raise typer.Exit()

    if not os.path.exists(LOG_FILE):
        empty_log()

    with open(LOG_FILE, 'r', encoding=LOG_FILE_ENCODING) as log_file:
        logs = json.load(log_file)

        if not logs:
            empty_log()

        logs_table = Table()

        logs_table.add_column("Timestamp", justify="center", style="cyan", no_wrap=True)
        logs_table.add_column("Area --area", justify="center", style="magenta")
        logs_table.add_column("Updated --since", justify="center", style="bright_cyan")
        logs_table.add_column("Fountains", justify="center", style="bold green")
        logs_table.add_column("Timeout (s)", justify="center", style="blue")
        logs_table.add_column("OSM", justify="center", style="yellow")
        logs_table.add_column("Post/Put", justify="center", style="green")
        logs_table.add_column("API Time (s)", justify="center", style="cyan")
        logs_table.add_column("Post/Save Time (s)", justify="center", style="cyan")

        for log in logs:
            logs_table.add_row(
                log.get("timestamp"),
                log.get("area", ''),
                log.get("since", ''),
                str(log.get("count")),
                str(log.get("timeout")),
                str(log.get("osm")),
                log.get("post") or log.get("put"),
                f"{log.get("request_time"):.3f}",
                f"{log.get("post_time"):.3f}",
            )

        console.print(logs_table)

@app.callback(invoke_without_command=True)
def fetch_fountains(
    context: typer.Context,
    area: Optional[str] = typer.Option(None, help="Search in a geographical region (geocode area: country, city, state...). If not specified, all world data is retrieved."),
    since: Optional[datetime] = typer.Option(None, "--since", "--updated", help="Search only fountains updated since a specified datetime, in ISO 8601 format.", formats=["%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"]),
    update: bool = typer.Option(False, "--update", help="Set --since automatically from the latest log of --area"),
    osm: bool = typer.Option(False, "--osm", help="Include OSM extra information (type, id, version, url, tags)"),
    timeout: int = typer.Option(1800, help="Timeout in seconds for the OSM API request (default 30 minutes)"),
    post: Optional[str] = typer.Option(None, help="URL to POST the fountains data"),
    put: Optional[str] = typer.Option(None, help="URL to PUT the fountains data")
):
    """
    Fetch fountains data from OpenStreetMap and save to file or post to a url.
    """
    if context.invoked_subcommand is None: # main command (no subcommand)
        check_url: str | None = post or put

        if check_url:
            check_url_method(check_url, 'POST' if post else 'PUT')

        logs = load_logs()

        if update:
            since = update_since(logs, since, area, post, put)

        timestamp = now()

        try:
            osm_api = OpenStreetMapAPI(timeout=timeout)

            if area:
                print_cancellable(f"Fetching fountains in {area}...")
                osm_data = osm_api.get_fountains_by_area(area, updated=since, timeout=timeout)
            else:
                if not update:
                    typer.confirm("--area not specified. Do you want to retrieve all world fountains?", abort=True)
                print_cancellable("Fetching all fountains...")
                osm_data = osm_api.get_fountains(updated=since, timeout=timeout)

            request_timestamp, request_time = debug_time("OpenStreetMap API", timestamp)

            fountains = transform_fountains_osm(osm_data, osm)
        except RequestError as e:
            error(f"{e.detail} ({e.status_code})")

        processed_at, _ = debug_time("Transform", request_timestamp)

        fountains_count = len(fountains)

        console.print(f"Fountains found: {fountains_count}")

        try:
            if post:
                method = 'POST'
                post_fountains_to_url(method, requests.post, fountains, post, timeout)
            elif put:
                method = 'PUT'
                post_fountains_to_url(method, requests.put, fountains, put, timeout)
            else:
                method = 'Save'
                save_fountains_to_file(fountains, filename=fountains_filename(area, timestamp))
        except (IOError, requests.HTTPError) as e:
            error(str(e))

        _, post_time = debug_time(method, processed_at)

        log_request(logs, timestamp, area, since, osm, timeout, post, put, request_time, post_time, fountains_count)

if __name__ == "__main__":
    app()
