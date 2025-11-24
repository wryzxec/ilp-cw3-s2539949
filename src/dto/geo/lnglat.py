from pydantic import BaseModel, field_validator

class LngLat(BaseModel):
    lng: float
    lat: float

    @field_validator("lng")
    @classmethod
    def validate_lng(cls, v: float) -> float:
        if v < -180.0 or v > 180.0:
            raise ValueError(f"lng must be in range [-180, 180], got {v}")
        return v

    @field_validator("lat")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if v < -90.0 or v > 90.0:
            raise ValueError(f"lat must be in range [-90, 90], got {v}")
        return v
