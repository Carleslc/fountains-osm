from typing import Optional
from typing_extensions import Annotated

from dataclasses import dataclass

from datetime import datetime

from fastapi import Query

Timeout = Annotated[int, Query(description="Timeout in seconds for the OSM API request (maximum 30 minutes)", le=1800)]

@dataclass
class AreaQueryParamsBase:
    area: Annotated[Optional[str], Query(description="Search in a geographical region (geocode area: country, city, state...)")] = None

@dataclass
class RadiusQueryParamsBase:
    lat: Annotated[float, Query(description="Latitude of the center point")]
    long: Annotated[float, Query(description="Longitude of the center point")]
    radius: Annotated[int, Query(description="Radius in meters to search for fountains")]

@dataclass
class BboxQueryParamsBase:
    south_lat: Annotated[float, Query(description="South (minimum latitude) of the bounding box")]
    west_long: Annotated[float, Query(description="West (minimum longitude) of the bounding box")]
    north_lat: Annotated[float, Query(description="North (maximum latitude) of the bounding box")]
    east_long: Annotated[float, Query(description="East (maximum longitude) of the bounding box")]

@dataclass
class CommonQueryParams:
    updated: Annotated[datetime | None, Query(description="Search only fountains updated since a specified datetime, in ISO 8601 format", alias="since")] = None
    raw: Annotated[bool, Query(description="Set to true to get the raw OSM data")] = False
    osm: Annotated[bool, Query(description="Include OSM extra information (type, id, version, url, tags). Ignored if raw is true")] = False
    timeout: Timeout = 60

@dataclass(kw_only=True)
class AreaQueryParams(CommonQueryParams, AreaQueryParamsBase):
    ...

@dataclass(kw_only=True)
class RadiusQueryParams(CommonQueryParams, RadiusQueryParamsBase):
    timeout: Timeout = 20

@dataclass(kw_only=True)
class BboxQueryParams(CommonQueryParams, BboxQueryParamsBase):
    timeout: Timeout = 30
