from typing import Any, Dict, List, Literal, Optional

import re

from datetime import datetime

from app.errors import RequestTimeoutError, OpenStreetMapError
from app.models.fountain import FountainOpenStreetMap, FountainOpenStreetMapInfo, FountainType, SafeWater, LegalWater

def determine_type(tags: Dict[str, str]) -> Optional[FountainType]:
    if tags.get('natural') == 'spring':
        return FountainType.NATURAL
    if tags.get('man_made') == 'water_tap':
        return FountainType.TAP_WATER
    if tags.get('amenity') == 'drinking_water':
        return FountainType.TAP_WATER
    if tags.get('amenity') == 'watering_place':
        return FountainType.WATERING_PLACE
    return None

def determine_operational_status(status: Optional[str]) -> Optional[bool]:
    if not status:
        return None
    operational_status_map = {
        "ok": True, "yes": True, "operational": True, "functional": True, "open": True,
        "non-operational": False, "broken": False, "closed": False, "out_of_order": False, "needs_maintenance": False
    }
    return operational_status_map.get(status)

def determine_safe_water(tags: Dict[str, str]) -> Optional[SafeWater]:
    if tags.get('amenity') == 'drinking_water' or tags.get('drinking_water:legal') == "yes" or tags.get('drinking_water') == "treated":
        return SafeWater.YES
    if tags.get('drinking_water') == "yes":
        return SafeWater.PROBABLY
    if tags.get('drinking_water') == "no":
        return SafeWater.NO
    return None

def determine_legal_water(tags: Dict[str, str]) -> Optional[LegalWater]:
    if tags.get('drinking_water:legal') == "yes" or tags.get('drinking_water') == "treated":
        return LegalWater.TREATED
    if tags.get('drinking_water:legal') == "no" or tags.get('drinking_water') == "untreated":
        return LegalWater.UNTREATED
    return None

def determine_access_bottles(tags: Dict[str, str]) -> Optional[bool]:
    if 'bottle' in tags:
        return tags['bottle'] == "yes"
    return None

def determine_access_pets(tags: Dict[str, str]) -> Optional[bool]:
    if 'dog' in tags:
        return tags['dog'] == "yes"
    if tags.get('amenity') == "watering_place":
        return True
    return None

def determine_access_wheelchair(tags: Dict[str, str]) -> Optional[bool]:
    if 'wheelchair' in tags:
        return tags['wheelchair'] == "yes"
    return None

def determine_description(tags: Dict[str, str]) -> Optional[str]:
    if 'description' in tags:
        return tags['description']
    if 'description:en' in tags:
        return tags['description:en']
    for key, value in tags.items():
        if key.startswith('description'):
            return value
    if 'note' in tags:
        return tags['note']
    if 'wikipedia' in tags:
        wiki_url = osm_tag_to_wikipedia_url(tags['wikipedia'])
        if wiki_url:
            return wiki_url
    if 'source' in tags and is_url(tags['source']):
        return tags['source']
    if 'operator' in tags:
        return tags['operator']
    return None

def osm_tag_to_wikipedia_url(tag: str) -> Optional[str]:
    if ':' not in tag:
        return None
    language_code, page_name = tag.split(':', 1)
    page_name = page_name.replace(' ', '_')
    return f"https://{language_code}.wikipedia.org/wiki/{page_name}"

def is_url(value: str) -> bool:
    return value.startswith('http') # fast check

def osm_url(osm_type: Literal["node", "way", "relation"], osm_id: str) -> str:
    return f"https://www.openstreetmap.org/{osm_type}/{osm_id}"

def transform_fountains_osm(osm_data: Dict[str, Any], include_osm: bool = False) -> List[FountainOpenStreetMap]:
    check_osm_errors(osm_data)

    try:
        transformed_data = []

        for element in osm_data.get("elements", []):
            element_type = element["type"]
            element_id = element["id"]

            if element_type == "node":
                lat, lon = element["lat"], element["lon"]
            else: # "way" or "relation"
                lat, lon = element["center"]["lat"], element["center"]["lon"]

            tags = element.get("tags", {})

            fountain = FountainOpenStreetMap.model_construct( # without validation: trusted data source (x30 faster)
                type=determine_type(tags),
                lat=lat,
                long=lon,
                name=tags.get("name"),
                picture=tags.get("image"),
                description=determine_description(tags),
                operational_status=determine_operational_status(tags.get("operational_status")),
                safe_water=determine_safe_water(tags),
                legal_water=determine_legal_water(tags),
                access_bottles=determine_access_bottles(tags),
                access_pets=determine_access_pets(tags),
                access_wheelchair=determine_access_wheelchair(tags),
                provider_id=f'{element_type}:{element_id}',
                updated_at=datetime.fromisoformat(element["timestamp"]), # before python 3.11: replace('Z', '+00:00')
            )

            if include_osm:
                fountain.osm = FountainOpenStreetMapInfo.model_construct(
                    type=element_type,
                    id=element_id,
                    version=element["version"],
                    tags=tags,
                    url=osm_url(element_type, element_id),
                )

            transformed_data.append(fountain)

        return transformed_data
    except (KeyError, ValueError) as e:
        raise OpenStreetMapError("Invalid OpenStreetMap response data") from e

def check_osm_errors(osm_data: Dict[str, Any]):
    error_message: str | None = osm_data.get("remark")

    if error_message:
        if error_message.startswith("runtime error"):
            error_message = error_message.split("runtime error: ", 1)[1]

            if error_message.startswith("Query timed out"):
                error_message = re.sub(r'in "query" at line \d+ ', '', error_message)

                raise RequestTimeoutError(error_message)

        raise OpenStreetMapError(error_message)
