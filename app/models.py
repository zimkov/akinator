from pydantic import BaseModel


class Animal(BaseModel):
    id: int
    name: str
    species: str
    age: int
