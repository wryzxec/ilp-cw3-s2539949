from dataclasses import dataclass
from typing import List

from src.dto.drone.drone import Drone
from src.dto.geo.lnglat import LngLat
from src.dto.drone.request import Request

@dataclass
class PathResult:
    path: List[LngLat]
    moves: int