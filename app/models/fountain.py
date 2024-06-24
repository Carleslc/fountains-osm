from typing import Any, Dict, Optional

from enum import Enum
from datetime import datetime

from pydantic import BaseModel

class FountainType(str, Enum):
    NATURAL = "natural"
    TAP_WATER = "tap_water"
    WATERING_PLACE = "watering_place"

class SafeWater(str, Enum):
    YES = "yes"
    PROBABLY = "probably"
    NO = "no"

class LegalWater(str, Enum):
    TREATED = "treated"
    UNTREATED = "untreated"


class Fountain(BaseModel):
    type: Optional[FountainType] = None
    lat: float
    long: float
    name: Optional[str] = None
    description: Optional[str] = None
    picture: Optional[str] = None
    operational_status: Optional[bool] = None
    safe_water: Optional[SafeWater] = None
    legal_water: Optional[LegalWater] = None
    access_bottles: Optional[bool] = None
    access_pets: Optional[bool] = None
    access_wheelchair: Optional[bool] = None
    provider_name: str
    provider_id: str
    updated_at: datetime # provider_updated_at


class FountainOpenStreetMap(Fountain):
    provider_name: str = "OpenStreetMap"
    osm: Optional['FountainOpenStreetMapInfo'] = None

class FountainOpenStreetMapInfo(BaseModel):
    type: str
    id: int
    version: int
    tags: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
