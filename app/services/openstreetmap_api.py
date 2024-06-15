"""
Request fountains in OpenStreetMap using Overpass API
"""

import re
import overpass

from app.services.nominatim_api import NominatimAPI
from app.errors import RequestTimeoutError, OpenStreetMapError

from app.config import logger

API_URL = "https://overpass-api.de/"
API_ENDPOINT = f'{API_URL}/api/interpreter'

FOUNTAIN_QUERY_TEMPLATE_FILE = 'queries/fountains-query-template.overpassql'

class OpenStreetMapAPI:
    """
    API to request fountains in OpenStreetMap
    """

    overpass_api: overpass.API
    """
    Overpass API wrapper
    https://wiki.openstreetmap.org/wiki/Overpass_API
    https://github.com/mvexel/overpass-api-python-wrapper
    """

    _geocoding_api: NominatimAPI | None = None
    """
    Geocoding API wrapper (lazy attribute)
    """

    _fountains_query_template: str
    """
    OverpassQL query template to look for fountains given different region parameters
    """

    def __init__(self, timeout: int = 1800):
        self.overpass_api = overpass.API(endpoint=API_ENDPOINT, timeout=timeout)

        self.__load_query_templates()
    
    @property
    def geocoding_api(self):
        """
        Geocoding API wrapper
        """
        if self._geocoding_api is None:
            self._geocoding_api = NominatimAPI()
        
        return self._geocoding_api

    def __load_query_templates(self):
        self._fountains_query_template = _load_query_template(FOUNTAIN_QUERY_TEMPLATE_FILE)

    def get_fountains(self, timeout: int = 1200) -> dict:
        logger.info('fountains timeout=%s', timeout)

        return self.__get_fountains_with_query(timeout)

    def get_fountains_by_area(self, area: str, timeout: int = 60) -> dict:
        area_id = self.geocoding_api.find_area_id(area)

        logger.info('fountains_by_area %s %s', area, area_id)

        return self.__get_fountains_with_query(timeout,
                                               bbox='area.searchArea',
                                               area_id=f'area(id:{area_id})->.searchArea;')

    def get_fountains_by_radius(self, lat: float, long: float, radius: int, timeout: int = 20) -> dict:
        logger.info('fountains_by_radius %(radius)s around %(lat)s,%(long)s', { 'radius': radius, 'lat': lat, 'long': long })

        return self.__get_fountains_with_query(timeout, bbox=f'around:{radius},{lat},{long}')

    def get_fountains_by_bbox(self, south_lat: float, west_long: float, north_lat: float, east_long: float, timeout: int = 30) -> dict:
        bbox = f'{south_lat},{west_long},{north_lat},{east_long}'

        logger.info('fountains_by_bbox bbox %s', bbox)

        return self.__get_fountains_with_query(timeout, bbox)

    def __get_fountains_with_query(self, timeout: int, bbox: str = '', area_id: str = '') -> dict: # json
        fountains_query = self._fountains_query_template.format(
            timeout=str(timeout),
            area_id=area_id,
            bbox=f'({bbox})' if bbox else ''
        )

        logger.debug(fountains_query)

        try:
            result = self.overpass_api.get(fountains_query, responseformat='json', build=False)
        except overpass.errors.TimeoutError as e:
            raise RequestTimeoutError(f"Overpass request timed out after {self.overpass_api.timeout} seconds") from e
        except overpass.errors.ServerLoadError as e:
            server_load_error = (
                "The Overpass server is currently under load and declined the request.\n"
                f"Try again later or retry with reduced timeout value (< {timeout})."
            )
            raise RequestTimeoutError(server_load_error) from e
        except overpass.errors.MultipleRequestsError as e:
            raise OpenStreetMapError("You are trying to run multiple requests at the same time") from e
        except (overpass.errors.ServerRuntimeError, overpass.errors.UnknownOverpassError) as e:
            raise OpenStreetMapError(e.message) from e

        return result # type: ignore


def _load_query_template(query_template_file_path: str):
    def clean_query_template(query_template: str):
        # Remove comments (lines starting with // after optional whitespace)
        query_template = re.sub(r'^\s*//.*$', '', query_template, flags=re.MULTILINE)

        # Remove empty lines and leading or trailing whitespace
        query_template = '\n'.join([line.strip() for line in query_template.splitlines() if line.strip() != ''])

        return query_template

    with open(query_template_file_path, 'r', encoding='utf8') as query_template_file:
        return clean_query_template(query_template_file.read())
