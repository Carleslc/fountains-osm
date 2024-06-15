from typing import List, Optional

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.models.fountain import FountainOpenStreetMap


class QueryResponse(BaseModel):
    query_url: Optional[str] = None
    query_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


class OpenStreetMapResponse(QueryResponse):
    provider_name: str = "OpenStreetMap"


class FountainsOpenStreetMapResponse(OpenStreetMapResponse):
    count: int
    fountains: List[FountainOpenStreetMap]
