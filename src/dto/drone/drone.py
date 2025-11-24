from pydantic import BaseModel

class Drone(BaseModel):
    id: str
    name: str