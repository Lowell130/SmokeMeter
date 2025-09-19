from pydantic import BaseModel
from typing import List


class MetricSummary(BaseModel):
    range: str
    total_cigs: int
    total_spend: float
    daily_series: list[int]


class HourlyHist(BaseModel):
    range: str
    hist: list[int]  # 24 bucket