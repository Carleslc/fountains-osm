# Fountains OpenStreetMap

Service to retrieve drinking water fountains from OpenStreetMap.

## Install

Install dependencies:
`pip install --user --upgrade -r requirements.txt`

Configure environment:
`cp .env.template .env`

## API Service

### Development

Run: `fastapi dev app/main.py`

**Endpoint**: http://127.0.0.1:8000

### Production

Run: `fastapi run app/main.py --workers 2`

Using Docker:

```bash
docker compose up --build -d

docker logs -f fountains-osm

docker compose down
```

https://fastapi.tiangolo.com/deployment/docker

### Queries

Docs: `http://127.0.0.1:8000/docs`
Examples: `http://127.0.0.1:8000/`

Special parameters:

- `osm=true`: Include OSM extra information (type, id, version, url, tags).
- `raw=true`: Get the raw OSM data as-is, without postprocessing.
- `timeout`: Specify the OSM query timeout in seconds.
- `updated`: Search only fountains updated since a specified datetime, in ISO 8601 format.

#### Find fountains around a center within radius

`/fountains/radius?lat=41.391111&long=2.180556&radius=2000&osm=true`

#### Find fountains within a bounding box

`/fountains/bbox?south_lat=41.36792&west_long=2.098646&north_lat=41.42857&east_long=2.209196`

#### Find fountains within a geographical area

`/fountains?area=Spain`

#### Find all fountains in the world

`/fountains?timeout=1800`

#### Find updated fountains since a specified date and time

All: `/fountains?updated=2024-06-15T00:00:00Z&timeout=1800`

Within a bounding box: `/fountains/bbox?updated=2024-01-01T00:00:00+00:00&south_lat=41.36792&west_long=2.098646&north_lat=41.42857&east_long=2.209196`

## CLI

### Usage

`python fountains_cli.py --help`

```
Usage: fountains_cli.py [OPTIONS] COMMAND [ARGS]...                                                                                                            
                                                                                                                                                                
 Fetch fountains data from OpenStreetMap and save to file or post to a url.                                                                                     
                                                                                                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --area                        TEXT                                                           Search in a geographical region (geocode area: country, city,   │
│                                                                                              state...). If not specified, all world data is retrieved.       │
│                                                                                              [default: None]                                                 │
│ --since,--updated             [%d/%m/%Y|%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%dT%H:%M:%S.%f|%Y-  Search only fountains updated since a specified datetime, in    │
│                               %m-%dT%H:%M:%S%z|%Y-%m-%dT%H:%M:%S.%f%z]                       ISO 8601 format.                                                │
│                                                                                              [default: None]                                                 │
│ --update                                                                                     Set --since automatically from the latest log of --area         │
│ --osm                                                                                        Include OSM extra information (type, id, version, url, tags)    │
│ --timeout                     INTEGER                                                        Timeout in seconds for the OSM API request (maximum 30 minutes) │
│                                                                                              [default: 1800]                                                 │
│ --post                        TEXT                                                           URL to POST the fountains data [default: None]                  │
│ --put                         TEXT                                                           URL to PUT the fountains data [default: None]                   │
│ --install-completion                                                                         Install completion for the current shell.                       │
│ --show-completion                                                                            Show completion for the current shell, to copy it or customize  │
│                                                                                              the installation.                                               │
│ --help                -h                                                                     Show this message and exit.                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ log   Show the log of previous requests. Alias: --logs                                                                                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### Save fountains data to a file

Download all fountains in the selected area:

```sh
python fountains_cli.py --area "Barcelona"
```

Download all fountains in the world from OpenStreetMap:

```sh
python fountains_cli.py
```

#### Send fountains data to an external endpoint

Upload all fountains in the selected area with a POST or PUT request to the specified endpoint.

```sh
python fountains_cli.py --area "Spain" --post "https://endpoint-url.com/fountains"
python fountains_cli.py --area "Spain" --put "https://endpoint-url.com/fountains"
```

#### Update fountains from latest log

Download updated fountains since the latest request of the selected area:

```sh
python fountains_cli.py --update
python fountains_cli.py --update --area "Barcelona"
python fountains_cli.py --update --area "Spain" --put "https://endpoint-url.com/fountains"
```

#### See logs of previous requests

```sh
python fountains_cli.py logs
```
