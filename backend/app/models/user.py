from typing import Optional
from pydantic import BaseModel, EmailStr


class UserInDB(BaseModel):
    id: str
    email: EmailStr
    password_hash: str
    baseline_cigs_per_day: int | None = None
    price_per_pack: float | None = None