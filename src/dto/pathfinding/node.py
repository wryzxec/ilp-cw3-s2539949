from dataclasses import dataclass
from typing import Optional

from src.dto.geo.lnglat import LngLat

@dataclass
class Node:
    position: LngLat
    distanceTravelled: float
    distanceLeft: float
    parent: Optional["Node"]