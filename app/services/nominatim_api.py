"""
Geocoding to request OpenStreetMap areas using Nominatim API
"""

from geopy.location import Location
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from app.config import APP_NAME
from app.errors import RequestTimeoutError, OpenStreetMapError

class NominatimAPI:
    """
    Geocoding Nominatim API wrapper
    https://wiki.openstreetmap.org/wiki/Nominatim
    """

    api: Nominatim

    def __init__(self, timeout: int = 10):
        self.api = Nominatim(user_agent=APP_NAME, timeout=timeout) # type: ignore

    def find_area_id(self, geocode_area: str) -> int | None:
        try:
            geocoding_result: Location | None = self.api.geocode(geocode_area, timeout=self.api.timeout) # type: ignore
        except GeocoderTimedOut as e:
            raise RequestTimeoutError(f"Geocoding request timed out after {self.api.timeout} seconds") from e
        except GeocoderServiceError as e:
            raise OpenStreetMapError(f"Geocoding request error: {repr(e)}") from e

        if geocoding_result is None:
            return None

        area_id = int(geocoding_result.raw["osm_id"]) + 3600000000 # relation id to area id

        return area_id
