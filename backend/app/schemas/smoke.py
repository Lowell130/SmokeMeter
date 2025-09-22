# app/schemas/smoke.py
from pydantic import BaseModel
from typing import Literal, Optional

class SmokeCreate(BaseModel):
    pack_id: Optional[str] = None  # ora opzionale
    type: Literal['smoked', 'wasted', 'gifted'] = 'smoked'
    brand: Optional[str] = None    # marca opzionale per le "loose smokes"

class SmokeUpdate(BaseModel):
    type: Optional[Literal['smoked', 'wasted', 'gifted']] = None
