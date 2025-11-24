import math
from dataclasses import dataclass

@dataclass
class Angle:
    def __init__(self, d):
        if d < 0.0 or d > 360.0:
            raise ValueError(f"angle must be in range [0,360], got {d}")
        if d%22.5 != 0:
            raise ValueError(f"angle must be a multiple of 22.5 got {d}")
        self._degrees = d

    def radians(self):
        return math.radians(self._degrees)