from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: str
    email: EmailStr
    baseline_cigs_per_day: int | None = None
    price_per_pack: float | None = None


class UserUpdate(BaseModel):
    baseline_cigs_per_day: int | None = None
    price_per_pack: float | None = None