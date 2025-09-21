from pydantic import BaseModel, Field
from typing import Literal, Optional

class SmokeCreate(BaseModel):
    pack_id: str
    type: Literal['smoked','wasted','gifted'] = 'smoked'  # default

class SmokeUpdate(BaseModel):
    type: Optional[Literal['smoked','wasted','gifted']] = None
