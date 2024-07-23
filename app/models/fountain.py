from typing import Any, Dict, Optional

from enum import Enum
from datetime import datetime

from pydantic import BaseModel

class FountainType(str, Enum):
    NATURAL = "natural"
    TAP_WATER = "tap_water"
    WATER_POINT = "water_point"
    WATERING_PLACE = "watering_place"

class SafeWater(str, Enum):
    YES = "yes"
    PROBABLY = "probably"
    NO = "no"

class LegalWater(str, Enum):
    TREATED = "treated"
    UNTREATED = "untreated"

class Access(str, Enum):
    YES = "yes"
    PERMISSIVE = "permissive"
    CUSTOMERS = "customers"
    PERMIT = "permit"
    PRIVATE = "private"
    NO = "no"
    UNKNOWN = "unknown"


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
    access: Optional[Access] = None
    fee: Optional[bool] = None
    address: Optional[str] = None
    website: Optional[str] = None
    provider_name: str
    provider_id: str
    provider_updated_at: datetime
    provider_url: Optional[str] = None


class FountainOpenStreetMap(Fountain):
    provider_name: str = "OpenStreetMap"
    osm: Optional['FountainOpenStreetMapInfo'] = None

class FountainOpenStreetMapInfo(BaseModel):
    type: str
    id: int
    version: int
    tags: Optional[Dict[str, Any]] = None
