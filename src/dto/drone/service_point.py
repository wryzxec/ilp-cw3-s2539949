from dataclasses import dataclass

from src.dto.geo.lnglat import LngLat

@dataclass
class ServicePoint:
    id: str
    name: str
    position: LngLat