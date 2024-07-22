from typing import Optional

from pydantic import BaseModel

class Provider(BaseModel):
    name: str
    url: Optional[str] = None
