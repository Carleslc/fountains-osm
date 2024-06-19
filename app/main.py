"""
App entrypoint
"""

from typing import Any, Dict

from fastapi import FastAPI

from app.api import fountains
from app.config import load_config, APP_NAME
from app.services.openstreetmap_api import API_URL
from app.errors import RequestError, request_error_handler

load_config()

app = FastAPI(
    title=APP_NAME,
    version='1.0',
    description="Service to retrieve fountains from OpenStreetMap."
)

app.include_router(fountains.router, tags=["fountains"])

app.add_exception_handler(RequestError, request_error_handler) # type: ignore

INFO = {
        "title": APP_NAME,
        "version": app.version,
        "description": app.description,
        "docs": "/docs",
        "github": "https://github.com/Carleslc/fountains-osm",
        "osm": {
            "web": "https://www.openstreetmap.org/",
            "testing": "https://overpass-turbo.eu/",
            "api": API_URL,
        },
        "examples": {
            "Find fountains around a center within a given radius": [
                "/fountains/radius?lat=41.391111&long=2.180556&radius=2000",
                "/fountains/radius?lat=41.391111&long=2.180556&radius=2000&osm=true",
                "/fountains/radius?lat=41.391111&long=2.180556&radius=2000&raw=true",
            ],
            "Find fountains within a bounding box": [
                "/fountains/bbox?south_lat=41.36792&west_long=2.098646&north_lat=41.42857&east_long=2.209196",
                "/fountains/bbox?south_lat=41.36792&west_long=2.098646&north_lat=41.42857&east_long=2.209196&osm=true",
                "/fountains/bbox?south_lat=41.36792&west_long=2.098646&north_lat=41.42857&east_long=2.209196&raw=true",
            ],
            "Find all fountains in a geographical area": [
                "/fountains?area=Barcelona",
                "/fountains?area=Spain",
                "/fountains?area=Spain&raw=true",
            ],
            "Find all fountains in the world": [
                "/fountains?timeout=1800",
                "/fountains?timeout=1200&raw=true",
            ],
            "Find updated fountains since a specified date and time": [
                "/fountains/bbox?updated=2024-01-01T00:00:00%2B00:00&south_lat=41.36792&west_long=2.098646&north_lat=41.42857&east_long=2.209196",
                "/fountains?updated=2024-06-15T00:00:00Z&timeout=1800",
            ]
        }
    }

@app.get("/", responses={
    200: {
        "content": {
            "application/json": {
                "example": INFO
            }
        }
    }
})
async def get_root() -> Dict[str, Any]:
    """
    Get useful information of this API.
    """
    return INFO
