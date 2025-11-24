from pydantic import BaseModel
from dataclasses import dataclass

from src.dto.geo.lnglat import LngLat

@dataclass
class ServicePoint(BaseModel):
    id: int
    name: str
    location: LngLat