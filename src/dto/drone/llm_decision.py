from typing import List
from pydantic import BaseModel

class LLMDecision(BaseModel):
    priority: int
    items: List[str]