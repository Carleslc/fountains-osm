from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.services.transform_fountains import transform_fountains_osm
from app.services.openstreetmap_api import OpenStreetMapAPI
from app.models.response import FountainsOpenStreetMapResponse
from app.api.params import AreaQueryParams, RadiusQueryParams, BboxQueryParams
from app.errors import ErrorResponse

router = APIRouter(
    prefix="/fountains",
    responses={
        408: { "description": "Request timed out", "model": ErrorResponse },
        502: { "description": "OpenStreetMap request error", "model": ErrorResponse }
    })

osm_api = OpenStreetMapAPI()

@router.get("/", response_model=FountainsOpenStreetMapResponse | Dict[str, Any])
def get_fountains_by_area(
    request: Request,
    params: AreaQueryParams = Depends(),
):
    """
    Find all fountains in an area.
    If area is not provided then the search is global (world).

    Parameters:
    - **area**: Search in a geographical region (geocode area: country, city, state...).
    - **updated**: Search only fountains updated since a specified datetime, in ISO 8601 format.
    - **raw**: Set to true to get the raw OSM data.
    - **osm**: Include OSM extra information (type, id, version, url, tags). Ignored if raw is true.
    - **timeout**: Timeout in seconds for the OSM API request (maximum 30 minutes).

    Returns:
    - JSON with fountains data either in raw OSM format or processed format.
    """
    if params.area:
        osm_data = osm_api.get_fountains_by_area(params.area,
                                                 updated=params.updated, timeout=params.timeout)
    else:
        osm_data = osm_api.get_fountains(updated=params.updated, timeout=params.timeout)

    return build_fountains_response(request, osm_data, params.raw, params.osm)

@router.get("/radius", response_model=FountainsOpenStreetMapResponse | Dict[str, Any])
def get_fountains_by_radius(
    request: Request,
    params: RadiusQueryParams = Depends(),
):
    """
    Find fountains around a center within a given radius.

    Parameters:
    - **lat**: Latitude of the center point.
    - **long**: Longitude of the center point.
    - **radius**: Radius in meters to search for fountains.
    - **updated**: Search only fountains updated since a specified datetime, in ISO 8601 format.
    - **raw**: Set to true to get the raw OSM data.
    - **osm**: Include OSM extra information (type, id, version, url, tags). Ignored if raw is true.
    - **timeout**: Timeout in seconds for the OSM API request (maximum 30 minutes).

    Returns:
    - JSON with fountains data either in raw OSM format or processed format.
    """
    osm_data = osm_api.get_fountains_by_radius(params.lat, params.long, params.radius,
                                               updated=params.updated, timeout=params.timeout)

    return build_fountains_response(request, osm_data, params.raw, params.osm)

@router.get("/bbox", response_model=FountainsOpenStreetMapResponse | Dict[str, Any])
def get_fountains_by_bbox(
    request: Request,
    params: BboxQueryParams = Depends(),
):
    """
    Find fountains within a bounding box.

    Parameters:
    - **south_lat**: South (minimum latitude) of the bounding box.
    - **west_long**: West (minimum longitude) of the bounding box.
    - **north_lat**: North (maximum latitude) of the bounding box.
    - **east_long**: East (maximum longitude) of the bounding box.
    - **updated**: Search only fountains updated since a specified datetime, in ISO 8601 format.
    - **raw**: Set to true to get the raw OSM data.
    - **osm**: Include OSM extra information (type, id, version, url, tags). Ignored if raw is true.
    - **timeout**: Timeout in seconds for the OSM API request (maximum 30 minutes).

    Returns:
    - JSON with fountains data either in raw OSM format or processed format.
    """
    osm_data = osm_api.get_fountains_by_bbox(params.south_lat, params.west_long, params.north_lat, params.east_long,
                                             updated=params.updated, timeout=params.timeout)

    return build_fountains_response(request, osm_data, params.raw, params.osm)


def build_fountains_response(request: Request, osm_data: Dict[str, Any], raw: bool, osm: bool) -> JSONResponse:
    if raw:
        return JSONResponse(content=osm_data)

    fountains = transform_fountains_osm(osm_data, osm)

    response = FountainsOpenStreetMapResponse(
        query_url=str(request.url),
        count=len(fountains),
        fountains=fountains
    )

    return JSONResponse(
        content=response.model_dump(
            mode='json',
            exclude_none=True,
            exclude={
                'fountains': {
                    '__all__': { 'provider_name' }
                }
            }
        )
    )
