from typing import Any, Dict, List, Literal, Optional

import re

from datetime import datetime

from app.errors import RequestTimeoutError, OpenStreetMapError
from app.models.fountain import FountainOpenStreetMap, FountainOpenStreetMapInfo, FountainType, SafeWater, LegalWater, Access

def determine_type(tags: Dict[str, str]) -> Optional[FountainType]:
    if tags.get('natural') == 'spring':
        return FountainType.NATURAL
    amenity = tags.get('amenity')
    if amenity == 'drinking_water':
        return FountainType.TAP_WATER
    if amenity == 'watering_place':
        return FountainType.WATERING_PLACE
    if amenity == 'water_point' or tags.get('waterway') == 'water_point':
        return FountainType.WATER_POINT
    if tags.get('man_made') == 'water_tap':
        return FountainType.TAP_WATER
    return None

def determine_name(tags: Dict[str, str]) -> Optional[str]:
    name = tags.get('name') or tags.get('name:en') or tags.get('name:es')
    if name:
        return name
    for key, value in tags.items():
        if key.startswith('name:'):
            return value
    return None

def determine_picture(tags: Dict[str, str]) -> Optional[str]:
    if 'image' in tags and is_url(tags['image']):
        return tags['image']
    return None

__OPERATIONAL_STATUS_MAP = {
    "ok": True, "yes": True, "operational": True, "functional": True, "open": True,
    "non-operational": False, "broken": False, "closed": False, "out_of_order": False, "needs_maintenance": False
}

def determine_operational_status(tags: Dict[str, str]) -> Optional[bool]:
    status = tags.get('operational_status')
    return __OPERATIONAL_STATUS_MAP.get(status) if status else None

def determine_safe_water(tags: Dict[str, str]) -> Optional[SafeWater]:
    drinking_water = tags.get('drinking_water')
    if drinking_water == "no":
        return SafeWater.NO
    amenity = tags.get('amenity')
    if amenity == 'drinking_water' or drinking_water == "treated" or tags.get('drinking_water:legal') == "yes":
        return SafeWater.YES
    if amenity == 'water_point' or drinking_water in ("yes", "conditional"):
        return SafeWater.PROBABLY
    return None

def determine_legal_water(tags: Dict[str, str]) -> Optional[LegalWater]:
    drinking_water = tags.get('drinking_water')
    drinking_water_legal = tags.get('drinking_water:legal')
    if drinking_water_legal == "yes" or drinking_water == "treated":
        return LegalWater.TREATED
    if drinking_water_legal == "no" or drinking_water == "untreated":
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
        if key.startswith('description:'):
            return value
    if 'note' in tags:
        return tags['note']
    if 'drive_water:description' in tags:
        return tags['drive_water:description']
    if 'operator' in tags:
        return tags['operator']
    return None

def determine_address(tags: Dict[str, str]) -> Optional[str]:
    address_parts = []
    if 'addr:street' in tags:
        street = tags['addr:street']
        if 'addr:suburb' in tags:
            street += f" ({tags['addr:suburb']})"
        if 'addr:streetnumber' in tags:
            street += ' ' + tags['addr:streetnumber']
        address_parts.append(street)
    if 'addr:housename' in tags:
        address_parts.append(tags['addr:housename'])
    if 'addr:floor' in tags:
        address_parts.append(tags['addr:floor'])
    if 'addr:housenumber' in tags:
        address_parts.append(tags['addr:housenumber'])
    if 'addr:hamlet' in tags:
        address_parts.append(tags['addr:hamlet'])
    if 'addr:district' in tags:
        district = tags['addr:district']
        if 'addr:subdistrict' in tags:
            district += f" ({tags['addr:subdistrict']})"
        address_parts.append(district)
    if 'addr:city' in tags:
        city = tags['addr:city']
        if 'addr:postcode' in tags:
            city += f' ({tags['addr:postcode']})'
        address_parts.append(city)
    if 'addr:province' in tags:
        address_parts.append(tags['addr:province'])
    if 'addr:state' in tags:
        address_parts.append(tags['addr:state'])
    if 'addr:country' in tags:
        address_parts.append(tags['addr:country'])
    return ', '.join(address_parts) if address_parts else None

def determine_access(tags: Dict[str, str]) -> Optional[Access]:
    if 'access' in tags:
        access = tags['access']
        if access in ('yes', 'public'):
            return Access.YES
        if access == 'permissive':
            return Access.PERMISSIVE
        if access == 'customers':
            return Access.CUSTOMERS
        if access == 'permit':
            return Access.PERMIT
        if access in ('private', 'military'):
            return Access.PRIVATE
        if access == 'no':
            return Access.NO
        if access == 'unknown':
            return Access.UNKNOWN
    return None

def determine_fee(tags: Dict[str, str]) -> Optional[bool]:
    if 'fee' in tags:
        fee = tags['fee']
        if fee != "unknown":
            return fee == "yes"
    return None

def determine_website(tags: Dict[str, str]) -> Optional[str]:
    if 'website' in tags and is_url(tags['website']):
        return tags['website']
    if 'wikipedia' in tags:
        wiki_url = osm_tag_to_wikipedia_url(tags['wikipedia'])
        if wiki_url:
            return wiki_url
    if 'contact:website' in tags and is_url(tags['contact:website']):
        return tags['contact:website']
    if 'source:url' in tags and is_url(tags['source:url']):
        return tags['source:url']
    if 'source' in tags and is_url(tags['source']):
        return tags['source']
    if 'url' in tags and is_url(tags['url']):
        return tags['url']
    return None

def osm_tag_to_wikipedia_url(wiki_tag: str) -> Optional[str]:
    if ':' not in wiki_tag:
        return None
    language_code, page_name = wiki_tag.split(':', 1)
    page_name = page_name.replace(' ', '_')
    return f"https://{language_code}.wikipedia.org/wiki/{page_name}"

__URL_REGEX = re.compile(
        # http:// or https://
        r'^(https?://)'
        # Domain name
        r'(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})'
        # Optional port number
        r'(:[0-9]{1,5})?'
        # Optional path
        r'(/.*)?$',
        re.IGNORECASE)

def is_url(value: str) -> bool:
    return __URL_REGEX.match(value) is not None

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
                name=determine_name(tags),
                picture=determine_picture(tags),
                description=determine_description(tags),
                operational_status=determine_operational_status(tags),
                safe_water=determine_safe_water(tags),
                legal_water=determine_legal_water(tags),
                access_bottles=determine_access_bottles(tags),
                access_pets=determine_access_pets(tags),
                access_wheelchair=determine_access_wheelchair(tags),
                access=determine_access(tags),
                fee=determine_fee(tags),
                address=determine_address(tags),
                website=determine_website(tags),
                provider_id=f'{element_type}:{element_id}',
                provider_updated_at=datetime.fromisoformat(element["timestamp"]), # before python 3.11: replace('Z', '+00:00')
                provider_url=osm_url(element_type, element_id)
            )

            if include_osm:
                fountain.osm = FountainOpenStreetMapInfo.model_construct(
                    type=element_type,
                    id=element_id,
                    version=element["version"],
                    tags=tags
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
