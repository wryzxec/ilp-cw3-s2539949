from pydantic import BaseModel

from src.dto.geo.lnglat import LngLat

class Request(BaseModel):
    id: str
    position: LngLat
    content: str=""