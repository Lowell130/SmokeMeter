# schemas/pack.py
from pydantic import BaseModel, Field
from typing import Literal

class PackCreate(BaseModel):
    brand: str
    size: Literal[10,20]
    price: float

class PackUpdate(BaseModel):
    brand: str | None = None
    size: int | None = None
    price: float | None = None

class PackPublic(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    brand: str
    size: int
    price: float
    created_at: int