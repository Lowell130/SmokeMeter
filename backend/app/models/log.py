from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional, List


LogType = Literal["cigarette", "purchase", "craving", "goal_update"]


class Log(BaseModel):
    user_id: str
    type: LogType
    ts: datetime
    meta: dict | None = None