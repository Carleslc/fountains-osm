# Fountains OpenStreetMap

Service to retrieve drinking water fountains from OpenStreetMap.

## API Service

### Development

#### Install

Install dependencies:
`pip install --user --upgrade -r requirements.txt`

Configure environment:
`cp .env.template .env`

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

- `osm=true`: Include OSM extra information (type, id, version, url, tags)
- `raw=true`: Get the raw OSM data as-is, without postprocessing
- `timeout`: Specify the OSM query timeout in seconds

#### Find fountains around a center within radius

`/fountains/radius?lat=41.391111&long=2.180556&radius=2000&osm=true`

#### Find fountains within a bounding box

`/fountains/bbox?south_lat=41.36792&west_long=2.098646&north_lat=41.42857&east_long=2.209196`

#### Find fountains within a geographical area

`/fountains?area=Spain`

#### Find all fountains in the world

`/fountains?timeout=1800`
