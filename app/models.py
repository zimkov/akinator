from pydantic import BaseModel
from typing import Optional

class Animal(BaseModel):
    id: int
    question: str
    yes: Optional[int] = None
    no: Optional[int] = None

